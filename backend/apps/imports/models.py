"""
Import Staging and Approval System Models
==========================================
Two-stage import system: Import → Staging → Approval → Production

Business Rules:
- All imports go to staging tables first
- Managing Attorney or Accountant must approve
- Cannot approve own import (dual control)
- Staging data kept forever until manually rejected
"""

from django.db import models
from django.contrib.auth.models import User
from django.core.validators import RegexValidator


# Reuse state choices from clients app
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


class StagingClient(models.Model):
    """
    Staging table for imported clients
    Mirrors clients table structure + staging metadata
    """
    # Staging metadata
    staging_id = models.AutoField(primary_key=True)
    import_batch_id = models.IntegerField(help_text='Links to import_logs.id')

    # Client fields (mirror production Client model)
    client_number = models.CharField(max_length=50, null=True, blank=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(null=True, blank=True)
    phone = models.CharField(
        max_length=20,
        null=True,
        blank=True,
        validators=[RegexValidator(
            regex=r'^(\+?1[-.\s]?)?\(?[0-9]{3}\)?[-.\s]?[0-9]{3}[-.\s]?[0-9]{4}$',
            message="Phone number must be in US format"
        )]
    )
    address = models.TextField(null=True, blank=True)
    city = models.CharField(max_length=100, null=True, blank=True)
    state = models.CharField(max_length=2, choices=US_STATE_CHOICES, null=True, blank=True)
    zip_code = models.CharField(max_length=20, null=True, blank=True)
    trust_account_status = models.CharField(max_length=30, default='ACTIVE_ZERO_BALANCE')
    is_active = models.BooleanField(default=True)
    data_source = models.CharField(
        max_length=20,
        choices=[
            ('webapp', 'Web Application'),
            ('csv_import', 'CSV Import'),
            ('api_import', 'API Import'),
        ],
        default='csv_import'
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'staging_clients'
        ordering = ['staging_id']
        indexes = [
            models.Index(fields=['import_batch_id']),
            models.Index(fields=['client_number']),
        ]

    def __str__(self):
        return f"Staging Client {self.staging_id}: {self.first_name} {self.last_name}"


class StagingCase(models.Model):
    """
    Staging table for imported cases
    Mirrors cases table structure + staging metadata
    """
    # Staging metadata
    staging_id = models.AutoField(primary_key=True)
    import_batch_id = models.IntegerField(help_text='Links to import_logs.id')

    # Links to staging client (NOT production client)
    staging_client = models.ForeignKey(
        StagingClient,
        on_delete=models.CASCADE,
        related_name='staging_cases',
        help_text='Links to staging_clients table'
    )

    # Case fields (mirror production Case model)
    case_number = models.CharField(max_length=100, null=True, blank=True)
    case_title = models.CharField(max_length=255)
    case_description = models.TextField(null=True, blank=True)
    case_status = models.CharField(
        max_length=20,
        choices=[
            ('Open', 'Open'),
            ('Closed', 'Closed'),
            ('Pending', 'Pending'),
        ],
        default='Open'
    )
    opened_date = models.DateField(null=True, blank=True)
    closed_date = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    data_source = models.CharField(
        max_length=20,
        choices=[
            ('webapp', 'Web Application'),
            ('csv_import', 'CSV Import'),
            ('api_import', 'API Import'),
        ],
        default='csv_import'
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'staging_cases'
        ordering = ['staging_id']
        indexes = [
            models.Index(fields=['import_batch_id']),
            models.Index(fields=['case_number']),
        ]

    def __str__(self):
        return f"Staging Case {self.staging_id}: {self.case_title}"


class StagingBankTransaction(models.Model):
    """
    Staging table for imported bank transactions
    Mirrors bank_transactions table structure + staging metadata
    """
    # Staging metadata
    staging_id = models.AutoField(primary_key=True)
    import_batch_id = models.IntegerField(help_text='Links to import_logs.id')

    # Links to staging records (NOT production records)
    staging_client = models.ForeignKey(
        StagingClient,
        on_delete=models.CASCADE,
        related_name='staging_transactions',
        help_text='Links to staging_clients table'
    )
    staging_case = models.ForeignKey(
        StagingCase,
        on_delete=models.CASCADE,
        related_name='staging_transactions',
        help_text='Links to staging_cases table'
    )

    # Transaction fields (mirror production BankTransaction model)
    # Note: bank_account will be set during approval (use default bank account)
    transaction_date = models.DateField()
    transaction_type = models.CharField(
        max_length=20,
        choices=[
            ('DEPOSIT', 'Deposit'),
            ('WITHDRAWAL', 'Withdrawal'),
            ('TRANSFER_IN', 'Transfer In'),
            ('TRANSFER_OUT', 'Transfer Out'),
        ]
    )
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    payee = models.CharField(max_length=200, null=True, blank=True)
    reference_number = models.CharField(max_length=50, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    status = models.CharField(
        max_length=20,
        choices=[
            ('Pending', 'Pending'),
            ('Cleared', 'Cleared'),
            ('Void', 'Void'),
        ],
        default='Pending'
    )
    data_source = models.CharField(
        max_length=20,
        choices=[
            ('webapp', 'Web Application'),
            ('csv_import', 'CSV Import'),
            ('api_import', 'API Import'),
        ],
        default='csv_import'
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'staging_bank_transactions'
        ordering = ['transaction_date', 'staging_id']
        indexes = [
            models.Index(fields=['import_batch_id']),
            models.Index(fields=['transaction_date']),
        ]

    def __str__(self):
        return f"Staging Transaction {self.staging_id}: {self.transaction_type} ${self.amount}"


class ImportNotification(models.Model):
    """
    In-app notifications for import workflow
    TODO: Add email notifications later
    """
    NOTIFICATION_TYPES = [
        ('import_pending', 'Import Pending Approval'),
        ('import_approved', 'Import Approved'),
        ('import_rejected', 'Import Rejected'),
    ]

    notification_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='import_notifications')
    notification_type = models.CharField(max_length=50, choices=NOTIFICATION_TYPES)
    import_batch_id = models.IntegerField(help_text='Links to import_logs.id')
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='sent_notifications',
        help_text='User who triggered this notification'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    read_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'import_notifications'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'is_read']),
            models.Index(fields=['import_batch_id']),
        ]

    def __str__(self):
        return f"Notification {self.notification_id}: {self.notification_type} for {self.user.username}"

    def mark_as_read(self):
        """Mark notification as read"""
        from django.utils import timezone
        self.is_read = True
        self.read_at = timezone.now()
        self.save()
