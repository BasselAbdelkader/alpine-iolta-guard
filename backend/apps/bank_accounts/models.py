from django.db import models


class BankAccount(models.Model):
    ACCOUNT_TYPE_CHOICES = [
        ('Trust Account', 'Trust Account'),
        ('Operating Account', 'Operating Account'),
        ('Escrow Account', 'Escrow Account'),
    ]

    account_number = models.CharField(max_length=50, unique=True)
    bank_name = models.CharField(max_length=200)
    bank_address = models.TextField(null=True, blank=True)
    account_name = models.CharField(max_length=200)
    routing_number = models.CharField(max_length=20, null=True, blank=True)
    account_type = models.CharField(max_length=50, choices=ACCOUNT_TYPE_CHOICES, default='Trust Account')
    opening_balance = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)
    # current_balance field removed - now calculated dynamically via get_current_balance()
    next_check_number = models.IntegerField(default=1001, help_text="Next sequential check number for IOLTA compliance")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'bank_accounts'
        ordering = ['bank_name', 'account_name']

    def __str__(self):
        return f"{self.bank_name} - {self.account_name}"
    
    def get_current_balance(self):
        """
        Calculate Trust Account Balance (ALL non-voided transactions: pending + cleared)
        This is the single source of truth for the account balance.
        Should ALWAYS equal the sum of all client balances.
        """
        # Get all non-voided transactions for this bank account in chronological order
        transactions = self.bank_transactions.exclude(
            status='voided'
        ).order_by('transaction_date', 'id')

        # Calculate running balance starting from opening balance
        running_balance = self.opening_balance

        for transaction in transactions:
            if transaction.transaction_type == 'DEPOSIT':
                running_balance += transaction.amount
            else:  # WITHDRAWAL or TRANSFER
                running_balance -= transaction.amount

        return running_balance

    def get_trust_balance(self):
        """
        Alias for get_current_balance() for clarity.
        Trust Balance = ALL non-voided transactions (pending + cleared)
        This should ALWAYS equal the sum of all client balances.
        """
        return self.get_current_balance()

    def get_register_balance(self):
        """
        Alias for get_current_balance() for clarity.
        Register Balance = ALL non-voided transactions (pending + cleared)
        This is the single source of truth for the account balance.
        Should ALWAYS equal: Trust Balance = Register Balance = Sum of Client Balances
        """
        return self.get_current_balance()

    def get_pending_transactions_count(self):
        """Get count of pending (uncleared) transactions"""
        return self.bank_transactions.filter(
            status='pending'
        ).exclude(
            status='voided'
        ).count()

    def verify_client_balance_match(self):
        """
        Verify that trust balance matches sum of client balances.
        Returns: dict with match status, balances, and difference
        """
        from apps.clients.models import Client

        trust_balance = self.get_current_balance()
        total_client_balance = sum(client.get_current_balance() for client in Client.objects.all())
        difference = abs(trust_balance - total_client_balance)
        matches = difference < 0.01  # Allow for rounding

        return {
            'matches': matches,
            'trust_balance': trust_balance,
            'client_balance_sum': total_client_balance,
            'difference': difference,
            'status': 'VERIFIED' if matches else 'MISMATCH',
            'status_class': 'success' if matches else 'danger'
        }
    
    def create_opening_balance_transaction(self):
        """Create opening balance transaction for new bank account using consolidated table"""
        # DISABLED: Opening balance is always $0.00
        # No opening balance transaction should be created
        return None
    
    def get_next_check_number(self):
        """
        Get and increment next check number atomically for IOLTA compliance.
        Ensures sequential, non-duplicate check numbers.
        """
        from django.db import transaction
        with transaction.atomic():
            # Lock the row to prevent race conditions
            account = BankAccount.objects.select_for_update().get(pk=self.pk)
            check_num = account.next_check_number
            account.next_check_number += 1
            account.save(update_fields=['next_check_number', 'updated_at'])
            return str(check_num)

    def save(self, *args, **kwargs):
        """Override save to create opening balance transaction and prevent edits after creation"""
        is_new = self.pk is None

        # Allow updates to next_check_number field (for IOLTA compliance)
        update_fields = kwargs.get('update_fields')
        if not is_new and update_fields and set(update_fields) <= {'next_check_number', 'updated_at'}:
            # Allow updating only next_check_number and updated_at
            super().save(*args, **kwargs)
            return

        if not is_new:
            # Prevent any other modifications to existing bank account
            raise ValueError("Bank account cannot be modified after creation. Please contact administrator to delete and recreate if changes are needed.")

        super().save(*args, **kwargs)

        # Create opening balance transaction for new accounts only
        if is_new:
            self.create_opening_balance_transaction()


class BankTransaction(models.Model):
    """
    Consolidated bank transactions table containing all transaction data
    Replaces the previous 3-table structure (transactions + transaction_items + bank_transactions)
    """
    TRANSACTION_TYPE_CHOICES = [
        ('DEPOSIT', 'Deposit'),
        ('WITHDRAWAL', 'Withdrawal'),
    ]

    ITEM_TYPE_CHOICES = [
        ('CLIENT_DEPOSIT', 'Client Deposit'),
        ('VENDOR_PAYMENT', 'Vendor Payment'),
        ('CASE_SETTLEMENT', 'Case Settlement'),
        ('BANK_FEE', 'Bank Fee'),
        ('INTEREST', 'Interest'),
        ('OTHER', 'Other'),
    ]

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('cleared', 'Cleared'),
        ('voided', 'Voided'),
        ('reconciled', 'Reconciled'),  # REQUIREMENT: Add Reconciled status
    ]

    # Core transaction fields
    transaction_number = models.CharField(max_length=100, unique=True, null=True, blank=True)
    bank_account = models.ForeignKey(BankAccount, on_delete=models.PROTECT, related_name='bank_transactions')
    transaction_date = models.DateField()
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPE_CHOICES)
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    description = models.TextField(blank=True)

    # Transaction detail fields (from transaction_items)
    client = models.ForeignKey('clients.Client', on_delete=models.PROTECT, null=True, blank=True, related_name='bank_transactions')
    case = models.ForeignKey('clients.Case', on_delete=models.PROTECT, null=True, blank=True, related_name='bank_transactions')
    vendor = models.ForeignKey('vendors.Vendor', on_delete=models.PROTECT, null=True, blank=True, related_name='bank_transactions')
    check_memo = models.CharField(max_length=500, blank=True)

    # REQUIREMENT: Check# and Reference are ONE field
    # reference_number is the primary field used for all transaction references
    # For withdrawals that are checks, this contains the check number
    # For deposits, this can contain any reference (receipt number, etc.)
    reference_number = models.CharField(max_length=100, blank=True, help_text="Transaction reference (check number for withdrawals, receipt for deposits)")

    # DEPRECATED: check_number field kept for backwards compatibility
    # Use reference_number instead. This will be removed in future version.
    check_number = models.CharField(max_length=50, blank=True, help_text="DEPRECATED: Use reference_number instead")

    payee = models.CharField(max_length=255, blank=True)
    item_type = models.CharField(max_length=20, choices=ITEM_TYPE_CHOICES, blank=True)

    # Status and control fields (is_cleared and is_voided removed - using status field instead)
    cleared_date = models.DateField(null=True, blank=True)
    check_is_printed = models.BooleanField(default=False)
    # Voiding fields - when voiding a transaction, set status='voided' and fill these fields
    voided_date = models.DateTimeField(null=True, blank=True)
    voided_by = models.CharField(max_length=100, blank=True)
    void_reason = models.TextField(blank=True)

    # Bank reconciliation fields (existing)
    post_date = models.DateField(null=True, blank=True)
    bank_reference = models.CharField(max_length=100, blank=True)
    bank_category = models.CharField(max_length=100, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    reconciliation_notes = models.TextField(blank=True)
    rec_id = models.IntegerField(null=True, blank=True)

    # Data source tracking for import auditing
    data_source = models.CharField(
        max_length=20,
        choices=[
            ('webapp', 'Web Application'),
            ('csv_import', 'CSV Import'),
            ('api_import', 'API Import'),
        ],
        default='webapp',
        help_text='Source of data entry'
    )
    import_batch_id = models.IntegerField(null=True, blank=True, help_text='Links to ImportAudit record')

    # Audit fields
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.CharField(max_length=100, blank=True)

    # Migration tracking fields (temporary)
    original_transaction_id = models.IntegerField(null=True, blank=True)
    original_item_id = models.IntegerField(null=True, blank=True)

    class Meta:
        db_table = 'bank_transactions'
        ordering = ['-transaction_date', '-created_at']
        indexes = [
            models.Index(fields=['bank_account', 'transaction_date']),
            models.Index(fields=['client_id']),
            models.Index(fields=['case_id']),
            models.Index(fields=['vendor_id']),
            models.Index(fields=['transaction_date', 'transaction_type']),
            models.Index(fields=['transaction_number']),
            models.Index(fields=['status', 'transaction_date']),
            models.Index(fields=['status']),
            models.Index(fields=['check_number']),
            models.Index(fields=['reference_number']),
        ]

    def __str__(self):
        if self.transaction_number:
            return f"{self.transaction_number} - {self.transaction_date} - ${self.amount}"
        return f"{self.bank_account.account_name} - {self.transaction_date} - {self.get_transaction_type_display()} - ${self.amount}"

    def save(self, *args, **kwargs):
        # === AUDIT LOGGING SETUP ===
        # Extract audit parameters (if provided by calling code)
        audit_user = kwargs.pop('audit_user', None)
        audit_reason = kwargs.pop('audit_reason', '')
        audit_ip = kwargs.pop('audit_ip', None)

        # Determine if this is a new record or update
        is_new = self.pk is None
        old_instance = None

        # If updating, get the old values before save
        if not is_new:
            try:
                old_instance = BankTransaction.objects.get(pk=self.pk)
            except BankTransaction.DoesNotExist:
                old_instance = None

        # Auto-generate transaction number if not provided and this is a new transaction
        if not self.transaction_number and not self.pk:
            from datetime import datetime
            current_year = datetime.now().year
            prefix = self.transaction_type[:4].upper()

            # Find the highest existing transaction number for this year and type
            max_number = 0
            existing_transactions = BankTransaction.objects.filter(
                transaction_number__startswith=f'{prefix}-{current_year}'
            ).values_list('transaction_number', flat=True)

            for transaction_number in existing_transactions:
                try:
                    num = int(transaction_number.split('-')[2])
                    if num > max_number:
                        max_number = num
                except (ValueError, IndexError):
                    continue

            # Generate unique transaction number by incrementing from max
            next_number = max_number + 1
            max_attempts = 1000  # Prevent infinite loop
            attempts = 0

            while attempts < max_attempts:
                potential_number = f"{prefix}-{current_year}-{next_number:03d}"

                # Check if this number already exists
                if not BankTransaction.objects.filter(transaction_number=potential_number).exists():
                    self.transaction_number = potential_number
                    break

                next_number += 1
                attempts += 1

            # Fallback if we couldn't find a unique number
            if not self.transaction_number:
                from django.utils import timezone
                timestamp = timezone.now().strftime('%Y%m%d%H%M%S%f')[:17]  # Include microseconds
                self.transaction_number = f"{prefix}-{current_year}-{timestamp}"

        # IOLTA Compliance: Auto-assign sequential check number for withdrawals
        # When a withdrawal is created, auto-assign check number ONLY if reference is NOT "TO PRINT" or blank
        # If reference is "TO PRINT" or blank, check number will be assigned when actually printing
        if (not self.pk and  # New transaction only
            self.transaction_type == 'WITHDRAWAL' and
            not self.check_number and
            self.status != 'voided' and
            self.reference_number and  # Has a reference
            self.reference_number != 'TO PRINT'):  # And it's not "TO PRINT"
            self.check_number = self.bank_account.get_next_check_number()
            # Mark as NOT printed (ready to print) - user should not control this via checkbox
            self.check_is_printed = False

        # Auto-generate bank reference if not provided and this is a new transaction
        if not self.bank_reference and not self.pk:
            from datetime import datetime
            timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
            self.bank_reference = f"BANK-{timestamp}-{self.pk or 'NEW'}"

        # REQUIREMENT: Sync check_number and reference_number (they should be one field)
        # For backwards compatibility, keep both fields in sync
        # Skip sync if both are intentionally blank (reissue case)
        if self.transaction_type == 'WITHDRAWAL':
            # Skip sync if both are explicitly blank (reissue voiding case)
            if not (self.reference_number == '' and self.check_number == ''):
                # For withdrawals, check_number should match reference_number
                if self.check_number and not self.reference_number:
                    self.reference_number = self.check_number
                elif self.reference_number and not self.check_number:
                    self.check_number = self.reference_number
                # If both exist and differ, reference_number takes precedence
                elif self.reference_number and self.check_number != self.reference_number:
                    self.check_number = self.reference_number

        # REQUIREMENT: Voided transaction handling
        # When transaction is voided, if reference is "TO PRINT", change it to "Voided"
        # UNLESS it's being explicitly set to blank (for reissue logic)
        if self.status == 'voided' and old_instance and old_instance.status != 'voided':
            # Transaction is being voided now
            if old_instance.reference_number == 'TO PRINT':
                # Original was TO PRINT
                if self.reference_number == '':
                    # Being set to blank - leave it blank (reissue case)
                    self.check_number = ''
                else:
                    # Not being set to blank - change to Voided (normal void)
                    self.reference_number = 'Voided'
                    self.check_number = 'Voided'
            # Set voided date if not already set
            if not self.voided_date:
                from django.utils import timezone
                self.voided_date = timezone.now()

        # ROOT CAUSE FIX: Auto-link vendor by matching payee name to vendor_name
        # This ensures vendor FK is set even when creating transactions directly (not via API/serializer)
        if self.payee and not self.vendor:
            from apps.vendors.models import Vendor
            # Try to find vendor by exact name match (case-insensitive)
            vendor = Vendor.objects.filter(vendor_name__iexact=self.payee.strip()).first()
            if vendor:
                self.vendor = vendor

        # Call parent save
        super().save(*args, **kwargs)

        # === AUDIT LOGGING ===
        # Create audit log after successful save
        try:
            self._create_audit_log(is_new, old_instance, audit_user, audit_reason, audit_ip)
        except Exception as e:
            # Log the error but don't fail the transaction save
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Audit logging failed for transaction {self.pk}: {str(e)}")

    @property
    def is_debit(self):
        """Returns True if this transaction decreases the account balance"""
        return self.transaction_type == 'WITHDRAWAL'

    @property
    def is_credit(self):
        """Returns True if this transaction increases the account balance"""
        return self.transaction_type == 'DEPOSIT'

    def get_signed_amount(self):
        """Returns amount with appropriate sign based on transaction type"""
        if self.is_debit:
            return -self.amount
        return self.amount

    def void_transaction(self, void_reason, voided_by=None, ip_address=None):
        """Void this transaction with reason and audit trail"""
        if self.status == 'voided':
            raise ValueError("Transaction is already voided")

        if self.status == 'cleared':
            raise ValueError("Cannot void cleared transaction")

        from django.utils import timezone
        self.status = 'voided'
        self.voided_date = timezone.now()
        self.voided_by = voided_by or 'system'
        self.void_reason = void_reason
        # Set amount to zero when voiding (voided transactions have no financial impact)
        self.amount = 0
        # Pass audit parameters to save method
        self.save(
            audit_user=voided_by or 'system',
            audit_reason=void_reason,
            audit_ip=ip_address
        )

    def _get_snapshot(self):
        """Get JSON snapshot of current transaction values for audit logging"""
        return {
            'transaction_number': self.transaction_number,
            'transaction_date': str(self.transaction_date),
            'transaction_type': self.transaction_type,
            'amount': str(self.amount),
            'status': self.status,
            'payee': self.payee,
            'description': self.description,
            'check_number': self.check_number,
            'reference_number': self.reference_number,
            'client_id': self.client_id,
            'case_id': self.case_id,
            'vendor_id': self.vendor_id,
            'check_memo': self.check_memo,
            'cleared_date': str(self.cleared_date) if self.cleared_date else None,
            'voided_date': str(self.voided_date) if self.voided_date else None,
            'voided_by': self.voided_by,
            'void_reason': self.void_reason,
        }

    def _create_audit_log(self, is_new, old_instance, audit_user, audit_reason, audit_ip):
        """Create audit log entry for this transaction change"""
        # Determine action type
        if is_new:
            action = 'CREATED'
            old_values = None
            old_amount = None
            old_status = None
        else:
            # Detect specific actions based on status changes
            if old_instance:
                if old_instance.status != 'voided' and self.status == 'voided':
                    action = 'VOIDED'
                elif old_instance.status == 'voided' and self.status != 'voided':
                    action = 'UNVOIDED'
                elif old_instance.status != 'cleared' and self.status == 'cleared':
                    action = 'CLEARED'
                else:
                    action = 'UPDATED'

                old_values = old_instance._get_snapshot()
                old_amount = old_instance.amount
                old_status = old_instance.status

                # Check if anything actually changed
                new_snapshot = self._get_snapshot()
                if old_values == new_snapshot and action == 'UPDATED':
                    # Nothing changed, don't create audit log
                    return
            else:
                action = 'UPDATED'
                old_values = None
                old_amount = None
                old_status = None

        # Get current values
        new_values = self._get_snapshot()
        # If transaction is voided, new amount should be 0.00 (transaction has no financial impact)
        new_amount = 0 if self.status == 'voided' else self.amount
        new_status = self.status

        # Determine user (from audit_user parameter, or try to get from Django's thread local)
        user = audit_user or 'system'

        # Create the audit log
        BankTransactionAudit.objects.create(
            transaction=self,
            action=action,
            action_by=user,
            old_values=old_values,
            new_values=new_values,
            old_amount=old_amount,
            new_amount=new_amount,
            old_status=old_status,
            new_status=new_status,
            change_reason=audit_reason,
            ip_address=audit_ip or '127.0.0.1'  # Default to localhost if not provided
        )


class BankReconciliation(models.Model):
    bank_account = models.ForeignKey(BankAccount, on_delete=models.CASCADE)
    reconciliation_date = models.DateField()
    statement_balance = models.DecimalField(max_digits=15, decimal_places=2)
    book_balance = models.DecimalField(max_digits=15, decimal_places=2)
    is_reconciled = models.BooleanField(default=False)
    reconciled_by = models.CharField(max_length=100, null=True, blank=True)
    reconciled_at = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'bank_reconciliations'
        ordering = ['-reconciliation_date']

    def __str__(self):
        return f"{self.bank_account.account_name} - {self.reconciliation_date}"

    @property
    def difference(self):
        return self.statement_balance - self.book_balance


class BankTransactionAudit(models.Model):
    """
    Audit trail for ALL changes to bank transactions.
    Records every create, update, clear, void action with complete before/after snapshots.

    Key Features:
    - Automatic logging on transaction save()
    - Tracks who, when, what changed
    - Stores JSON snapshots for complete history
    - Special handling for voided transactions
    - IP address tracking for security
    """

    AUDIT_ACTION_CHOICES = [
        ('CREATED', 'Created'),
        ('UPDATED', 'Updated'),
        ('CLEARED', 'Cleared'),
        ('VOIDED', 'Voided'),
        ('UNVOIDED', 'Unvoided'),
        ('DELETED', 'Deleted'),
    ]

    # Link to transaction (CASCADE so audit logs deleted if transaction deleted)
    transaction = models.ForeignKey(
        BankTransaction,
        on_delete=models.CASCADE,
        related_name='audit_logs',
        help_text="Transaction this audit log belongs to"
    )

    # Audit metadata
    action = models.CharField(
        max_length=20,
        choices=AUDIT_ACTION_CHOICES,
        help_text="Type of action performed"
    )
    action_date = models.DateTimeField(
        auto_now_add=True,
        help_text="When this action occurred"
    )
    action_by = models.CharField(
        max_length=100,
        help_text="Username of person who made the change"
    )

    # Complete snapshots (JSON)
    old_values = models.JSONField(
        null=True,
        blank=True,
        help_text="Complete snapshot of values BEFORE change"
    )
    new_values = models.JSONField(
        null=True,
        blank=True,
        help_text="Complete snapshot of values AFTER change"
    )

    # Key fields for quick queries (denormalized for performance)
    old_amount = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Amount before change"
    )
    new_amount = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Amount after change"
    )
    old_status = models.CharField(
        max_length=20,
        null=True,
        blank=True,
        help_text="Status before change (pending/cleared/voided)"
    )
    new_status = models.CharField(
        max_length=20,
        null=True,
        blank=True,
        help_text="Status after change (pending/cleared/voided)"
    )

    # Change details
    change_reason = models.TextField(
        blank=True,
        help_text="Reason for the change (required for voids)"
    )

    # Security/audit tracking
    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True,
        help_text="IP address of user who made the change"
    )

    class Meta:
        db_table = 'bank_transaction_audit'
        ordering = ['-action_date']
        indexes = [
            models.Index(fields=['transaction', '-action_date'], name='audit_trans_date_idx'),
            models.Index(fields=['action'], name='audit_action_idx'),
            models.Index(fields=['action_by'], name='audit_user_idx'),
            models.Index(fields=['action_date'], name='audit_date_idx'),
        ]
        verbose_name = 'Bank Transaction Audit Log'
        verbose_name_plural = 'Bank Transaction Audit Logs'

    def __str__(self):
        transaction_ref = getattr(self.transaction, 'reference_number', 'Unknown')
        return f"{transaction_ref} - {self.action} by {self.action_by} at {self.action_date.strftime('%Y-%m-%d %H:%M')}"

    def get_changes_summary(self):
        """
        Generate human-readable summary of what changed.
        Returns a string describing all changes made.
        """
        changes = []

        # Amount change
        if self.old_amount is not None and self.new_amount is not None:
            if self.old_amount != self.new_amount:
                changes.append(f"Amount: ${self.old_amount:,.2f} → ${self.new_amount:,.2f}")
        elif self.new_amount is not None:
            changes.append(f"Amount: ${self.new_amount:,.2f} (initial)")

        # Status change
        if self.old_status and self.new_status:
            if self.old_status != self.new_status:
                changes.append(f"Status: {self.old_status} → {self.new_status}")
        elif self.new_status:
            changes.append(f"Status: {self.new_status} (initial)")

        # Check JSON for other changes
        if self.old_values and self.new_values:
            # Check payee change
            old_payee = self.old_values.get('payee')
            new_payee = self.new_values.get('payee')
            if old_payee != new_payee:
                changes.append(f"Payee: {old_payee or 'None'} → {new_payee or 'None'}")

            # Check description change
            old_desc = self.old_values.get('description')
            new_desc = self.new_values.get('description')
            if old_desc != new_desc:
                old_preview = (old_desc[:30] + '...') if old_desc and len(old_desc) > 30 else (old_desc or 'None')
                new_preview = (new_desc[:30] + '...') if new_desc and len(new_desc) > 30 else (new_desc or 'None')
                changes.append(f"Description changed: {old_preview} → {new_preview}")

        return " | ".join(changes) if changes else "No significant changes detected"

    def get_action_badge_class(self):
        """Return Bootstrap badge class for this action"""
        badge_classes = {
            'CREATED': 'bg-primary',
            'UPDATED': 'bg-info',
            'CLEARED': 'bg-success',
            'VOIDED': 'bg-danger',
            'UNVOIDED': 'bg-warning text-dark',
            'DELETED': 'bg-dark',
        }
        return badge_classes.get(self.action, 'bg-secondary')