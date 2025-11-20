from rest_framework import serializers
from ..models import BankAccount, BankTransaction, BankReconciliation


class BankAccountSerializer(serializers.ModelSerializer):
    """Complete serializer for BankAccount model"""

    trust_balance = serializers.SerializerMethodField()
    register_balance = serializers.SerializerMethodField()
    pending_count = serializers.SerializerMethodField()
    formatted_trust_balance = serializers.SerializerMethodField()
    account_type_display = serializers.CharField(source='get_account_type_display', read_only=True)
    transactions_count = serializers.SerializerMethodField()
    last_transaction_date = serializers.SerializerMethodField()

    class Meta:
        model = BankAccount
        fields = [
            'id', 'account_number', 'bank_name', 'bank_address', 'account_name',
            'routing_number', 'account_type', 'account_type_display', 'opening_balance',
            'trust_balance', 'register_balance', 'pending_count',
            'formatted_trust_balance', 'is_active', 'next_check_number',
            'transactions_count', 'last_transaction_date', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_trust_balance(self, obj):
        """Get trust balance (ALL non-voided transactions: pending + cleared)"""
        return obj.get_current_balance()

    def get_register_balance(self, obj):
        """Get register balance (same as trust balance - ALL non-voided transactions)"""
        return obj.get_register_balance()

    def get_pending_count(self, obj):
        """Get count of pending transactions"""
        return obj.get_pending_transactions_count()

    def get_formatted_trust_balance(self, obj):
        """Get professionally formatted trust balance"""
        balance = obj.get_current_balance()
        if balance < 0:
            return f"({abs(balance):,.2f})"  # Parentheses for negative
        return f"{balance:,.2f}"
    
    def get_transactions_count(self, obj):
        """Count of transactions for this bank account"""
        return obj.bank_transactions.count()

    def get_last_transaction_date(self, obj):
        """Date of most recent transaction"""
        last_transaction = obj.bank_transactions.order_by('-transaction_date').first()
        return last_transaction.transaction_date if last_transaction else None
    
    def validate_account_number(self, value):
        """Validate account number is unique"""
        if BankAccount.objects.filter(account_number=value).exists():
            raise serializers.ValidationError("Account number already exists")
        return value
    
    def validate_opening_balance(self, value):
        """Validate opening balance is non-negative"""
        if value < 0:
            raise serializers.ValidationError("Opening balance cannot be negative")
        return value


class BankAccountListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for bank account list views"""

    trust_balance = serializers.SerializerMethodField()
    register_balance = serializers.SerializerMethodField()
    formatted_trust_balance = serializers.SerializerMethodField()
    account_type_display = serializers.CharField(source='get_account_type_display', read_only=True)

    class Meta:
        model = BankAccount
        fields = [
            'id', 'account_number', 'bank_name', 'account_name',
            'account_type', 'account_type_display', 'opening_balance',
            'trust_balance', 'register_balance',
            'formatted_trust_balance', 'next_check_number',
            'is_active', 'created_at'
        ]

    def get_trust_balance(self, obj):
        """Trust balance (ALL non-voided transactions)"""
        return obj.get_current_balance()

    def get_register_balance(self, obj):
        """Register balance (same as trust balance)"""
        return obj.get_register_balance()

    def get_formatted_trust_balance(self, obj):
        balance = obj.get_current_balance()
        if balance < 0:
            return f"({abs(balance):,.2f})"
        return f"{balance:,.2f}"


class BankTransactionSerializer(serializers.ModelSerializer):
    """Serializer for BankTransaction model"""

    bank_account_name = serializers.CharField(source='bank_account.account_name', read_only=True)
    bank_account_number = serializers.CharField(source='bank_account.account_number', read_only=True)
    transaction_type_display = serializers.CharField(source='get_transaction_type_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    # Add client, case, vendor, payee fields
    client_name = serializers.CharField(source='client.full_name', read_only=True, allow_null=True)
    case_number = serializers.CharField(source='case.case_number', read_only=True, allow_null=True)
    vendor_name = serializers.CharField(source='vendor.vendor_name', read_only=True, allow_null=True)

    class Meta:
        model = BankTransaction
        fields = [
            'id', 'bank_account', 'bank_account_name', 'bank_account_number',
            'transaction_date', 'post_date', 'transaction_type', 'transaction_type_display',
            'amount', 'description', 'check_memo',
            'reference_number', 'check_number', 'bank_reference', 'bank_category',
            'status', 'status_display',
            'client', 'client_name', 'case', 'case_number', 'vendor', 'vendor_name', 'payee',
            'reconciliation_notes', 'transaction_number', 'created_at', 'updated_at', 'created_by',
            'voided_date', 'voided_by', 'void_reason'
        ]
        read_only_fields = ['id', 'bank_reference', 'transaction_number', 'created_at', 'updated_at']

    def validate(self, data):
        """Validate that all required fields are provided"""
        from decimal import Decimal
        errors = {}

        # REQUIREMENT: If status is "Cleared" or "Reconciled", block ALL editing except description
        if self.instance and self.instance.status in ['cleared', 'reconciled']:
            # This is an update to an existing cleared/reconciled transaction
            # Only allow changes to description field
            allowed_changes = ['description']
            changed_fields = []

            for field, value in data.items():
                if field not in allowed_changes:
                    # Check if this field is actually changing
                    if hasattr(self.instance, field) and getattr(self.instance, field) != value:
                        changed_fields.append(field)

            if changed_fields:
                errors['non_field_errors'] = [
                    f'Cannot modify {self.instance.get_status_display()} transactions. '
                    f'Only the description field can be edited. '
                    f'Attempted to change: {", ".join(changed_fields)}'
                ]

        # Check if bank_account is provided
        if not data.get('bank_account'):
            errors['bank_account'] = 'Please select a Bank Account before saving the transaction.'

        # Check if client is provided
        if not data.get('client'):
            errors['client'] = 'Please select a Client before saving the transaction.'

        # Check if case is provided
        if not data.get('case'):
            errors['case'] = 'Please select a Case before saving the transaction.'

        # Check if transaction_date is provided
        if not data.get('transaction_date'):
            errors['transaction_date'] = 'Please enter a Transaction Date before saving the transaction.'

        # Check if transaction_type is provided
        if not data.get('transaction_type'):
            errors['transaction_type'] = 'Please select a Transaction Type before saving the transaction.'

        # Check if reference_number is provided
        if not data.get('reference_number'):
            errors['reference_number'] = 'Please enter a Reference Number before saving the transaction.'

        # Check if payee is provided
        if not data.get('payee') or not data.get('payee').strip():
            errors['payee'] = 'Please enter a Payee before saving the transaction.'

        # Check if amount is provided and valid
        amount = data.get('amount')
        if not amount or float(amount) <= 0:
            errors['amount'] = 'Please enter a valid Amount before saving the transaction.'

        # Check if description is provided
        if not data.get('description') or not data.get('description').strip():
            errors['description'] = 'Please enter a Description before saving the transaction.'

        # CRITICAL VALIDATION: Prevent negative balances for withdrawals
        if data.get('transaction_type') in ['WITHDRAWAL', 'TRANSFER_OUT'] and data.get('client') and data.get('case') and data.get('amount'):
            from apps.clients.models import Client, Case

            client = data.get('client')
            case = data.get('case')
            withdrawal_amount = Decimal(str(data.get('amount')))

            # Get current balances
            client_balance = Decimal(str(client.get_current_balance() or 0))
            case_balance = Decimal(str(case.get_current_balance() or 0))

            # If this is an update (editing existing transaction), we need to add back the old amount
            if self.instance:
                old_amount = Decimal(str(self.instance.amount or 0))
                if self.instance.transaction_type in ['WITHDRAWAL', 'TRANSFER_OUT']:
                    # Add back the old withdrawal to get the "before" balance
                    client_balance += old_amount
                    case_balance += old_amount

            # Check if withdrawal would cause negative balance
            new_client_balance = client_balance - withdrawal_amount
            new_case_balance = case_balance - withdrawal_amount

            if new_client_balance < 0:
                errors['amount'] = f'Insufficient funds. Client balance: ${client_balance:,.2f}. Cannot withdraw ${withdrawal_amount:,.2f}.'

            if new_case_balance < 0:
                errors['amount'] = f'Insufficient funds. Case balance: ${case_balance:,.2f}. Cannot withdraw ${withdrawal_amount:,.2f}.'

        if errors:
            raise serializers.ValidationError(errors)

        return data

    def create(self, validated_data):
        """Override create to pass audit parameters to model save()"""
        # Extract audit parameters (passed from view)
        audit_user = validated_data.pop('audit_user', 'system')
        audit_reason = validated_data.pop('audit_reason', '')
        audit_ip = validated_data.pop('audit_ip', '127.0.0.1')

        # ROOT CAUSE FIX: Auto-link vendor by matching payee name to vendor_name
        payee = validated_data.get('payee')
        if payee and not validated_data.get('vendor'):
            from apps.vendors.models import Vendor
            # Try to find vendor by exact name match (case-insensitive)
            vendor = Vendor.objects.filter(vendor_name__iexact=payee.strip()).first()
            if vendor:
                validated_data['vendor'] = vendor

        # Create instance
        instance = BankTransaction(**validated_data)
        instance.save(audit_user=audit_user, audit_reason=audit_reason, audit_ip=audit_ip)
        return instance

    def update(self, instance, validated_data):
        """Override update to pass audit parameters to model save()"""
        # Extract audit parameters (passed from view)
        audit_user = validated_data.pop('audit_user', 'system')
        audit_reason = validated_data.pop('audit_reason', '')
        audit_ip = validated_data.pop('audit_ip', '127.0.0.1')

        # ROOT CAUSE FIX: Auto-link vendor if payee changed
        if 'payee' in validated_data and not validated_data.get('vendor'):
            from apps.vendors.models import Vendor
            payee = validated_data.get('payee')
            if payee:
                vendor = Vendor.objects.filter(vendor_name__iexact=payee.strip()).first()
                if vendor:
                    validated_data['vendor'] = vendor

        # Update instance fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        # Save with audit parameters
        instance.save(audit_user=audit_user, audit_reason=audit_reason, audit_ip=audit_ip)
        return instance


class BankReconciliationSerializer(serializers.ModelSerializer):
    """Serializer for BankReconciliation model"""
    
    bank_account_name = serializers.CharField(source='bank_account.account_name', read_only=True)
    difference = serializers.DecimalField(max_digits=15, decimal_places=2, read_only=True)
    is_balanced = serializers.SerializerMethodField()
    
    class Meta:
        model = BankReconciliation
        fields = [
            'id', 'bank_account', 'bank_account_name', 'reconciliation_date',
            'statement_balance', 'book_balance', 'difference', 'is_balanced',
            'is_reconciled', 'reconciled_by', 'reconciled_at', 'notes',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'difference', 'created_at', 'updated_at']
    
    def get_is_balanced(self, obj):
        """Check if statement and book balance match"""
        return obj.difference == 0
    
    def validate(self, data):
        """Custom validation for reconciliation"""
        if data.get('is_reconciled') and not data.get('reconciled_by'):
            data['reconciled_by'] = self.context.get('request').user.username if self.context.get('request') else 'system'
        
        return data
