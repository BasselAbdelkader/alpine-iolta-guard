from django import forms
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from .models import Client, Case, US_STATE_CHOICES
from trust_account_project.forms import SecureModelForm, CSRFProtectedMixin


class ClientForm(SecureModelForm):
    class Meta:
        model = Client
        fields = [
            'client_name', 'email', 'phone', 'address', 'city', 'state', 'zip_code', 'is_active'
        ]
        widgets = {
            'client_name': forms.TextInput(attrs={
                'class': 'form-control'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-control'
            }),
            'address': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3
            }),
            'city': forms.TextInput(attrs={
                'class': 'form-control'
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
        self.fields['client_name'].required = True
        self.fields['is_active'].initial = True

        # Replace state field completely to be a dropdown
        self.fields['state'] = forms.ChoiceField(
            choices=US_STATE_CHOICES,
            required=False,
            widget=forms.Select(attrs={
                'class': 'form-select'
            })
        )

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
                raise ValidationError('Please enter a valid email address')

            # Split email into local and domain parts
            try:
                local, domain = email.rsplit('@', 1)
            except ValueError:
                raise ValidationError('Please enter a valid email address')

            # Check domain has at least one dot and valid TLD
            if '.' not in domain:
                raise ValidationError('Email domain must include a valid extension (e.g., .com, .org)')

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
                raise ValidationError(f'Invalid email domain extension ".{tld}". Please use a valid extension like .com, .org, .net, etc.')

        return email

    def clean_zip_code(self):
        """Validate zip code is exactly 5 digits"""
        zip_code = self.cleaned_data.get('zip_code')

        if not zip_code:
            return zip_code

        # Remove any whitespace
        zip_code = zip_code.strip()

        if zip_code:
            # Check if it's exactly 5 digits
            if not zip_code.isdigit() or len(zip_code) != 5:
                raise ValidationError('Zip code must be exactly 5 digits (e.g., 12345)')

        return zip_code

    def clean(self):
        """Validate that client_name is unique"""
        cleaned_data = super().clean()
        client_name = cleaned_data.get('client_name')

        if client_name:
            # Check for existing client with same name, excluding current instance if editing
            existing_clients = Client.objects.filter(
                client_name__iexact=client_name.strip()
            )

            # If editing an existing client, exclude it from the check
            if self.instance and self.instance.pk:
                existing_clients = existing_clients.exclude(pk=self.instance.pk)

            if existing_clients.exists():
                existing_client = existing_clients.first()
                raise ValidationError({
                    'client_name': f'A client named "{client_name}" already exists in the system. '
                                 f'Client names must be unique in trust account systems. '
                                 f'(Existing client ID: {existing_client.id})'
                })

        return cleaned_data


class CaseForm(SecureModelForm):
    class Meta:
        model = Case
        fields = [
            'case_title', 'client', 'case_description', 'case_status', 'case_amount', 'opened_date', 'closed_date', 'is_active'
        ]
        widgets = {
            'case_title': forms.TextInput(attrs={
                'class': 'form-control',
                'required': True
            }),
            'client': forms.Select(attrs={
                'class': 'form-select'
            }),
            'case_description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4
            }),
            'case_status': forms.Select(attrs={
                'class': 'form-select'
            }),
            'case_amount': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0'
            }),
            'opened_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'closed_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            })
        }
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['case_title'].required = True
        self.fields['client'].queryset = Client.objects.filter(is_active=True).order_by('client_name')
        self.fields['client'].required = True
        self.fields['case_status'].required = True

        # Set default values
        if not self.instance.pk:  # Only for new cases
            self.fields['case_status'].initial = 'Open'
            self.fields['is_active'].initial = True
