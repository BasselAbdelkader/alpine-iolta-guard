from django.db import models
from django.core.validators import RegexValidator
from django.db import transaction
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


# US State choices - 2-letter codes only
US_STATES = [
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


class LawFirm(models.Model):
    """Law firm information for trust account compliance and reporting"""
    firm_name = models.CharField(max_length=200, help_text="Full legal name of the law firm")
    doing_business_as = models.CharField(max_length=200, blank=True, help_text="DBA name if different")

    # Contact Information
    address_line1 = models.CharField(max_length=100)
    address_line2 = models.CharField(max_length=100, blank=True)
    city = models.CharField(max_length=50)
    state = models.CharField(max_length=2, choices=US_STATES, help_text="Two-letter state code")
    zip_code = models.CharField(max_length=10)
    phone = models.CharField(max_length=20)
    fax = models.CharField(max_length=20, blank=True)
    email = models.EmailField()
    website = models.URLField(blank=True)
    
    # Principal Attorney Information
    principal_attorney = models.CharField(max_length=100, help_text="Managing partner or principal attorney")
    attorney_bar_number = models.CharField(
        max_length=20,
        help_text="State bar registration number",
        validators=[RegexValidator(
            regex=r'^[A-Z0-9\-]+$',
            message='Bar number must contain only letters, numbers, and hyphens'
        )]
    )
    attorney_state = models.CharField(max_length=2, choices=US_STATES, help_text="State of bar admission")
    
    # Trust Account Compliance
    trust_account_required = models.BooleanField(default=True)
    iolta_compliant = models.BooleanField(
        default=False, 
        help_text="Interest on Lawyer Trust Account compliance"
    )
    approval_threshold = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=10000.00, 
        help_text="Transaction amount requiring two-person approval"
    )
    trust_account_certification_date = models.DateField(
        null=True, 
        blank=True,
        help_text="Date of last trust account certification"
    )
    
    # Business Information
    tax_id = models.CharField(
        max_length=20, 
        blank=True,
        help_text="Federal Tax ID (EIN)"
    )
    state_registration = models.CharField(
        max_length=50, 
        blank=True,
        help_text="State business registration number"
    )
    
    # System Fields
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'law_firm'
        verbose_name = 'Law Firm'
        verbose_name_plural = 'Law Firm Information'

    def __str__(self):
        return self.firm_name
    
    @property
    def full_address(self):
        """Return formatted full address"""
        address = self.address_line1
        if self.address_line2:
            address += f"\n{self.address_line2}"
        address += f"\n{self.city}, {self.state} {self.zip_code}"
        return address
    
    @property
    def contact_info(self):
        """Return formatted contact information"""
        info = f"Phone: {self.phone}"
        if self.fax:
            info += f"\nFax: {self.fax}"
        info += f"\nEmail: {self.email}"
        if self.website:
            info += f"\nWebsite: {self.website}"
        return info
    
    def save(self, *args, **kwargs):
        # Ensure only one active law firm exists
        if self.is_active:
            LawFirm.objects.filter(is_active=True).exclude(pk=self.pk).update(is_active=False)
        super().save(*args, **kwargs)
    
    @classmethod
    def get_active_firm(cls):
        """Get the active law firm"""
        return cls.objects.filter(is_active=True).first()


class Setting(models.Model):
    category = models.CharField(max_length=50)
    key = models.CharField(max_length=100)
    value = models.CharField(max_length=255)
    display_order = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'settings'
        ordering = ['category', 'display_order', 'key']
        unique_together = ['category', 'key']

    def __str__(self):
        return f"{self.category}.{self.key} = {self.value}"

    @classmethod
    def get_choices_for_category(cls, category):
        """Get choices list for a specific category for use in forms"""
        return cls.objects.filter(category=category, is_active=True).values_list('key', 'value')

    @classmethod
    def get_value(cls, category, key, default=None):
        """Get a specific setting value"""
        try:
            return cls.objects.get(category=category, key=key, is_active=True).value
        except cls.DoesNotExist:
            return default

class CheckSequence(models.Model):
    """Tracks the next available check number for sequential assignment"""
    bank_account = models.OneToOneField(
        'bank_accounts.BankAccount',
        on_delete=models.CASCADE,
        related_name='check_sequence',
        help_text="Bank account for this check sequence"
    )
    next_check_number = models.IntegerField(
        default=1001,
        help_text="Next check number to assign"
    )
    last_assigned_number = models.IntegerField(
        null=True,
        blank=True,
        help_text="Last check number that was assigned"
    )
    last_assigned_date = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When the last check number was assigned"
    )
    
    class Meta:
        db_table = 'check_sequences'
        verbose_name = 'Check Sequence'
        verbose_name_plural = 'Check Sequences'
    
    def __str__(self):
        return f"{self.bank_account.account_name} - Next: {self.next_check_number}"
    
    @classmethod
    def get_next_numbers(cls, bank_account, count):
        """
        Get the next 'count' check numbers for a bank account.
        Returns a list of check numbers and updates the sequence.
        Thread-safe using database transaction.

        IMPORTANT: Always syncs with BankAccount.next_check_number as the authoritative source.
        """
        with transaction.atomic():
            # Get or create sequence for this bank account
            sequence, created = cls.objects.select_for_update().get_or_create(
                bank_account=bank_account,
                defaults={'next_check_number': bank_account.next_check_number or 1001}
            )

            # BUGFIX: Sync with BankAccount.next_check_number (authoritative source)
            # If user edited the Next Check # via UI, BankAccount.next_check_number will be updated
            # We need to use that value, not the CheckSequence value
            bank_account.refresh_from_db()
            if bank_account.next_check_number and bank_account.next_check_number > sequence.next_check_number:
                # User manually updated the check number via UI - use their value
                start_number = bank_account.next_check_number
            else:
                # Use the sequence value
                start_number = sequence.next_check_number

            # Generate check numbers
            reference_numbers = list(range(start_number, start_number + count))

            # Update BOTH sequence and bank account
            from django.utils import timezone
            sequence.last_assigned_number = reference_numbers[-1]
            sequence.next_check_number = reference_numbers[-1] + 1
            sequence.last_assigned_date = timezone.now()
            sequence.save()

            # Update BankAccount.next_check_number to keep them in sync
            bank_account.next_check_number = reference_numbers[-1] + 1
            bank_account.save(update_fields=['next_check_number', 'updated_at'])

            return reference_numbers


class ImportAudit(models.Model):
    """Tracks data import batches for auditing and batch deletion"""

    IMPORT_TYPE_CHOICES = [
        ('csv', 'CSV Import'),
        ('api', 'API Import'),
    ]

    STATUS_CHOICES = [
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('partial', 'Partially Completed'),
    ]

    # Import metadata
    import_date = models.DateTimeField(auto_now_add=True)
    import_type = models.CharField(max_length=20, choices=IMPORT_TYPE_CHOICES)
    file_name = models.CharField(max_length=255, blank=True, help_text='Original filename for CSV imports')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='in_progress')

    # Import statistics
    total_records = models.IntegerField(default=0, help_text='Total records attempted')
    successful_records = models.IntegerField(default=0, help_text='Successfully imported')
    failed_records = models.IntegerField(default=0, help_text='Failed to import')

    # Breakdown by entity type (actual results)
    clients_created = models.IntegerField(default=0)
    cases_created = models.IntegerField(default=0)
    transactions_created = models.IntegerField(default=0)
    vendors_created = models.IntegerField(default=0)

    # Skipped/Duplicate counts (actual results)
    clients_skipped = models.IntegerField(default=0, help_text='Clients skipped (duplicates)')
    cases_skipped = models.IntegerField(default=0, help_text='Cases skipped (duplicates)')
    vendors_skipped = models.IntegerField(default=0, help_text='Vendors skipped (duplicates)')
    rows_with_errors = models.IntegerField(default=0, help_text='Rows with null/invalid data')

    # Preview/Expected counts (before import)
    expected_clients = models.IntegerField(default=0, help_text='Expected new clients from preview')
    expected_cases = models.IntegerField(default=0, help_text='Expected new cases from preview')
    expected_transactions = models.IntegerField(default=0, help_text='Expected new transactions from preview')
    expected_vendors = models.IntegerField(default=0, help_text='Expected new vendors from preview')

    # Total counts from CSV (including duplicates and nulls)
    total_clients_in_csv = models.IntegerField(default=0, help_text='Total client rows in CSV (including duplicates)')
    total_cases_in_csv = models.IntegerField(default=0, help_text='Total case rows in CSV (including duplicates)')
    total_transactions_in_csv = models.IntegerField(default=0, help_text='Total transaction rows in CSV')
    total_vendors_in_csv = models.IntegerField(default=0, help_text='Total vendor rows in CSV (including duplicates)')

    # Existing entity counts (from preview - already in system)
    existing_clients = models.IntegerField(default=0, help_text='Clients already in system')
    existing_cases = models.IntegerField(default=0, help_text='Cases already in system')
    existing_vendors = models.IntegerField(default=0, help_text='Vendors already in system')

    # Preview validation
    preview_data = models.TextField(blank=True, help_text='JSON data from preview validation')
    preview_errors = models.TextField(blank=True, help_text='Validation errors found during preview')

    # Error tracking
    error_log = models.TextField(blank=True, help_text='JSON or text log of errors')

    # User tracking
    imported_by = models.CharField(max_length=100, help_text='Username who performed import')

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True, help_text='When import finished')

    class Meta:
        db_table = 'import_audit'
        ordering = ['-import_date']
        verbose_name = 'Import Audit'
        verbose_name_plural = 'Import Audits'

    def __str__(self):
        return f"{self.get_import_type_display()} - {self.import_date.strftime('%Y-%m-%d %H:%M')} - {self.get_status_display()}"

    @property
    def success_rate(self):
        """Calculate success rate percentage"""
        if self.total_records == 0:
            return 0
        return round((self.successful_records / self.total_records) * 100, 2)

    def mark_completed(self):
        """Mark import as completed"""
        from django.utils import timezone
        self.status = 'completed'
        self.completed_at = timezone.now()
        self.save(update_fields=['status', 'completed_at'])

    def mark_failed(self, error_message=''):
        """Mark import as failed"""
        from django.utils import timezone
        self.status = 'failed'
        self.completed_at = timezone.now()
        if error_message:
            self.error_log = error_message
        self.save(update_fields=['status', 'completed_at', 'error_log'])

    def delete_imported_data(self):
        """
        Delete all data imported in this batch.
        Returns count of deleted records by type.
        """
        from apps.clients.models import Client, Case
        from apps.bank_accounts.models import BankTransaction
        from apps.vendors.models import Vendor

        deleted_counts = {
            'clients': 0,
            'cases': 0,
            'transactions': 0,
            'vendors': 0,
        }

        # Delete in reverse order of dependencies
        # 1. Transactions first (they depend on clients, cases, vendors)
        transactions = BankTransaction.objects.filter(import_batch_id=self.id)
        deleted_counts['transactions'] = transactions.count()
        transactions.delete()

        # 2. Cases (they depend on clients)
        cases = Case.objects.filter(import_batch_id=self.id)
        deleted_counts['cases'] = cases.count()
        cases.delete()

        # 3. Vendors (independent)
        vendors = Vendor.objects.filter(import_batch_id=self.id)
        deleted_counts['vendors'] = vendors.count()
        vendors.delete()

        # 4. Clients last
        clients = Client.objects.filter(import_batch_id=self.id)
        deleted_counts['clients'] = clients.count()
        clients.delete()

        return deleted_counts


class CaseNumberCounter(models.Model):
    """Tracks the last used case number for auto-increment - prevents reuse of deleted case numbers"""
    last_number = models.IntegerField(default=0, help_text='Last case number assigned (CASE-XXXXXX format)')

    class Meta:
        db_table = 'case_number_counter'
        verbose_name = 'Case Number Counter'
        verbose_name_plural = 'Case Number Counters'

    def __str__(self):
        return f"Last Case Number: CASE-{self.last_number:06d}"

    @classmethod
    def get_next_number(cls):
        """Get next case number and increment counter (thread-safe)"""
        with transaction.atomic():
            counter, created = cls.objects.select_for_update().get_or_create(
                id=1,  # Only one counter record
                defaults={'last_number': 0}
            )
            counter.last_number += 1
            counter.save()
            return counter.last_number


class ImportLog(models.Model):
    """Logs QuickBooks and other import operations for auditing"""

    IMPORT_TYPE_CHOICES = [
        ('quickbooks', 'QuickBooks Import'),
        ('csv', 'CSV Import'),
        ('excel', 'Excel Import'),
        ('api', 'API Import'),
    ]

    STATUS_CHOICES = [
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('partial', 'Partially Completed'),
    ]

    # Import metadata
    import_type = models.CharField(max_length=50, choices=IMPORT_TYPE_CHOICES)
    filename = models.CharField(max_length=255, null=True, blank=True, help_text='Original filename')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='in_progress')
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    # Import statistics
    total_rows = models.IntegerField(null=True, blank=True, help_text='Total rows in import file')
    clients_created = models.IntegerField(default=0, help_text='New clients created')
    clients_existing = models.IntegerField(default=0, help_text='Existing clients found')
    cases_created = models.IntegerField(default=0, help_text='New cases created')
    transactions_created = models.IntegerField(default=0, help_text='New transactions created')
    transactions_skipped = models.IntegerField(default=0, help_text='Transactions skipped (duplicates)')

    # Error and summary tracking
    errors = models.JSONField(null=True, blank=True, help_text='JSON array of error messages')
    summary = models.JSONField(null=True, blank=True, help_text='JSON summary of import results')

    # User tracking
    created_by = models.ForeignKey(
        'auth.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='import_logs',
        help_text='User who performed the import'
    )

    # Two-stage approval workflow fields
    approval_status = models.CharField(
        max_length=20,
        choices=[
            ('pending_review', 'Pending Review'),
            ('committed', 'Committed to Production'),
            ('rejected', 'Rejected'),
        ],
        default='pending_review',
        help_text='Approval status for two-stage import workflow'
    )
    reviewed_by = models.ForeignKey(
        'auth.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reviewed_imports',
        help_text='User who approved or rejected this import'
    )
    reviewed_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text='When import was reviewed (approved or rejected)'
    )
    review_notes = models.TextField(
        blank=True,
        help_text='Reason for approval or rejection'
    )

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'import_logs'
        ordering = ['-started_at']
        verbose_name = 'Import Log'
        verbose_name_plural = 'Import Logs'

    def __str__(self):
        return f"{self.get_import_type_display()} - {self.started_at.strftime('%Y-%m-%d %H:%M')} - {self.get_status_display()}"

    @property
    def total_created(self):
        """Total entities created in this import"""
        return self.clients_created + self.cases_created + self.transactions_created

    @property
    def duration(self):
        """Calculate import duration in seconds"""
        if self.completed_at and self.started_at:
            return (self.completed_at - self.started_at).total_seconds()
        return None

    def mark_completed(self):
        """Mark import as completed"""
        from django.utils import timezone
        self.status = 'completed'
        self.completed_at = timezone.now()
        self.save(update_fields=['status', 'completed_at', 'updated_at'])

    def mark_failed(self, error_message=''):
        """Mark import as failed"""
        from django.utils import timezone
        self.status = 'failed'
        self.completed_at = timezone.now()
        if error_message:
            if self.errors is None:
                self.errors = []
            self.errors.append(error_message)
        self.save(update_fields=['status', 'completed_at', 'errors', 'updated_at'])


class UserProfile(models.Model):
    """
    Extended user profile with role-based access control for IOLTA Guard.
    Implements 5 user roles as defined in Trust Account Compliance Audit.
    """

    ROLE_CHOICES = [
        ('managing_attorney', 'Managing Attorney'),
        ('staff_attorney', 'Staff Attorney'),
        ('paralegal', 'Paralegal'),
        ('bookkeeper', 'Bookkeeper'),
        ('system_admin', 'System Administrator'),
    ]

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='profile',
        help_text='Link to Django User account'
    )

    role = models.CharField(
        max_length=30,
        choices=ROLE_CHOICES,
        default='paralegal',
        help_text='User role determines permissions'
    )

    # Additional profile information
    phone = models.CharField(max_length=20, blank=True, help_text='Contact phone number')
    employee_id = models.CharField(max_length=50, blank=True, help_text='Employee ID or bar number')
    department = models.CharField(max_length=100, blank=True, help_text='Department or practice area')

    # Access control
    is_active = models.BooleanField(default=True, help_text='User can access the system')
    can_approve_transactions = models.BooleanField(
        default=False,
        help_text='Can approve high-value transactions (≥ $10,000)'
    )
    can_reconcile = models.BooleanField(
        default=False,
        help_text='Can perform bank reconciliation'
    )
    can_print_checks = models.BooleanField(
        default=False,
        help_text='Can print checks (requires dual approval)'
    )
    can_manage_users = models.BooleanField(
        default=False,
        help_text='Can create/edit user accounts'
    )

    # Audit fields
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_profiles',
        help_text='Admin who created this user'
    )

    class Meta:
        db_table = 'user_profiles'
        verbose_name = 'User Profile'
        verbose_name_plural = 'User Profiles'

    def __str__(self):
        return f"{self.user.get_full_name() or self.user.username} ({self.get_role_display()})"

    def save(self, *args, **kwargs):
        """Set default permissions based on role"""
        # Set default permissions when role changes
        if self.role == 'managing_attorney':
            self.can_approve_transactions = True
            self.can_reconcile = True
            self.can_print_checks = True
            self.can_manage_users = True
        elif self.role == 'staff_attorney':
            self.can_approve_transactions = False
            self.can_reconcile = False
            self.can_print_checks = False
            self.can_manage_users = False
        elif self.role == 'paralegal':
            self.can_approve_transactions = False
            self.can_reconcile = False
            self.can_print_checks = False
            self.can_manage_users = False
        elif self.role == 'bookkeeper':
            self.can_approve_transactions = False
            self.can_reconcile = True
            self.can_print_checks = True
            self.can_manage_users = False
        elif self.role == 'system_admin':
            self.can_approve_transactions = False
            self.can_reconcile = False
            self.can_print_checks = False
            self.can_manage_users = True

        super().save(*args, **kwargs)

    @property
    def role_description(self):
        """Get detailed description of role permissions"""
        descriptions = {
            'managing_attorney': 'Full access to all functions. Can approve high-value transactions, reconcile accounts, and manage users.',
            'staff_attorney': 'Create/edit own cases and clients. View assigned cases only. Cannot approve high-value transactions.',
            'paralegal': 'Limited data entry. Create/edit clients and cases. Enter transactions (require approval). No financial reports.',
            'bookkeeper': 'Financial operations. Enter transactions, reconcile accounts, generate reports. Cannot approve own transactions.',
            'system_admin': 'Technical access only. User management and system configuration. No access to client data or transactions.',
        }
        return descriptions.get(self.role, '')

    @property
    def permission_summary(self):
        """Get summary of current permissions"""
        permissions = []
        if self.can_approve_transactions:
            permissions.append('Approve Transactions')
        if self.can_reconcile:
            permissions.append('Bank Reconciliation')
        if self.can_print_checks:
            permissions.append('Print Checks')
        if self.can_manage_users:
            permissions.append('Manage Users')
        return ', '.join(permissions) if permissions else 'Basic Access'


@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    """Automatically create UserProfile when User is created"""
    if created:
        UserProfile.objects.create(user=instance)
