from django import forms
from .models import Settlement, SettlementDistribution, SettlementReconciliation
from apps.clients.models import Client, Case
from apps.vendors.models import Vendor
from apps.bank_accounts.models import BankAccount


class SettlementForm(forms.ModelForm):
    class Meta:
        model = Settlement
        fields = [
            'settlement_date', 'client', 'case', 'bank_account', 
            'total_amount', 'status', 'notes'
        ]
        widgets = {
            'settlement_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'client': forms.Select(attrs={
                'class': 'form-control'
            }),
            'case': forms.Select(attrs={
                'class': 'form-control'
            }),
            'bank_account': forms.Select(attrs={
                'class': 'form-control'
            }),
            'total_amount': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0',
                'placeholder': '0.00'
            }),
            'status': forms.Select(attrs={
                'class': 'form-control'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Enter settlement notes and details'
            })
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['client'].queryset = Client.objects.filter(is_active=True).order_by('last_name', 'first_name')
        self.fields['case'].queryset = Case.objects.filter(is_active=True).order_by('-opened_date')
        self.fields['bank_account'].queryset = BankAccount.objects.filter(is_active=True).order_by('bank_name')
        
        # Make fields required
        self.fields['client'].required = True
        self.fields['bank_account'].required = True
        self.fields['total_amount'].required = True
        
        # Set empty labels for better UX
        self.fields['case'].empty_label = "Select a case (optional)"
        self.fields['client'].empty_label = "Select a client"
        self.fields['bank_account'].empty_label = "Select bank account"


class SettlementDistributionForm(forms.ModelForm):
    class Meta:
        model = SettlementDistribution
        fields = [
            'distribution_type', 'vendor', 'client', 'amount', 
            'description', 'reference_number'
        ]
        widgets = {
            'distribution_type': forms.Select(attrs={
                'class': 'form-control'
            }),
            'vendor': forms.Select(attrs={
                'class': 'form-control'
            }),
            'client': forms.Select(attrs={
                'class': 'form-control'
            }),
            'amount': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0',
                'placeholder': '0.00'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Enter distribution description'
            }),
            'reference_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter check number (optional)'
            })
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['vendor'].queryset = Vendor.objects.filter(is_active=True).order_by('vendor_name')
        self.fields['client'].queryset = Client.objects.filter(is_active=True).order_by('last_name', 'first_name')
        
        # Make fields required
        self.fields['distribution_type'].required = True
        self.fields['amount'].required = True
        
        # Set empty labels
        self.fields['vendor'].empty_label = "Select vendor (if applicable)"
        self.fields['client'].empty_label = "Select client (if applicable)"
        
        # Add CSS classes for conditional display
        self.fields['vendor'].widget.attrs['id'] = 'id_vendor'
        self.fields['client'].widget.attrs['id'] = 'id_client'

    def clean(self):
        cleaned_data = super().clean()
        vendor = cleaned_data.get('vendor')
        client = cleaned_data.get('client')
        distribution_type = cleaned_data.get('distribution_type')
        
        # Validate that either vendor or client is selected, but not both
        if not vendor and not client:
            raise forms.ValidationError("Please select either a vendor or client recipient.")
        
        if vendor and client:
            raise forms.ValidationError("Please select either a vendor OR client, not both.")
        
        # Validate distribution type logic
        if distribution_type == 'CLIENT_REFUND' and not client:
            raise forms.ValidationError("Client refund must have a client recipient.")
        
        if distribution_type in ['VENDOR_PAYMENT', 'ATTORNEY_FEES', 'MEDICAL_EXPENSES'] and not vendor:
            raise forms.ValidationError("This distribution type requires a vendor recipient.")
        
        return cleaned_data


class SettlementReconciliationForm(forms.ModelForm):
    class Meta:
        model = SettlementReconciliation
        fields = [
            'bank_balance_after', 'client_balance_after', 'notes'
        ]
        widgets = {
            'bank_balance_after': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'placeholder': '0.00'
            }),
            'client_balance_after': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'placeholder': '0.00'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Enter reconciliation notes'
            })
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['bank_balance_after'].required = True
        self.fields['client_balance_after'].required = True