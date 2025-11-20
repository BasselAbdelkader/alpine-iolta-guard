from rest_framework import serializers
from apps.bank_accounts.models import BankTransaction


class CheckSerializer(serializers.ModelSerializer):
    """Serializer for checks to print"""

    client_name = serializers.SerializerMethodField()
    case_number = serializers.SerializerMethodField()
    vendor_name = serializers.SerializerMethodField()
    check_number = serializers.CharField(source='reference_number', read_only=True)

    class Meta:
        model = BankTransaction
        fields = [
            'id', 'transaction_number', 'transaction_date', 'amount',
            'payee', 'check_memo', 'reference_number', 'check_number',
            'client_name', 'case_number', 'vendor_name', 'check_is_printed'
        ]

    def get_client_name(self, obj):
        """Get client full name"""
        return obj.client.full_name if obj.client else None

    def get_case_number(self, obj):
        """Get case number"""
        return obj.case.case_number if obj.case else None

    def get_vendor_name(self, obj):
        """Get vendor name"""
        return obj.vendor.vendor_name if obj.vendor else None
