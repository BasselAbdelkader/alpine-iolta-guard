from rest_framework import serializers
from ..bank_accounts.models import BankTransaction


class BankTransactionItemSerializer(serializers.ModelSerializer):
    """Serializer for BankTransaction model (for individual transaction items)"""

    client_name = serializers.CharField(source='client.full_name', read_only=True)
    client_number = serializers.CharField(source='client.client_number', read_only=True)
    case_title = serializers.CharField(source='case.case_title', read_only=True)
    case_number = serializers.CharField(source='case.case_number', read_only=True)
    vendor_name = serializers.CharField(source='vendor.name', read_only=True)
    item_type_display = serializers.CharField(source='get_item_type_display', read_only=True)

    class Meta:
        model = BankTransaction
        fields = [
            'id', 'bank_account', 'client', 'client_name', 'client_number',
            'case', 'case_title', 'case_number', 'vendor', 'vendor_name',
            'amount', 'description', 'item_type', 'item_type_display',
            'transaction_type', 'transaction_date', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']

    def validate_amount(self, value):
        """Ensure amount is positive"""
        if value <= 0:
            raise serializers.ValidationError("Amount must be positive")
        return value

    def validate(self, data):
        """Custom validation for transaction items"""
        # Ensure case is provided
        if not data.get('case'):
            raise serializers.ValidationError("Every transaction item must be linked to a case")

        # If client is not provided but case is, use case's client
        if not data.get('client') and data.get('case'):
            data['client'] = data['case'].client

        # Validate item type matches the linked entities
        item_type = data.get('item_type')
        if item_type == 'CLIENT_DEPOSIT' and not data.get('client'):
            raise serializers.ValidationError("Client must be specified for CLIENT_DEPOSIT items")
        elif item_type == 'VENDOR_PAYMENT' and not data.get('vendor'):
            raise serializers.ValidationError("Vendor must be specified for VENDOR_PAYMENT items")

        return data


class BankTransactionSerializer(serializers.ModelSerializer):
    """Complete serializer for BankTransaction model"""

    bank_account_name = serializers.CharField(source='bank_account.account_name', read_only=True)
    bank_account_number = serializers.CharField(source='bank_account.account_number', read_only=True)
    transaction_type_display = serializers.CharField(source='get_transaction_type_display', read_only=True)
    client_name = serializers.CharField(source='client.full_name', read_only=True)
    case_title = serializers.CharField(source='case.case_title', read_only=True)
    vendor_name = serializers.CharField(source='vendor.name', read_only=True)
    item_type_display = serializers.CharField(source='get_item_type_display', read_only=True)

    class Meta:
        model = BankTransaction
        fields = [
            'id', 'transaction_number', 'bank_account', 'bank_account_name', 'bank_account_number',
            'transaction_type', 'transaction_type_display', 'transaction_date', 'amount',
            'description', 'reference_number', 'status', 'cleared_date',
            'voided_date', 'voided_by', 'void_reason',
            'client', 'client_name', 'case', 'case_title', 'vendor', 'vendor_name',
            'item_type', 'item_type_display', 'memo', 'payee', 'reference_number',
            'created_by', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'transaction_number', 'created_at', 'updated_at']

    def validate_amount(self, value):
        """Ensure amount is positive"""
        if value <= 0:
            raise serializers.ValidationError("Amount must be positive")
        return value

    def validate(self, data):
        """Custom validation for transactions"""
        transaction_type = data.get('transaction_type')
        is_cleared = data.get('status')
        cleared_date = data.get('cleared_date')

        # If transaction is marked as cleared, cleared_date should be provided
        if is_cleared and not cleared_date:
            from datetime import date
            data['cleared_date'] = date.today()

        return data

    def create(self, validated_data):
        """Create bank transaction"""
        return BankTransaction.objects.create(**validated_data)

    def update(self, instance, validated_data):
        """Update bank transaction"""
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance


class BankTransactionListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for bank transaction list views"""

    bank_account_name = serializers.CharField(source='bank_account.account_name', read_only=True)
    transaction_type_display = serializers.CharField(source='get_transaction_type_display', read_only=True)
    case_title = serializers.CharField(source='case.case_title', read_only=True)
    client_name = serializers.CharField(source='client.full_name', read_only=True)

    class Meta:
        model = BankTransaction
        fields = [
            'id', 'transaction_number', 'bank_account_name',
            'transaction_type', 'transaction_type_display', 'transaction_date',
            'amount', 'description', 'reference_number', 'status',
            'case_title', 'client_name', 'created_at'
        ]


class BankTransactionItemListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for bank transaction item list views"""

    client_name = serializers.CharField(source='client.full_name', read_only=True)
    case_title = serializers.CharField(source='case.case_title', read_only=True)
    vendor_name = serializers.CharField(source='vendor.name', read_only=True)
    item_type_display = serializers.CharField(source='get_item_type_display', read_only=True)

    class Meta:
        model = BankTransaction
        fields = [
            'id', 'transaction_number', 'transaction_date', 'transaction_type',
            'client_name', 'case_title', 'vendor_name', 'amount',
            'description', 'item_type', 'item_type_display', 'created_at'
        ]