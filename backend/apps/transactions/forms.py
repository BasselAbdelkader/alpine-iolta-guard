from django import forms
from django.forms import inlineformset_factory
from django.core.exceptions import ValidationError
from datetime import date
# from .models import Transaction, TransactionItem  # OLD MODELS - COMMENTED OUT
from ..bank_accounts.models import BankAccount, BankTransaction
from ..clients.models import Client, Case
from ..vendors.models import Vendor
from ..settlements.models import Settlement


class DynamicCaseChoiceField(forms.ModelChoiceField):
    """Custom ModelChoiceField that validates cases dynamically based on selected client"""
    
    def to_python(self, value):
        if value in self.empty_values:
            return None
        try:
            # Try to get the case by ID, regardless of initial queryset
            case = Case.objects.get(pk=value, is_active=True)
            return case
        except (ValueError, TypeError, Case.DoesNotExist):
            raise forms.ValidationError(self.error_messages['invalid_choice'], code='invalid_choice')

class TransactionForm(forms.ModelForm):
    # Add fields from TransactionItem directly to the form
    client = forms.ModelChoiceField(
        queryset=Client.objects.filter(is_active=True),
        required=True,
        empty_label="Select Client",
        widget=forms.Select(attrs={'class': 'form-select', 'readonly': True})
    )
    case = DynamicCaseChoiceField(
        queryset=Case.objects.none(),  # Start empty, will be populated via AJAX
        required=True,
        empty_label="Select Case",
        widget=forms.Select(attrs={'class': 'form-select', 'readonly': True})
    )
    payee_name = forms.CharField(
        max_length=255,
        required=True,
        label="Payee",
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter payee name...',
            'autocomplete': 'off'
        })
    )

    class Meta:
        model = BankTransaction
        fields = [
            'bank_account', 'transaction_type', 'transaction_date', 'amount',
            'check_memo', 'description', 'reference_number', 'status', 'cleared_date', 'check_is_printed'
        ]
        widgets = {
            'bank_account': forms.Select(attrs={
                'class': 'form-select'
            }),
            'transaction_type': forms.Select(attrs={
                'class': 'form-select'
            }),
            'transaction_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'amount': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'placeholder': '0.00'
            }),
            'check_memo': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Check memo'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Enter detailed transaction description'
            }),
            'reference_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Check number, wire reference, etc.'
            }),
            'status': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'cleared_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'check_is_printed': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            })
        }
        
    def __init__(self, *args, **kwargs):
        # Extract custom parameters
        client_id = kwargs.pop('client_id', None)
        case_id = kwargs.pop('case_id', None)
        
        super().__init__(*args, **kwargs)
        
        # Set default bank account to the first active one
        active_bank_accounts = BankAccount.objects.filter(is_active=True).order_by('bank_name', 'account_name')
        self.fields['bank_account'].queryset = active_bank_accounts
        if active_bank_accounts.exists():
            self.fields['bank_account'].initial = active_bank_accounts.first()
        self.fields['bank_account'].empty_label = "Select Bank Account"
        self.fields['bank_account'].required = True
        
        # Set transaction type defaults
        self.fields['transaction_type'].required = True
        self.fields['transaction_type'].initial = 'WITHDRAWAL'  # Default to Withdrawal
        
        # Set transaction date to today and make it required
        self.fields['transaction_date'].required = True
        self.fields['transaction_date'].initial = date.today()

        self.fields['amount'].required = True

        # Make payee, memo, description, and reference required
        self.fields['check_memo'].required = True
        self.fields['description'].required = True
        self.fields['reference_number'].required = True
        
        # Handle client and case restrictions based on parameters
        if client_id and case_id:
            try:
                # Restrict to specific client and case
                specific_client = Client.objects.get(id=client_id, is_active=True)
                specific_case = Case.objects.get(id=case_id, client=specific_client, is_active=True)

                # Store restricted IDs for validation
                self.restricted_client_id = client_id
                self.restricted_case_id = case_id

                # Set client dropdown to only show this client
                self.fields['client'].queryset = Client.objects.filter(id=client_id)
                self.fields['client'].initial = specific_client
                # Make visually disabled but still functional for form submission
                self.fields['client'].widget.attrs.update({
                    'style': 'pointer-events: none; background-color: #f8f9fa; color: #6c757d;',
                    'data-restricted': 'true',
                    'title': 'Pre-selected for this case'
                })

                # Set case dropdown to only show this case
                self.fields['case'].queryset = Case.objects.filter(id=case_id)
                self.fields['case'].initial = specific_case
                # Make visually disabled but still functional for form submission
                self.fields['case'].widget.attrs.update({
                    'style': 'pointer-events: none; background-color: #f8f9fa; color: #6c757d;',
                    'data-restricted': 'true',
                    'title': 'Pre-selected for this case'
                })

            except (Client.DoesNotExist, Case.DoesNotExist):
                # Fallback to normal behavior if invalid IDs
                self.fields['client'].queryset = Client.objects.filter(is_active=True).order_by('first_name', 'last_name')
                self.fields['case'].queryset = Case.objects.none()
        else:
            # Normal behavior for other scenarios
            self.fields['client'].queryset = Client.objects.filter(is_active=True).order_by('first_name', 'last_name')

            # If editing and there's a client selected, populate cases for that client
            if self.instance and hasattr(self.instance, 'pk') and self.instance.pk:
                # In consolidated model, client is directly on the transaction
                if self.instance.client:
                    self.fields['case'].queryset = Case.objects.filter(
                        client=self.instance.client,
                        is_active=True
                    ).order_by('-opened_date')

        # When editing existing transaction, make client and case read-only and greyed out
        if self.instance and hasattr(self.instance, 'pk') and self.instance.pk:
            # In consolidated model, client and case are directly on the transaction
            if self.instance.client and self.instance.case:
                # Set client field as read-only and greyed out
                self.fields['client'].queryset = Client.objects.filter(id=self.instance.client.id)
                self.fields['client'].initial = self.instance.client
                self.fields['client'].widget.attrs.update({
                    'disabled': True,
                    'style': 'background-color: #e9ecef !important; color: #6c757d !important; pointer-events: none !important;',
                    'title': 'Client cannot be changed when editing transactions'
                })

                # Set case field as read-only and greyed out
                self.fields['case'].queryset = Case.objects.filter(id=self.instance.case.id)
                self.fields['case'].initial = self.instance.case
                self.fields['case'].widget.attrs.update({
                    'disabled': True,
                    'style': 'background-color: #e9ecef !important; color: #6c757d !important; pointer-events: none !important;',
                    'title': 'Case cannot be changed when editing transactions'
                })
    
    def clean(self):
        cleaned_data = super().clean()
        client = cleaned_data.get('client')
        case = cleaned_data.get('case')
        transaction_date = cleaned_data.get('transaction_date')
        
        # If both client and case are selected, validate that case belongs to client
        if client and case:
            if case.client != client:
                raise forms.ValidationError("Selected case does not belong to the selected client.")
        
        # Validate transaction date is not before last settlement date for the case
        if case and transaction_date:
            last_settlement = Settlement.objects.filter(
                case=case,
                status='COMPLETED'
            ).order_by('-settlement_date').first()
            
            if last_settlement and transaction_date < last_settlement.settlement_date:
                raise forms.ValidationError({
                    'transaction_date': f'Transaction date cannot be before the last settlement date ({last_settlement.settlement_date.strftime("%Y-%m-%d")})'
                })
        
        return cleaned_data
    
    def clean_client(self):
        client = self.cleaned_data.get('client')
        # Allow restricted client values even if they're not in the initial queryset
        if not client and hasattr(self, 'restricted_client_id'):
            try:
                client = Client.objects.get(id=self.restricted_client_id, is_active=True)
            except Client.DoesNotExist:
                pass
        return client
    
    def clean_case(self):
        case = self.cleaned_data.get('case')
        # Allow restricted case values even if they're not in the initial queryset
        if not case and hasattr(self, 'restricted_case_id'):
            try:
                case = Case.objects.get(id=self.restricted_case_id, is_active=True)
            except Case.DoesNotExist:
                pass
        return case

# OLD TRANSACTION ITEM FORM - NOT NEEDED WITH CONSOLIDATED MODEL
# class TransactionItemForm(forms.ModelForm):
#     class Meta:
#         model = TransactionItem
#         fields = ['client', 'case', 'vendor', 'amount', 'description', 'item_type']
#     # ... rest commented out

# TransactionItemFormSet = inlineformset_factory(
#     Transaction,
#     TransactionItem,
#     form=TransactionItemForm,
#     extra=1,
#     can_delete=True,
#     min_num=0,
#     validate_min=True
# )