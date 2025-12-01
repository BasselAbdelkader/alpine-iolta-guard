from rest_framework import serializers
from django.contrib.auth.models import User
from apps.settings.models import ImportAudit, UserProfile


class ImportAuditSerializer(serializers.ModelSerializer):
    """Serializer for ImportAudit model"""

    class Meta:
        model = ImportAudit
        fields = [
            'id',
            'import_date',
            'import_type',
            'file_name',
            'status',
            'total_records',
            'successful_records',
            'failed_records',
            'clients_created',
            'cases_created',
            'transactions_created',
            'vendors_created',
            'clients_skipped',
            'cases_skipped',
            'vendors_skipped',
            'rows_with_errors',
            'expected_clients',
            'expected_cases',
            'expected_transactions',
            'expected_vendors',
            'total_clients_in_csv',
            'total_cases_in_csv',
            'total_transactions_in_csv',
            'total_vendors_in_csv',
            'existing_clients',
            'existing_cases',
            'existing_vendors',
            'preview_data',
            'preview_errors',
            'error_log',
            'imported_by',
            'created_at',
            'completed_at',
        ]
        read_only_fields = ['id', 'created_at']


class CSVPreviewSerializer(serializers.Serializer):
    """Serializer for CSV preview validation"""
    csv_file = serializers.FileField(required=True)

    def validate_csv_file(self, value):
        """Validate that the uploaded file is a CSV"""
        if not value.name.endswith('.csv'):
            raise serializers.ValidationError('File must be a CSV file')

        # Check file size (max 10MB)
        if value.size > 10 * 1024 * 1024:
            raise serializers.ValidationError('CSV file must be less than 10MB')

        return value


class UserProfileSerializer(serializers.ModelSerializer):
    """Serializer for UserProfile model"""
    username = serializers.CharField(source='user.username', read_only=True)
    email = serializers.EmailField(source='user.email', read_only=True)
    first_name = serializers.CharField(source='user.first_name', read_only=True)
    last_name = serializers.CharField(source='user.last_name', read_only=True)
    full_name = serializers.SerializerMethodField()
    role_display = serializers.CharField(source='get_role_display', read_only=True)
    role_description = serializers.CharField(read_only=True)
    permission_summary = serializers.CharField(read_only=True)
    created_by_username = serializers.CharField(source='created_by.username', read_only=True, allow_null=True)

    class Meta:
        model = UserProfile
        fields = [
            'id',
            'user',
            'username',
            'email',
            'first_name',
            'last_name',
            'full_name',
            'role',
            'role_display',
            'role_description',
            'phone',
            'employee_id',
            'department',
            'is_active',
            'can_approve_transactions',
            'can_reconcile',
            'can_print_checks',
            'can_manage_users',
            'permission_summary',
            'created_by',
            'created_by_username',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'user', 'created_at', 'updated_at', 'created_by']

    def get_full_name(self, obj):
        """Get user's full name"""
        return obj.user.get_full_name() or obj.user.username


class UserCreateSerializer(serializers.Serializer):
    """Serializer for creating new users with profiles"""
    username = serializers.CharField(max_length=150)
    email = serializers.EmailField()
    first_name = serializers.CharField(max_length=150, required=False, allow_blank=True)
    last_name = serializers.CharField(max_length=150, required=False, allow_blank=True)
    password = serializers.CharField(write_only=True, min_length=8)
    role = serializers.ChoiceField(choices=UserProfile.ROLE_CHOICES)
    phone = serializers.CharField(max_length=20, required=False, allow_blank=True)
    employee_id = serializers.CharField(max_length=50, required=False, allow_blank=True)
    department = serializers.CharField(max_length=100, required=False, allow_blank=True)
    is_active = serializers.BooleanField(default=True)

    def validate_username(self, value):
        """Check if username already exists"""
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError('A user with this username already exists.')
        return value

    def validate_email(self, value):
        """Check if email already exists"""
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError('A user with this email already exists.')
        return value

    def create(self, validated_data):
        """Create user and profile"""
        # Extract profile data
        role = validated_data.pop('role')
        phone = validated_data.pop('phone', '')
        employee_id = validated_data.pop('employee_id', '')
        department = validated_data.pop('department', '')
        is_active = validated_data.pop('is_active', True)

        # Create user
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
            is_active=is_active
        )

        # Get or create profile (should be auto-created by signal)
        profile, created = UserProfile.objects.get_or_create(user=user)

        # Update profile with additional info
        profile.role = role
        profile.phone = phone
        profile.employee_id = employee_id
        profile.department = department
        profile.is_active = is_active

        # Set created_by if available in context
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            profile.created_by = request.user

        profile.save()

        return profile


class UserUpdateSerializer(serializers.Serializer):
    """Serializer for updating existing users"""
    email = serializers.EmailField(required=False)
    first_name = serializers.CharField(max_length=150, required=False, allow_blank=True)
    last_name = serializers.CharField(max_length=150, required=False, allow_blank=True)
    role = serializers.ChoiceField(choices=UserProfile.ROLE_CHOICES, required=False)
    phone = serializers.CharField(max_length=20, required=False, allow_blank=True)
    employee_id = serializers.CharField(max_length=50, required=False, allow_blank=True)
    department = serializers.CharField(max_length=100, required=False, allow_blank=True)
    is_active = serializers.BooleanField(required=False)
    password = serializers.CharField(write_only=True, min_length=8, required=False)

    def update(self, instance, validated_data):
        """Update user and profile"""
        user = instance.user

        # Update user fields
        if 'email' in validated_data:
            user.email = validated_data['email']
        if 'first_name' in validated_data:
            user.first_name = validated_data['first_name']
        if 'last_name' in validated_data:
            user.last_name = validated_data['last_name']
        if 'password' in validated_data:
            user.set_password(validated_data['password'])
        if 'is_active' in validated_data:
            user.is_active = validated_data['is_active']
        user.save()

        # Update profile fields
        if 'role' in validated_data:
            instance.role = validated_data['role']
        if 'phone' in validated_data:
            instance.phone = validated_data['phone']
        if 'employee_id' in validated_data:
            instance.employee_id = validated_data['employee_id']
        if 'department' in validated_data:
            instance.department = validated_data['department']
        if 'is_active' in validated_data:
            instance.is_active = validated_data['is_active']

        instance.save()

        return instance
