from rest_framework import serializers
from django.utils import timezone
from django.contrib.auth.models import User
from ..models import BankAccount, BankTransaction, BankReconciliation, TransactionApproval


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
            'reference_number', 'bank_reference', 'bank_category',
            'status', 'status_display',
            'client', 'client_name', 'case', 'case_number', 'vendor', 'vendor_name', 'payee',
            'reconciliation_notes', 'transaction_number', 'created_at', 'updated_at', 'created_by',
            'voided_date', 'voided_by', 'void_reason'
        ]
        read_only_fields = ['id', 'bank_reference', 'transaction_number', 'created_at', 'updated_at']

    def validate(self, data):
        """Validate that all required fields are provided"""
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

        # ===================================================================
        # COMPLIANCE CONTROL #1: NEGATIVE BALANCE PREVENTION
        # ===================================================================
        # CRITICAL: Prevent withdrawals that would create negative balances
        # This prevents illegal commingling of client funds (ABA Rule 1.15)
        # ===================================================================

        transaction_type = data.get('transaction_type')

        # Only validate withdrawals (deposits can't create negative balances)
        if transaction_type in ['WITHDRAWAL', 'TRANSFER_OUT']:
            client = data.get('client')
            case = data.get('case')
            withdrawal_amount = data.get('amount')

            if client and case and withdrawal_amount:
                from decimal import Decimal
                withdrawal_amount = Decimal(str(withdrawal_amount))

                # Get current balances
                client_balance = client.get_current_balance()
                case_balance = case.get_current_balance()

                # CRITICAL CHECK #1: Client balance must be sufficient
                if withdrawal_amount > client_balance:
                    errors['amount'] = (
                        f'Insufficient client funds. '
                        f'Client "{client.full_name}" has ${client_balance:,.2f} available. '
                        f'Cannot withdraw ${withdrawal_amount:,.2f}. '
                        f'Negative balances are prohibited by trust accounting rules.'
                    )

                # CRITICAL CHECK #2: Case balance must be sufficient
                if withdrawal_amount > case_balance:
                    errors['amount'] = (
                        f'Insufficient case funds. '
                        f'Case "{case.case_title}" has ${case_balance:,.2f} available. '
                        f'Cannot withdraw ${withdrawal_amount:,.2f}. '
                        f'Negative balances are prohibited by trust accounting rules.'
                    )

        if errors:
            raise serializers.ValidationError(errors)

        return data

    def create(self, validated_data):
        """Override create to pass audit parameters to model save()"""
        # Extract audit parameters (passed from view)
        audit_user = validated_data.pop('audit_user', 'system')
        audit_reason = validated_data.pop('audit_reason', '')
        audit_ip = validated_data.pop('audit_ip', '127.0.0.1')

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


# ===================================================================
# COMPLIANCE CONTROL #3: TWO-PERSON APPROVAL WORKFLOW SERIALIZERS
# ===================================================================

class UserSerializer(serializers.ModelSerializer):
    """Lightweight serializer for User model (for approval workflow)"""
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'full_name']
        read_only_fields = fields

    def get_full_name(self, obj):
        """Get user's full name or username if name not set"""
        if obj.first_name or obj.last_name:
            return f"{obj.first_name} {obj.last_name}".strip()
        return obj.username


class TransactionApprovalSerializer(serializers.ModelSerializer):
    """
    Serializer for TransactionApproval model with nested transaction details.

    COMPLIANCE CONTROL #3: Two-Person Approval Workflow
    - Maker-checker pattern enforcement
    - Permission-based approval authorization
    - Complete audit trail
    """

    # Nested serializers (read-only)
    transaction = BankTransactionSerializer(read_only=True)
    created_by = UserSerializer(read_only=True)
    reviewed_by = UserSerializer(read_only=True)

    # Computed fields
    days_pending = serializers.SerializerMethodField()
    can_approve = serializers.SerializerMethodField()
    is_creator = serializers.SerializerMethodField()
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = TransactionApproval
        fields = [
            'id', 'transaction', 'created_by', 'created_at',
            'reviewed_by', 'reviewed_at', 'status', 'status_display',
            'request_notes', 'review_notes', 'ip_address',
            'days_pending', 'can_approve', 'is_creator'
        ]
        read_only_fields = [
            'id', 'transaction', 'created_by', 'created_at',
            'reviewed_by', 'reviewed_at', 'ip_address'
        ]

    def get_days_pending(self, obj):
        """Calculate days since approval was requested"""
        if obj.status == 'pending':
            delta = timezone.now() - obj.created_at
            return delta.days
        return None

    def get_can_approve(self, obj):
        """
        Check if current user can approve this transaction.

        Requirements:
        1. User must have 'can_approve_transactions' permission
        2. User must NOT be the creator (maker-checker)
        3. Status must be 'pending'
        """
        request = self.context.get('request')
        if not request or not request.user:
            return False

        user = request.user

        # Must be pending
        if obj.status != 'pending':
            return False

        # Must have permission
        if not user.has_perm('bank_accounts.can_approve_transactions'):
            return False

        # Cannot approve own transaction (maker-checker)
        if obj.created_by_id == user.id:
            return False

        return True

    def get_is_creator(self, obj):
        """Check if current user is the creator of this approval request"""
        request = self.context.get('request')
        if not request or not request.user:
            return False

        return obj.created_by_id == request.user.id


class TransactionApprovalListSerializer(serializers.ModelSerializer):
    """
    Lightweight serializer for TransactionApproval list views.
    Shows essential info without full transaction details.
    """

    # Transaction summary fields (without full nested serializer)
    transaction_id = serializers.IntegerField(source='transaction.id', read_only=True)
    transaction_number = serializers.CharField(source='transaction.transaction_number', read_only=True)
    transaction_amount = serializers.DecimalField(
        source='transaction.amount',
        max_digits=15,
        decimal_places=2,
        read_only=True
    )
    transaction_type = serializers.CharField(source='transaction.transaction_type', read_only=True)
    transaction_date = serializers.DateField(source='transaction.transaction_date', read_only=True)

    # Related entity summary
    client_name = serializers.CharField(source='transaction.client.full_name', read_only=True)
    case_number = serializers.CharField(source='transaction.case.case_number', read_only=True)
    payee = serializers.CharField(source='transaction.payee', read_only=True)

    # User summary
    created_by_name = serializers.CharField(source='created_by.username', read_only=True)
    reviewed_by_name = serializers.CharField(source='reviewed_by.username', read_only=True, allow_null=True)

    # Computed fields
    days_pending = serializers.SerializerMethodField()
    can_approve = serializers.SerializerMethodField()
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = TransactionApproval
        fields = [
            'id', 'transaction_id', 'transaction_number', 'transaction_amount',
            'transaction_type', 'transaction_date', 'client_name', 'case_number', 'payee',
            'created_by_name', 'created_at', 'reviewed_by_name', 'reviewed_at',
            'status', 'status_display', 'request_notes', 'days_pending', 'can_approve'
        ]

    def get_days_pending(self, obj):
        """Calculate days since approval was requested"""
        if obj.status == 'pending':
            delta = timezone.now() - obj.created_at
            return delta.days
        return None

    def get_can_approve(self, obj):
        """Check if current user can approve this transaction"""
        request = self.context.get('request')
        if not request or not request.user:
            return False

        user = request.user

        # Must be pending
        if obj.status != 'pending':
            return False

        # Must have permission
        if not user.has_perm('bank_accounts.can_approve_transactions'):
            return False

        # Cannot approve own transaction (maker-checker)
        if obj.created_by_id == user.id:
            return False

        return True
