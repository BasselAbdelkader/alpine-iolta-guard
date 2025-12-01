from rest_framework import serializers
from ..models import Vendor, VendorType


class VendorTypeSerializer(serializers.ModelSerializer):
    """Serializer for VendorType model"""
    
    vendors_count = serializers.SerializerMethodField()
    
    class Meta:
        model = VendorType
        fields = [
            'id', 'name', 'description', 'is_active', 
            'vendors_count', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_vendors_count(self, obj):
        """Count of vendors with this type"""
        return obj.vendor_set.count()


class VendorSerializer(serializers.ModelSerializer):
    """Complete serializer for Vendor model"""
    
    vendor_type_name = serializers.CharField(source='vendor_type.name', read_only=True)
    client_name = serializers.CharField(source='client.full_name', read_only=True)
    client_number = serializers.CharField(source='client.client_number', read_only=True)
    payment_count = serializers.SerializerMethodField()
    total_paid = serializers.SerializerMethodField()
    last_payment_date = serializers.SerializerMethodField()
    
    class Meta:
        model = Vendor
        fields = [
            'id', 'vendor_number', 'vendor_name', 'vendor_type', 'vendor_type_name',
            'contact_person', 'email', 'phone', 'address', 'city', 'state', 'zip_code',
            'tax_id', 'client', 'client_name', 'client_number', 'is_active',
            'payment_count', 'total_paid', 'last_payment_date',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'vendor_number', 'created_at', 'updated_at']
    
    def get_payment_count(self, obj):
        """Count of payments made to this vendor"""
        from apps.bank_accounts.models import BankTransaction
        return BankTransaction.objects.filter(vendor=obj).count()
    
    def get_total_paid(self, obj):
        """Total amount paid to this vendor"""
        from apps.bank_accounts.models import BankTransaction
        from django.db.models import Sum
        total = BankTransaction.objects.filter(vendor=obj).aggregate(
            total=Sum('amount')
        )['total']
        return str(total or 0)
    
    def get_last_payment_date(self, obj):
        """Date of last payment to this vendor"""
        from apps.bank_accounts.models import BankTransaction
        last_transaction = BankTransaction.objects.filter(vendor=obj).order_by('-transaction_date').first()
        return last_transaction.transaction_date if last_transaction else None
    
    def validate_vendor_name(self, value):
        """Validate vendor name is not duplicate"""
        if Vendor.objects.filter(vendor_name=value).exists():
            # Allow updates to same vendor
            if self.instance and self.instance.vendor_name == value:
                return value
            raise serializers.ValidationError("Vendor with this name already exists")
        return value
    
    def validate_email(self, value):
        """Validate email format and uniqueness if provided"""
        if value and Vendor.objects.filter(email=value).exists():
            # Allow updates to same vendor
            if self.instance and self.instance.email == value:
                return value
            raise serializers.ValidationError("Vendor with this email already exists")
        return value
    
    def validate(self, data):
        """Custom validation for vendor data"""
        # If client is specified, some fields can be auto-populated from client
        client = data.get('client')
        if client:
            # Auto-populate vendor name from client if not provided
            if not data.get('vendor_name'):
                data['vendor_name'] = client.full_name
            
            # Auto-populate contact info from client if not provided
            if not data.get('email') and client.email:
                data['email'] = client.email
            if not data.get('phone') and client.phone:
                data['phone'] = client.phone
            if not data.get('address') and client.address:
                data['address'] = client.address
                data['city'] = client.city
                data['state'] = client.state
                data['zip_code'] = client.zip_code
        
        return data


class VendorListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for vendor list views"""
    
    vendor_type_name = serializers.CharField(source='vendor_type.name', read_only=True)
    client_name = serializers.CharField(source='client.full_name', read_only=True)
    payment_count = serializers.SerializerMethodField()
    total_paid = serializers.SerializerMethodField()
    
    class Meta:
        model = Vendor
        fields = [
            'id', 'vendor_number', 'vendor_name', 'vendor_type_name',
            'contact_person', 'email', 'phone', 'client_name', 'is_active',
            'payment_count', 'total_paid', 'created_at'
        ]
    
    def get_payment_count(self, obj):
        if hasattr(obj, 'annotated_payment_count'):
            return obj.annotated_payment_count
        from apps.bank_accounts.models import BankTransaction
        return BankTransaction.objects.filter(vendor=obj).count()
    
    def get_total_paid(self, obj):
        if hasattr(obj, 'annotated_total_paid'):
            return str(obj.annotated_total_paid)
        from apps.bank_accounts.models import BankTransaction
        from django.db.models import Sum
        total = BankTransaction.objects.filter(vendor=obj).aggregate(
            total=Sum('amount')
        )['total']
        return str(total or 0)
