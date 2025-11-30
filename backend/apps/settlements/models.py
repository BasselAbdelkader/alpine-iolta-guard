from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone


class Settlement(models.Model):
    SETTLEMENT_STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('IN_PROGRESS', 'In Progress'),
        ('COMPLETED', 'Completed'),
        ('CANCELLED', 'Cancelled'),
    ]

    settlement_number = models.CharField(max_length=100, unique=True, null=True, blank=True)
    settlement_date = models.DateField(default=timezone.now)
    client = models.ForeignKey('clients.Client', on_delete=models.PROTECT)
    case = models.ForeignKey('clients.Case', on_delete=models.PROTECT, null=True, blank=True)
    bank_account = models.ForeignKey('bank_accounts.BankAccount', on_delete=models.PROTECT)
    total_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)
    status = models.CharField(max_length=20, choices=SETTLEMENT_STATUS_CHOICES, default='PENDING')
    notes = models.TextField(null=True, blank=True)
    created_by = models.CharField(max_length=100, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'settlements'
        ordering = ['-settlement_date', '-created_at']

    def __str__(self):
        return f"Settlement {self.settlement_number} - {self.client.full_name}"

    def save(self, *args, **kwargs):
        if not self.settlement_number:
            # Auto-generate settlement number
            from datetime import datetime
            year = datetime.now().year
            last_settlement = Settlement.objects.filter(
                settlement_number__startswith=f'SET-{year}'
            ).order_by('-id').first()
            
            if last_settlement:
                try:
                    last_num = int(last_settlement.settlement_number.split('-')[2])
                    self.settlement_number = f"SET-{year}-{last_num + 1:03d}"
                except (ValueError, IndexError):
                    self.settlement_number = f"SET-{year}-001"
            else:
                self.settlement_number = f"SET-{year}-001"
        
        super().save(*args, **kwargs)

    @property
    def is_balanced(self):
        """Check if settlement is balanced (total distributions = total amount)"""
        total_distributions = self.distributions.aggregate(
            total=models.Sum('amount')
        )['total'] or 0
        return total_distributions == self.total_amount

    @property
    def remaining_balance(self):
        """Calculate remaining balance to be distributed"""
        total_distributions = self.distributions.aggregate(
            total=models.Sum('amount')
        )['total'] or 0
        return self.total_amount - total_distributions


class SettlementDistribution(models.Model):
    DISTRIBUTION_TYPE_CHOICES = [
        ('VENDOR_PAYMENT', 'Vendor Payment'),
        ('CLIENT_REFUND', 'Client Refund'),
        ('ATTORNEY_FEES', 'Attorney Fees'),
        ('COURT_COSTS', 'Court Costs'),
        ('MEDICAL_EXPENSES', 'Medical Expenses'),
        ('OTHER', 'Other'),
    ]

    settlement = models.ForeignKey(Settlement, on_delete=models.CASCADE, related_name='distributions')
    vendor = models.ForeignKey('vendors.Vendor', on_delete=models.PROTECT, null=True, blank=True)
    client = models.ForeignKey('clients.Client', on_delete=models.PROTECT, null=True, blank=True)
    distribution_type = models.CharField(max_length=20, choices=DISTRIBUTION_TYPE_CHOICES)
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    description = models.TextField(null=True, blank=True)
    reference_number = models.CharField(max_length=50, null=True, blank=True)
    is_paid = models.BooleanField(default=False)
    paid_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'settlement_distributions'
        ordering = ['settlement', 'distribution_type']

    def __str__(self):
        recipient = self.vendor.vendor_name if self.vendor else self.client.full_name
        return f"{self.distribution_type} - {recipient} - ${self.amount}"

    def clean(self):
        if self.amount <= 0:
            raise ValidationError("Distribution amount must be positive")
        
        if not self.vendor and not self.client:
            raise ValidationError("Distribution must have either a vendor or client recipient")
        
        if self.vendor and self.client:
            raise ValidationError("Distribution cannot have both vendor and client recipients")

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)


class SettlementReconciliation(models.Model):
    RECONCILIATION_STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('BALANCED', 'Balanced'),
        ('UNBALANCED', 'Unbalanced'),
        ('RESOLVED', 'Resolved'),
    ]

    settlement = models.OneToOneField(Settlement, on_delete=models.CASCADE, related_name='reconciliation')
    bank_balance_before = models.DecimalField(max_digits=15, decimal_places=2)
    bank_balance_after = models.DecimalField(max_digits=15, decimal_places=2)
    client_balance_before = models.DecimalField(max_digits=15, decimal_places=2)
    client_balance_after = models.DecimalField(max_digits=15, decimal_places=2)
    total_distributions = models.DecimalField(max_digits=15, decimal_places=2)
    reconciliation_status = models.CharField(max_length=20, choices=RECONCILIATION_STATUS_CHOICES, default='PENDING')
    reconciled_by = models.CharField(max_length=100, null=True, blank=True)
    reconciled_at = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'settlement_reconciliations'
        ordering = ['-reconciled_at', '-created_at']

    def __str__(self):
        return f"Reconciliation for {self.settlement.settlement_number}"

    @property
    def balance_difference(self):
        """Calculate the difference between expected and actual balance changes"""
        expected_bank_change = self.bank_balance_before - self.total_distributions
        actual_bank_change = self.bank_balance_after
        return expected_bank_change - actual_bank_change

    @property
    def is_balanced(self):
        """Check if the 3-way reconciliation is balanced"""
        return abs(self.balance_difference) < 0.01  # Allow for small rounding differences

    def perform_reconciliation(self):
        """Perform the 3-way reconciliation check"""
        if self.is_balanced:
            self.reconciliation_status = 'BALANCED'
        else:
            self.reconciliation_status = 'UNBALANCED'
        
        self.reconciled_at = timezone.now()
        self.save()