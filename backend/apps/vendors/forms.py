from django import forms
from django.core.validators import RegexValidator
from .models import Vendor, VendorType
from ..clients.models import Client
import re

# US States choices - Two letter codes
US_STATES = [
    ('', 'Select State'),
    ('AL', 'AL'), ('AK', 'AK'), ('AZ', 'AZ'), ('AR', 'AR'), ('CA', 'CA'),
    ('CO', 'CO'), ('CT', 'CT'), ('DE', 'DE'), ('FL', 'FL'), ('GA', 'GA'),
    ('HI', 'HI'), ('ID', 'ID'), ('IL', 'IL'), ('IN', 'IN'), ('IA', 'IA'),
    ('KS', 'KS'), ('KY', 'KY'), ('LA', 'LA'), ('ME', 'ME'), ('MD', 'MD'),
    ('MA', 'MA'), ('MI', 'MI'), ('MN', 'MN'), ('MS', 'MS'), ('MO', 'MO'),
    ('MT', 'MT'), ('NE', 'NE'), ('NV', 'NV'), ('NH', 'NH'), ('NJ', 'NJ'),
    ('NM', 'NM'), ('NY', 'NY'), ('NC', 'NC'), ('ND', 'ND'), ('OH', 'OH'),
    ('OK', 'OK'), ('OR', 'OR'), ('PA', 'PA'), ('RI', 'RI'), ('SC', 'SC'),
    ('SD', 'SD'), ('TN', 'TN'), ('TX', 'TX'), ('UT', 'UT'), ('VT', 'VT'),
    ('VA', 'VA'), ('WA', 'WA'), ('WV', 'WV'), ('WI', 'WI'), ('WY', 'WY')
]

class VendorForm(forms.ModelForm):
    state = forms.ChoiceField(
        choices=US_STATES,
        required=False,
        initial='',
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    class Meta:
        model = Vendor
        fields = [
            'vendor_name', 'contact_person', 'email', 'phone',
            'address', 'city', 'state', 'zip_code', 'is_active'
        ]
        widgets = {
            'vendor_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter vendor name'
            }),
            'contact_person': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter contact person name'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-control'
            }),
            'address': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Enter street address'
            }),
            'city': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter city'
            }),
            'zip_code': forms.TextInput(attrs={
                'class': 'form-control',
                'maxlength': '5'
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            })
        }
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Only vendor_name is required
        self.fields['vendor_name'].required = True
        self.fields['contact_person'].required = False
        self.fields['email'].required = False
        self.fields['phone'].required = False
        self.fields['address'].required = False
        self.fields['city'].required = False
        self.fields['state'].required = False
        self.fields['zip_code'].required = False
        self.fields['is_active'].initial = True

        # Add is-invalid class to fields with errors
        if self.errors:
            for field_name, errors in self.errors.items():
                if field_name in self.fields:
                    current_classes = self.fields[field_name].widget.attrs.get('class', '')
                    self.fields[field_name].widget.attrs['class'] = f'{current_classes} is-invalid'.strip()

    def clean_email(self):
        """Validate email format"""
        email = self.cleaned_data.get('email')

        if not email:
            return email

        email = email.strip()

        if email:
            # Basic email validation - must have @ and proper domain
            if '@' not in email:
                raise forms.ValidationError('Please enter a valid email address')

            # Split email into local and domain parts
            try:
                local, domain = email.rsplit('@', 1)
            except ValueError:
                raise forms.ValidationError('Please enter a valid email address')

            # Check domain has at least one dot and valid TLD
            if '.' not in domain:
                raise forms.ValidationError('Email domain must include a valid extension (e.g., .com, .org)')

            # Get the TLD (last part after final dot)
            domain_parts = domain.split('.')
            tld = domain_parts[-1].lower()

            # List of valid TLDs (common ones)
            valid_tlds = [
                'com', 'org', 'net', 'edu', 'gov', 'mil', 'int',
                'co', 'io', 'ai', 'app', 'dev', 'info', 'biz',
                'us', 'uk', 'ca', 'au', 'de', 'fr', 'jp', 'cn',
                'law', 'legal', 'attorney', 'lawyer'
            ]

            if tld not in valid_tlds:
                raise forms.ValidationError(f'Invalid email domain extension ".{tld}". Please use a valid extension like .com, .org, .net, etc.')

        return email

    def clean_zip_code(self):
        """Validate ZIP code format - exactly 5 digits only"""
        zip_code = self.cleaned_data.get('zip_code')

        if not zip_code:
            return zip_code

        zip_code = zip_code.strip()

        if zip_code:
            # Only accept exactly 5 digits
            if not zip_code.isdigit() or len(zip_code) != 5:
                raise forms.ValidationError('Zip code must be exactly 5 digits (e.g., 12345)')

        return zip_code

