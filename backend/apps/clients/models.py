from django.db import models
from django.core.validators import RegexValidator
from django.contrib.auth.models import User  # SECURITY FIX C2: For assigned_users relationship

# Name validator - only letters, numbers, spaces, hyphens, apostrophes, periods, commas
name_validator = RegexValidator(
    regex=r"^[a-zA-Z0-9\s\-'.,&]+$",
    message="Name can only contain letters, numbers, spaces, hyphens, apostrophes, periods, commas, and ampersands. No other special characters allowed."
)

# US States choices - Two letter codes
US_STATE_CHOICES = [
    ('', 'Select State'),
    ('AL', 'AL'), ('AK', 'AK'), ('AZ', 'AZ'), ('AR', 'AR'),
    ('CA', 'CA'), ('CO', 'CO'), ('CT', 'CT'), ('DE', 'DE'),
    ('FL', 'FL'), ('GA', 'GA'), ('HI', 'HI'), ('ID', 'ID'),
    ('IL', 'IL'), ('IN', 'IN'), ('IA', 'IA'), ('KS', 'KS'),
    ('KY', 'KY'), ('LA', 'LA'), ('ME', 'ME'), ('MD', 'MD'),
    ('MA', 'MA'), ('MI', 'MI'), ('MN', 'MN'), ('MS', 'MS'),
    ('MO', 'MO'), ('MT', 'MT'), ('NE', 'NE'), ('NV', 'NV'),
    ('NH', 'NH'), ('NJ', 'NJ'), ('NM', 'NM'), ('NY', 'NY'),
    ('NC', 'NC'), ('ND', 'ND'), ('OH', 'OH'), ('OK', 'OK'),
    ('OR', 'OR'), ('PA', 'PA'), ('RI', 'RI'), ('SC', 'SC'),
    ('SD', 'SD'), ('TN', 'TN'), ('TX', 'TX'), ('UT', 'UT'),
    ('VT', 'VT'), ('VA', 'VA'), ('WA', 'WA'), ('WV', 'WV'),
    ('WI', 'WI'), ('WY', 'WY'), ('DC', 'DC')
]

class Client(models.Model):
    # Client = Person/Entity who won the case and has money held in trust
    # Keep it simple - no unnecessary categorization
    
    TRUST_ACCOUNT_STATUS_CHOICES = [
        ('ACTIVE_WITH_FUNDS', 'Active with Funds'),
        ('ACTIVE_ZERO_BALANCE', 'Active - Zero Balance'),
        ('DORMANT', 'Dormant (No Activity 2+ Years)'),
        ('NEGATIVE_BALANCE', 'Negative Balance'),
        ('CLOSED', 'Closed/Inactive'),
    ]
    
    client_number = models.CharField(max_length=50, unique=True, null=True, blank=True)
    client_name = models.CharField(max_length=200, validators=[name_validator])  # Full client name - no special chars
    email = models.EmailField(null=True, blank=True)
    phone = models.CharField(
        max_length=20, 
        null=True, 
        blank=True,
        validators=[RegexValidator(regex=r'^(\+?1[-.\s]?)?\(?[0-9]{3}\)?[-.\s]?[0-9]{3}[-.\s]?[0-9]{4}$', message="Phone number must be entered in US format: (123) 456-7890, 123-456-7890, or +1234567890")]
    )
    address = models.TextField(null=True, blank=True)
    city = models.CharField(max_length=100, null=True, blank=True)
    state = models.CharField(max_length=2, choices=US_STATE_CHOICES, null=True, blank=True)
    zip_code = models.CharField(max_length=20, null=True, blank=True)
    # No client_type field - clients are simply persons/entities with money in trust
# current_balance field removed - now calculated dynamically via get_current_balance()
    trust_account_status = models.CharField(max_length=30, choices=TRUST_ACCOUNT_STATUS_CHOICES, default='ACTIVE_ZERO_BALANCE')
    is_active = models.BooleanField(default=True)

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

    # SECURITY FIX C2: IDOR Protection - Role-Based Access Control
    # Many-to-many relationship for user assignments (staff attorneys, paralegals)
    assigned_users = models.ManyToManyField(
        User,
        related_name='assigned_clients',
        blank=True,
        help_text='Users (staff attorneys, paralegals) who can access this client'
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'clients'
        ordering = ['client_name']  # Order by full name
        constraints = [
            models.UniqueConstraint(
                fields=['client_name'],
                name='unique_client_name'
            )
        ]

    def __str__(self):
        return self.client_name

    @property
    def full_name(self):
        """Backwards compatibility - returns client_name"""
        return self.client_name
    
    def get_current_balance(self):
        """Calculate current balance dynamically from consolidated bank_transactions table"""
        from ..bank_accounts.models import BankTransaction
        from django.db.models import Sum

        # Get deposits for this client (non-voided)
        deposits = BankTransaction.objects.filter(
            client_id=self.id,
            transaction_type='DEPOSIT'
        ).exclude(
            status='voided'
        ).aggregate(total=Sum('amount'))['total'] or 0

        # Get withdrawals for this client (non-voided)
        withdrawals = BankTransaction.objects.filter(
            client_id=self.id,
            transaction_type__in=['WITHDRAWAL', 'TRANSFER_OUT']
        ).exclude(
            status='voided'
        ).aggregate(total=Sum('amount'))['total'] or 0

        return deposits - withdrawals
    
    def get_formatted_balance(self):
        """Return balance in professional accounting format (parentheses for negatives)"""
        balance = self.get_current_balance()
        if balance < 0:
            return f"({abs(balance):,.2f})"  # Professional accounting standard
        return f"{balance:,.2f}"
    
    def get_balance_status_class(self):
        """Return CSS class for balance status (professional accounting color coding)"""
        balance = self.get_current_balance()
        if balance < 0:
            return 'text-danger fw-bold'  # RED + BOLD for negative balances (critical alert)
        elif balance == 0:
            return 'text-muted'           # Gray for zero balances
        else:
            return 'text-success'         # Green for positive balances

    def get_last_transaction_date(self):
        """Get the date of the most recent transaction for this client"""
        from ..bank_accounts.models import BankTransaction

        last_transaction = BankTransaction.objects.filter(
            client=self
        ).exclude(
            status='voided'
        ).order_by('-transaction_date').first()

        return last_transaction.transaction_date if last_transaction else None

    def calculate_trust_account_status(self):
        """Calculate the appropriate trust account status based on balance and activity"""
        from datetime import date, timedelta
        
        current_balance = self.get_current_balance()
        last_activity = self.get_last_transaction_date()
        
        # Negative balance - highest priority
        if current_balance < 0:
            return 'NEGATIVE_BALANCE'
        
        # Active with funds
        elif current_balance > 0:
            return 'ACTIVE_WITH_FUNDS'
        
        # Zero balance - check activity
        elif current_balance == 0:
            if last_activity:
                two_years_ago = date.today() - timedelta(days=730)
                
                # If last activity is within 2 years
                if last_activity >= two_years_ago:
                    return 'ACTIVE_ZERO_BALANCE'
                else:
                    return 'DORMANT'
            else:
                # No transaction history
                return 'ACTIVE_ZERO_BALANCE'
        
        return 'ACTIVE_ZERO_BALANCE'  # Default fallback

    def get_calculated_trust_account_status_display(self):
        """Get display text for the calculated trust account status"""
        status = self.calculate_trust_account_status()
        status_choices = dict(self.TRUST_ACCOUNT_STATUS_CHOICES)
        return status_choices.get(status, status)

    def update_trust_account_status(self):
        """Update the trust_account_status field with calculated value"""
        calculated_status = self.calculate_trust_account_status()
        if self.trust_account_status != calculated_status:
            self.trust_account_status = calculated_status
            return True  # Status changed
        return False  # No change

    def save(self, *args, **kwargs):
        if not self.client_number:
            # Auto-generate client number with atomic operation
            from django.db import transaction
            with transaction.atomic():
                # Lock the table to prevent race conditions
                last_client = Client.objects.select_for_update().order_by('-id').first()
                if last_client and last_client.client_number:
                    try:
                        last_num = int(last_client.client_number.split('-')[1])
                        self.client_number = f"CL-{last_num + 1:03d}"
                    except (ValueError, IndexError):
                        # Fallback to count if parsing fails
                        count = Client.objects.select_for_update().count()
                        self.client_number = f"CL-{count + 1:03d}"
                else:
                    self.client_number = "CL-001"
        super().save(*args, **kwargs)


class Case(models.Model):
    CASE_STATUS_CHOICES = [
        ('Open', 'Open'),
        ('Pending Settlement', 'Pending Settlement'),
        ('Settled', 'Settled'),
        ('Closed', 'Closed'),
    ]

    case_number = models.CharField(max_length=100, unique=True, editable=False)  # Auto-generated, hidden from users
    case_title = models.CharField(max_length=255, verbose_name="Case Title")  # User-facing field
    client = models.ForeignKey(Client, on_delete=models.PROTECT, related_name='cases')
    case_description = models.TextField(null=True, blank=True)
    case_amount = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True, default=None)
    case_status = models.CharField(max_length=50, choices=CASE_STATUS_CHOICES, default='Open')
    opened_date = models.DateField(null=True, blank=True)
    closed_date = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

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

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'cases'
        ordering = ['-opened_date', 'case_number']

    def __str__(self):
        return f"{self.case_title} - {self.client.full_name}"
    
    def get_current_balance(self):
        """Calculate current balance dynamically from consolidated bank_transactions table for this case"""
        from ..bank_accounts.models import BankTransaction
        from django.db.models import Sum

        # Get deposits for this case (non-voided)
        deposits = BankTransaction.objects.filter(
            case=self,
            transaction_type='DEPOSIT'
        ).exclude(
            status='voided'
        ).aggregate(total=Sum('amount'))['total'] or 0

        # Get withdrawals for this case (non-voided)
        withdrawals = BankTransaction.objects.filter(
            case=self,
            transaction_type__in=['WITHDRAWAL', 'TRANSFER_OUT']
        ).exclude(
            status='voided'
        ).aggregate(total=Sum('amount'))['total'] or 0

        return deposits - withdrawals
    
    def get_formatted_balance(self):
        """Return balance in professional accounting format (parentheses for negatives)"""
        balance = self.get_current_balance()
        if balance < 0:
            return f"({abs(balance):,.2f})"  # Professional accounting standard
        return f"{balance:,.2f}"
    
    def get_balance_status_class(self):
        """Return CSS class for balance status (professional accounting color coding)"""
        balance = self.get_current_balance()
        if balance < 0:
            return 'text-danger fw-bold'  # RED + BOLD for negative balances (critical alert)
        elif balance == 0:
            return 'text-muted'           # Gray for zero balances
        else:
            return 'text-success'         # Green for positive balances

    def save(self, *args, **kwargs):
        """Override save to handle auto-incremental case_number and create automatic deposit"""
        from django.db import transaction

        is_new = self.pk is None
        old_case_amount = None

        # Wrap entire save operation in atomic transaction to ensure data consistency
        with transaction.atomic():
            # Auto-generate case_number for new cases
            if is_new and not self.case_number:
                self.case_number = self._generate_case_number()

            # Track case amount changes for existing cases
            if not is_new:
                try:
                    old_case = Case.objects.get(pk=self.pk)
                    old_case_amount = old_case.case_amount
                except Case.DoesNotExist:
                    old_case_amount = 0

            super().save(*args, **kwargs)

            # Create automatic deposit transaction for new cases with amount > 0
            if is_new and self.case_amount and self.case_amount > 0:
                self._create_case_deposit()
            # Update deposit for existing cases if amount changed
            elif not is_new and old_case_amount != self.case_amount and self.case_amount and self.case_amount > 0:
                self._update_case_deposit(old_case_amount)
    
    def _generate_case_number(self):
        """Generate auto-incremental case number atomically - never reuse deleted numbers"""
        from django.db import transaction, connection

        # Use atomic transaction to prevent race conditions
        with transaction.atomic():
            # Query the database with proper parameterization to prevent SQL injection
            with connection.cursor() as cursor:
                # Use parameterized query to prevent SQL injection
                cursor.execute("""
                    SELECT case_number
                    FROM cases
                    WHERE case_number LIKE %s
                    ORDER BY CAST(SUBSTRING(case_number FROM 6) AS INTEGER) DESC
                    LIMIT 1
                    FOR UPDATE
                """, ['CASE-%'])  # Parameterized to prevent SQL injection
                row = cursor.fetchone()

                if row and row[0]:
                    try:
                        # Extract the numeric part (CASE-000001 -> 000001 -> 1)
                        numeric_part = row[0].split('-')[1]
                        highest_num = int(numeric_part)
                    except (ValueError, IndexError):
                        highest_num = 0
                else:
                    highest_num = 0

            # Generate next number (start from 1 if no existing CASE- numbers)
            next_num = highest_num + 1
            return f"CASE-{next_num:06d}"  # 6-digit zero-padded
    
    def _create_case_deposit(self):
        """Create automatic deposit transaction for this case"""
        from ..bank_accounts.models import BankAccount, BankTransaction
        from datetime import datetime

        # Get the first bank account (trust account)
        bank_account = BankAccount.objects.first()
        if not bank_account:
            return  # No bank account available

        # Generate transaction number
        current_year = datetime.now().year
        last_transaction = BankTransaction.objects.filter(
            transaction_number__startswith=f'TXN-{current_year}'
        ).order_by('-id').first()
        
        if last_transaction:
            try:
                last_num = int(last_transaction.transaction_number.split('-')[2])
                transaction_number = f"TXN-{current_year}-{last_num + 1:03d}"
            except (ValueError, IndexError):
                transaction_number = f"TXN-{current_year}-001"
        else:
            transaction_number = f"TXN-{current_year}-001"
        
        # BUG #15 FIX: Create the consolidated deposit transaction with payee set to client name
        transaction = BankTransaction.objects.create(
            transaction_number=transaction_number,
            bank_account=bank_account,
            transaction_type='DEPOSIT',
            transaction_date=self.created_at.date(),
            amount=self.case_amount,
            description=f'Automatic deposit for case {self.case_number}: {self.case_description or "N/A"}',
            reference_number=f'{self.case_number}',
            payee=self.client.full_name,  # BUG #15 FIX: Set payee to client name
            client=self.client,
            case=self,
            item_type='CLIENT_DEPOSIT',
            status='pending'  # New deposits start as uncleared
        )
        
        return transaction
    
    def _update_case_deposit(self, old_amount):
        """Update existing case deposit when case amount changes"""
        from ..bank_accounts.models import BankTransaction
        from decimal import Decimal

        # Convert to Decimal for accurate comparison
        old_amount = Decimal(str(old_amount)) if old_amount else Decimal('0')
        new_amount = Decimal(str(self.case_amount)) if self.case_amount else Decimal('0')

        # Find ALL existing case deposits (there might be multiple from updates)
        existing_transactions = BankTransaction.objects.filter(
            case=self,
            item_type='CLIENT_DEPOSIT',
            transaction_type='DEPOSIT'
        ).exclude(status='voided').order_by('-created_at')

        if existing_transactions.exists():
            # Get the most recent non-voided deposit
            latest_transaction = existing_transactions.first()

            # Calculate the difference
            amount_difference = new_amount - old_amount

            if amount_difference != 0:
                # Update the most recent transaction
                latest_transaction.amount = new_amount
                latest_transaction.description = f'Updated deposit for case {self.case_number}: {self.case_description or "N/A"} (Changed from ${old_amount:,.2f} to ${new_amount:,.2f})'
                latest_transaction.save()

                # Void any older duplicate deposits to prevent double-counting
                for old_deposit in existing_transactions[1:]:
                    if old_deposit.status != 'voided':
                        old_deposit.status = 'voided'
                        old_deposit.void_reason = f'Superseded by updated deposit transaction'
                        old_deposit.save()
        else:
            # No existing deposit found, create new one
            if new_amount > 0:
                self._create_case_deposit()