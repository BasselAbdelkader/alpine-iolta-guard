from rest_framework import serializers
from apps.clients.models import Client, Case
from apps.bank_accounts.models import BankTransaction


class ClientLedgerTransactionSerializer(serializers.Serializer):
    """Serializer for individual transaction in client ledger"""
    date = serializers.DateField()
    description = serializers.CharField()
    reference = serializers.CharField()
    transaction_number = serializers.CharField()
    transaction_type = serializers.CharField()
    debit = serializers.DecimalField(max_digits=15, decimal_places=2)
    credit = serializers.DecimalField(max_digits=15, decimal_places=2)
    balance = serializers.DecimalField(max_digits=15, decimal_places=2)
    status = serializers.CharField()
    reference_number = serializers.CharField(allow_blank=True)
    payee = serializers.CharField(allow_blank=True)
    case_title = serializers.CharField(allow_blank=True, allow_null=True)


class ClientLedgerSummarySerializer(serializers.Serializer):
    """Serializer for ledger summary totals"""
    opening_balance = serializers.DecimalField(max_digits=15, decimal_places=2)
    total_debits = serializers.DecimalField(max_digits=15, decimal_places=2)
    total_credits = serializers.DecimalField(max_digits=15, decimal_places=2)
    closing_balance = serializers.DecimalField(max_digits=15, decimal_places=2)


class ClientLedgerSerializer(serializers.Serializer):
    """Main serializer for client ledger report"""
    client = serializers.SerializerMethodField()
    case = serializers.SerializerMethodField()
    date_from = serializers.DateField()
    date_to = serializers.DateField()
    transactions = ClientLedgerTransactionSerializer(many=True)
    summary = ClientLedgerSummarySerializer()

    def get_client(self, obj):
        """Return client details"""
        client = obj.get('client')
        if not client:
            return None

        return {
            'id': client.id,
            'client_number': client.client_number,
            'full_name': client.full_name,
            'first_name': client.first_name,
            'last_name': client.last_name,
            'email': client.email,
            'phone': client.phone,
            'address': client.address,
            'city': client.city,
            'state': client.state,
            'zip_code': client.zip_code,
        }

    def get_case(self, obj):
        """Return case details if applicable"""
        case = obj.get('case')
        if not case:
            return None

        return {
            'id': case.id,
            'case_number': case.case_number,
            'case_title': case.case_title,
            'case_status': case.case_status,
            'opened_date': case.opened_date,
            'closed_date': case.closed_date,
        }
