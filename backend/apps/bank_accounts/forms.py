from django import forms
from .models import BankAccount, BankTransaction

class BankAccountForm(forms.ModelForm):
    class Meta:
        model = BankAccount
        fields = [
            'account_number', 'bank_name', 'bank_address', 'account_name',
            'routing_number', 'account_type', 'opening_balance', 'next_check_number', 'is_active'
        ]
        widgets = {
            'account_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter account number'
            }),
            'bank_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter bank name'
            }),
            'bank_address': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Enter bank address'
            }),
            'account_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter account name'
            }),
            'routing_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter routing number'
            }),
            'account_type': forms.Select(attrs={
                'class': 'form-select'
            }),
            'opening_balance': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'placeholder': '0.00'
            }),
            'next_check_number': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '1001',
                'min': '1'
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            })
        }
        labels = {
            'next_check_number': 'Starting Check Number (IOLTA Compliance)'
        }
        help_texts = {
            'next_check_number': 'Enter the first check number from your pre-numbered check stock. Sequential numbering ensures IOLTA compliance.'
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['account_number'].required = True
        self.fields['bank_name'].required = True
        self.fields['account_name'].required = True
        self.fields['next_check_number'].required = True
        self.fields['is_active'].initial = True


class BankTransactionForm(forms.ModelForm):
    class Meta:
        model = BankTransaction
        fields = [
            'bank_account', 'transaction_date', 'post_date', 'transaction_type',
            'amount', 'description', 'client', 'case', 'vendor', 'payee', 'check_memo',
            'reference_number', 'bank_reference', 'bank_category',
            'reconciliation_notes', 'status', 'check_is_printed'
        ]
        widgets = {
            'bank_account': forms.Select(attrs={
                'class': 'form-select'
            }),
            'transaction_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'post_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'transaction_type': forms.Select(attrs={
                'class': 'form-select'
            }),
            'amount': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Enter transaction description'
            }),
            'reference_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Wire reference, ACH number, etc.'
            }),
            'bank_reference': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Bank internal reference number'
            }),
            'client': forms.Select(attrs={
                'class': 'form-select'
            }),
            'case': forms.Select(attrs={
                'class': 'form-select'
            }),
            'vendor': forms.Select(attrs={
                'class': 'form-select'
            }),
            'payee': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Payee name (if different from vendor)'
            }),
            'check_memo': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 1,
                'placeholder': 'Check memo (appears on check)'
            }),
            'bank_category': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Bank transaction category'
            }),
            'reconciliation_notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Notes for reconciliation'
            }),
            'status': forms.Select(attrs={
                'class': 'form-select'
            }),
            'check_is_printed': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            })
        }
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['bank_account'].queryset = BankAccount.objects.filter(is_active=True)
        self.fields['bank_account'].empty_label = "Select Bank Account"

        # Required fields
        self.fields['bank_account'].required = True
        self.fields['transaction_date'].required = True
        self.fields['transaction_type'].required = True
        self.fields['amount'].required = True
        self.fields['description'].required = True
        self.fields['reference_number'].required = True
        self.fields['payee'].required = True
        self.fields['check_memo'].required = False  # Not required

        # Client and Case: OPTIONAL in dynamic mode, but MUST be validated in view
        # If missing, transaction won't be assigned to any client (causes deficit!)
        self.fields['client'].required = False
        self.fields['case'].required = False

        # Custom error messages per PDF requirements
        self.fields['bank_account'].error_messages = {
            'required': 'Please choose a bank account.'
        }
        self.fields['payee'].error_messages = {
            'required': 'Please add a valid payee.'
        }
        self.fields['amount'].error_messages = {
            'required': 'Please enter a valid amount.',
            'invalid': 'Please enter a valid amount.'
        }
        # Generic error messages for other fields
        self.fields['transaction_date'].error_messages = {'required': 'Date is required.'}
        self.fields['transaction_type'].error_messages = {'required': 'Type is required.'}
        self.fields['reference_number'].error_messages = {'required': 'Ref is required.'}
        self.fields['description'].error_messages = {'required': 'Description is required.'}

        # Set up related object fields
        from apps.clients.models import Client, Case
        from apps.vendors.models import Vendor

        self.fields['client'].queryset = Client.objects.filter(is_active=True).order_by('first_name', 'last_name')
        self.fields['client'].empty_label = "Select Client"
        self.fields['client'].required = False

        self.fields['case'].queryset = Case.objects.filter(is_active=True).order_by('-opened_date')
        self.fields['case'].empty_label = "Select Case"
        self.fields['case'].required = False

        self.fields['vendor'].queryset = Vendor.objects.filter(is_active=True).order_by('vendor_name')
        self.fields['vendor'].empty_label = "Select Vendor"
        self.fields['vendor'].required = False

        # Set default status to pending
        self.fields['status'].initial = 'pending'
        self.fields['status'].required = False

        # Set today as default date
        from datetime import date
        self.fields['transaction_date'].initial = date.today()

    def clean_payee(self):
        """Validate payee field - REQUIRED for all transactions"""
        payee = self.cleaned_data.get('payee')

        # Strip whitespace
        if payee:
            payee = payee.strip()

        # CRITICAL: Payee is REQUIRED - prevents untracked transactions
        if not payee:
            raise forms.ValidationError('Payee is required. Please add a valid payee.')

        return payee

    def clean_amount(self):
        """Accept decimals and commas per PDF requirements"""
        amount = self.cleaned_data.get('amount')
        if amount is not None:
            # Amount already cleaned by Django, just validate it's positive
            from decimal import Decimal
            if amount <= Decimal('0'):
                raise forms.ValidationError('Please enter a valid amount.')
        return amount


class BankTransactionSearchForm(forms.Form):
    """Form for searching and filtering bank transactions"""
    search = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search by description, reference, check number...'
        })
    )
    
    transaction_type = forms.ChoiceField(
        required=False,
        choices=[('', 'All Types')] + BankTransaction.TRANSACTION_TYPE_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    status = forms.ChoiceField(
        required=False,
        choices=[('', 'All Status')] + BankTransaction.STATUS_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    date_from = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        })
    )
    
    date_to = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        })
    )