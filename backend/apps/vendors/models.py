from django.db import models
from django.core.validators import RegexValidator

# Name validator - only letters, numbers, spaces, hyphens, apostrophes, periods, commas
name_validator = RegexValidator(
    regex=r"^[a-zA-Z0-9\s\-'.,&]+$",
    message="Name can only contain letters, numbers, spaces, hyphens, apostrophes, periods, commas, and ampersands. No other special characters allowed."
)

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


class VendorType(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(null=True, blank=True)
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

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'vendor_types'
        ordering = ['name']

    def __str__(self):
        return self.name


class Vendor(models.Model):
    vendor_number = models.CharField(max_length=50, unique=True, null=True, blank=True)
    vendor_name = models.CharField(max_length=200, validators=[name_validator])  # No special chars
    vendor_type = models.ForeignKey(VendorType, on_delete=models.PROTECT, null=True, blank=True)
    contact_person = models.CharField(max_length=200, null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    phone = models.CharField(
        max_length=20,
        null=True,
        blank=True,
        validators=[RegexValidator(regex=r'^(\+?1[-.\s]?)?\(?[0-9]{3}\)?[-.\s]?[0-9]{3}[-.\s]?[0-9]{4}$', message="Phone number must be entered in US format: (555) 123-4567, 555-123-4567, or +15551234567")]
    )
    address = models.TextField(null=True, blank=True)
    city = models.CharField(max_length=100, null=True, blank=True)
    state = models.CharField(max_length=2, choices=US_STATES, null=True, blank=True, help_text="Two-letter state code")
    zip_code = models.CharField(max_length=20, null=True, blank=True)
    tax_id = models.CharField(max_length=50, null=True, blank=True)
    client = models.ForeignKey('clients.Client', on_delete=models.CASCADE, null=True, blank=True, help_text="If vendor is also a client")
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
        db_table = 'vendors'
        ordering = ['vendor_name']

    def __str__(self):
        return self.vendor_name

    def save(self, *args, **kwargs):
        if not self.vendor_number:
            # Auto-generate vendor number
            if self.client:
                # Client-vendor - check if client already has a vendor
                existing_vendor = Vendor.objects.filter(client=self.client).first()
                if existing_vendor:
                    # Use existing vendor number pattern but make it unique
                    base_number = f"CV-{self.client.id:03d}"
                    counter = 1
                    self.vendor_number = f"{base_number}-{counter}"
                    while Vendor.objects.filter(vendor_number=self.vendor_number).exists():
                        counter += 1
                        self.vendor_number = f"{base_number}-{counter}"
                else:
                    self.vendor_number = f"CV-{self.client.id:03d}"
            else:
                # Regular vendor
                last_vendor = Vendor.objects.filter(vendor_number__startswith='VEN-').order_by('-id').first()
                if last_vendor and last_vendor.vendor_number:
                    try:
                        last_num = int(last_vendor.vendor_number.split('-')[1])
                        self.vendor_number = f"VEN-{last_num + 1:03d}"
                    except (ValueError, IndexError):
                        self.vendor_number = f"VEN-{Vendor.objects.filter(client__isnull=True).count() + 1:03d}"
                else:
                    self.vendor_number = "VEN-001"
        super().save(*args, **kwargs)