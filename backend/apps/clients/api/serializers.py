from rest_framework import serializers
import re
from ..models import Client, Case


class ClientSerializer(serializers.ModelSerializer):
    """Serializer for Client model with calculated fields"""

    current_balance = serializers.SerializerMethodField()
    formatted_balance = serializers.SerializerMethodField()
    trust_status_display = serializers.CharField(source='get_trust_account_status_display', read_only=True)
    calculated_trust_status = serializers.SerializerMethodField()
    calculated_trust_status_display = serializers.SerializerMethodField()
    last_transaction_date = serializers.SerializerMethodField()
    balance_status_class = serializers.SerializerMethodField()
    full_name = serializers.CharField(read_only=True)

    class Meta:
        model = Client
        fields = [
            'full_name',
            'id', 'client_number', 'client_name',
            'email', 'phone', 'address', 'city', 'state', 'zip_code',
            'trust_account_status', 'trust_status_display',
            'calculated_trust_status', 'calculated_trust_status_display',
            'current_balance', 'formatted_balance', 'balance_status_class',
            'last_transaction_date', 'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'client_number', 'created_at', 'updated_at', 'full_name']

    def get_current_balance(self, obj):
        """Get current balance as decimal"""
        return obj.get_current_balance()

    def get_formatted_balance(self, obj):
        """Get professionally formatted balance"""
        return obj.get_formatted_balance()

    def get_calculated_trust_status(self, obj):
        """Get calculated trust status"""
        return obj.calculate_trust_account_status()

    def get_calculated_trust_status_display(self, obj):
        """Get calculated trust status display"""
        return obj.get_calculated_trust_account_status_display()

    def get_last_transaction_date(self, obj):
        """Get last transaction date"""
        return obj.get_last_transaction_date()

    def get_balance_status_class(self, obj):
        """Get CSS class for balance status"""
        return obj.get_balance_status_class()

    def validate_client_name(self, value):
        """BUG #5 FIX: Validate first name contains only letters, hyphens, apostrophes, and periods"""
        if value:
            # Allow letters (any language), hyphens, apostrophes, periods, and spaces
            if not re.match(r"^[a-zA-Z\s\-'.]+$", value):
                raise serializers.ValidationError(
                    "First name can only contain letters, spaces, hyphens (-), apostrophes ('), and periods (.)."
                )
        return value


    def validate_zip_code(self, value):
        """BUG #1 FIX: Validate zip code format (US 5-digit or 5+4 format)"""
        if value:
            # Allow 5-digit or 5+4 format (12345 or 12345-6789)
            if not re.match(r'^\d{5}(-\d{4})?$', value):
                raise serializers.ValidationError(
                    "Invalid zip code format. Please enter a valid US zip code (e.g., 12345 or 12345-6789)."
                )
        return value

    def validate(self, data):
        """Custom validation for client data"""
        errors = {}

        # Check for duplicate client_name (excluding current instance for updates)
        client_name = data.get("client_name", self.instance.client_name if self.instance else None)

        if client_name:
            queryset = Client.objects.filter(client_name=client_name)

            # Exclude current instance during updates
            if self.instance:
                queryset = queryset.exclude(pk=self.instance.pk)

            if queryset.exists():
                errors["non_field_errors"] = ["A client with this name already exists. Please check for duplicates."]

        if errors:
            raise serializers.ValidationError(errors)

        return data


class ClientListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for client list views"""

    current_balance = serializers.SerializerMethodField()
    formatted_balance = serializers.SerializerMethodField()
    trust_status_display = serializers.CharField(source='get_trust_account_status_display', read_only=True)
    full_name = serializers.CharField(read_only=True)
    has_cases = serializers.SerializerMethodField()


    class Meta:
        model = Client
        fields = [
            'full_name',
            'id', 'client_number', 'client_name',
            'email', 'phone', 'trust_account_status', 'trust_status_display',
            'current_balance', 'formatted_balance', 'is_active', 'created_at',
            'has_cases'
        ]

    def get_current_balance(self, obj):
        # OPTIMIZATION: Use annotated balance if available (prevent N+1 queries)
        if hasattr(obj, 'annotated_balance'):
            return obj.annotated_balance
        return obj.get_current_balance()

    def get_formatted_balance(self, obj):
        # Use annotated balance if available
        if hasattr(obj, 'annotated_balance'):
            balance = obj.annotated_balance
            if balance < 0:
                return f"({abs(balance):,.2f})"
            return f"{balance:,.2f}"
        return obj.get_formatted_balance()

    def get_has_cases(self, obj):
        # Use prefetched data to avoid N+1 queries
        # Check if 'cases' relation was prefetched and has items
        if hasattr(obj, '_prefetched_objects_cache') and 'cases' in obj._prefetched_objects_cache:
            return bool(obj._prefetched_objects_cache['cases'])
        return obj.cases.exists() # Fallback, though prefetching should make this rare



class CaseSerializer(serializers.ModelSerializer):
    """Serializer for Case model with calculated fields"""

    client_name = serializers.CharField(source='client.full_name', read_only=True)
    client_number = serializers.CharField(source='client.client_number', read_only=True)
    current_balance = serializers.SerializerMethodField()
    formatted_balance = serializers.SerializerMethodField()
    balance_status_class = serializers.SerializerMethodField()
    case_status_display = serializers.CharField(source='get_case_status_display', read_only=True)

    class Meta:
        model = Case
        fields = [
            'id', 'case_number', 'case_title', 'client', 'client_name', 'client_number',
            'case_description', 'case_amount', 'case_status', 'case_status_display',
            'current_balance', 'formatted_balance', 'balance_status_class',
            'opened_date', 'closed_date', 'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'case_number', 'created_at', 'updated_at']

    def get_current_balance(self, obj):
        """Get current balance as decimal"""
        return obj.get_current_balance()

    def get_formatted_balance(self, obj):
        """Get professionally formatted balance"""
        return obj.get_formatted_balance()

    def get_balance_status_class(self, obj):
        """Get CSS class for balance status"""
        return obj.get_balance_status_class()

    def validate_client(self, value):
        """BUG #21 FIX: Ensure client is active"""
        if not value.is_active:
            raise serializers.ValidationError("Cannot create case for inactive client.")
        return value

    def validate_case_amount(self, value):
        """BUG #14 FIX: Validate case amount is greater than zero if provided"""
        if value is not None and value <= 0:
            raise serializers.ValidationError("Case amount must be greater than zero.")
        return value

    def validate(self, data):
        """Custom validation for case data"""
        from datetime import date
        errors = {}

        case_status = data.get('case_status', self.instance.case_status if self.instance else None)
        closed_date = data.get('closed_date', self.instance.closed_date if self.instance else None)
        opened_date = data.get('opened_date', self.instance.opened_date if self.instance else None)

        # BUG #17 FIX: If case status is Closed, closed_date should be provided
        if case_status == 'Closed' and not closed_date:
            errors['closed_date'] = ["Closed date is required when case status is 'Closed'."]

        # BUG #18 FIX: Validate closed date cannot be earlier than opened date
        if opened_date and closed_date and closed_date < opened_date:
            errors['closed_date'] = ["Closed date cannot be earlier than opened date."]

        # BUG #20 FIX: Validate opened date is not in the future
        if opened_date and opened_date > date.today():
            errors['opened_date'] = ["Opened date cannot be in the future."]

        if errors:
            raise serializers.ValidationError(errors)

        return data


class CaseListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for case list views"""

    client_name = serializers.CharField(source='client.full_name', read_only=True)
    client_number = serializers.CharField(source='client.client_number', read_only=True)
    current_balance = serializers.SerializerMethodField()
    formatted_balance = serializers.SerializerMethodField()

    class Meta:
        model = Case
        fields = [
            'id', 'case_number', 'case_title', 'client_name', 'client_number',
            'case_status', 'current_balance', 'formatted_balance',
            'opened_date', 'is_active', 'created_at'
        ]

    def get_current_balance(self, obj):
        # OPTIMIZATION: Use annotated balance if available (prevent N+1 queries)
        if hasattr(obj, 'annotated_balance'):
            return obj.annotated_balance
        return obj.get_current_balance()

    def get_formatted_balance(self, obj):
        # Use annotated balance if available
        if hasattr(obj, 'annotated_balance'):
            balance = obj.annotated_balance
            if balance < 0:
                return f"({abs(balance):,.2f})"
            return f"{balance:,.2f}"
        return obj.get_formatted_balance()
