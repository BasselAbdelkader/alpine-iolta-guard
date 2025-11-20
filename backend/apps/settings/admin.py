from django.contrib import admin
from .models import LawFirm, Setting, CheckSequence, ImportAudit, CaseNumberCounter, ImportLog, UserProfile


@admin.register(LawFirm)
class LawFirmAdmin(admin.ModelAdmin):
    list_display = ['firm_name', 'city', 'state', 'principal_attorney', 'is_active']
    list_filter = ['state', 'is_active', 'iolta_compliant']
    search_fields = ['firm_name', 'principal_attorney', 'city']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Firm Information', {
            'fields': ('firm_name', 'doing_business_as', 'is_active')
        }),
        ('Address', {
            'fields': ('address_line1', 'address_line2', 'city', 'state', 'zip_code')
        }),
        ('Contact Information', {
            'fields': ('phone', 'fax', 'email', 'website')
        }),
        ('Principal Attorney', {
            'fields': ('principal_attorney', 'attorney_bar_number', 'attorney_state')
        }),
        ('Trust Account Compliance', {
            'fields': ('trust_account_required', 'iolta_compliant', 'trust_account_certification_date')
        }),
        ('Business Information', {
            'fields': ('tax_id', 'state_registration')
        }),
        ('System Fields', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )


@admin.register(Setting)
class SettingAdmin(admin.ModelAdmin):
    list_display = ['category', 'key', 'value', 'display_order', 'is_active']
    list_filter = ['category', 'is_active']
    search_fields = ['key', 'value']
    list_editable = ['display_order', 'is_active']


@admin.register(CheckSequence)
class CheckSequenceAdmin(admin.ModelAdmin):
    list_display = ['bank_account', 'next_check_number', 'last_assigned_number', 'last_assigned_date']
    search_fields = ['bank_account__account_name']
    readonly_fields = ['last_assigned_number', 'last_assigned_date']


@admin.register(ImportAudit)
class ImportAuditAdmin(admin.ModelAdmin):
    list_display = ['import_date', 'import_type', 'status', 'clients_created', 'cases_created', 'transactions_created', 'imported_by']
    list_filter = ['import_type', 'status', 'import_date']
    search_fields = ['file_name', 'imported_by']
    readonly_fields = ['import_date', 'created_at', 'completed_at']

    fieldsets = (
        ('Import Information', {
            'fields': ('import_type', 'file_name', 'status', 'imported_by')
        }),
        ('Statistics', {
            'fields': ('total_records', 'successful_records', 'failed_records')
        }),
        ('Created Entities', {
            'fields': ('clients_created', 'cases_created', 'transactions_created', 'vendors_created')
        }),
        ('Skipped Entities', {
            'fields': ('clients_skipped', 'cases_skipped', 'vendors_skipped', 'rows_with_errors')
        }),
        ('CSV Totals', {
            'fields': ('total_clients_in_csv', 'total_cases_in_csv', 'total_transactions_in_csv', 'total_vendors_in_csv'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('import_date', 'created_at', 'completed_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(CaseNumberCounter)
class CaseNumberCounterAdmin(admin.ModelAdmin):
    list_display = ['id', 'last_number', '__str__']
    readonly_fields = ['last_number']


@admin.register(ImportLog)
class ImportLogAdmin(admin.ModelAdmin):
    list_display = ['started_at', 'import_type', 'status', 'total_created', 'created_by']
    list_filter = ['import_type', 'status', 'started_at']
    search_fields = ['filename', 'created_by__username']
    readonly_fields = ['started_at', 'created_at', 'updated_at', 'duration', 'total_created']

    fieldsets = (
        ('Import Information', {
            'fields': ('import_type', 'filename', 'status', 'created_by')
        }),
        ('Statistics', {
            'fields': ('total_rows', 'clients_created', 'clients_existing', 'cases_created', 'transactions_created', 'transactions_skipped', 'total_created')
        }),
        ('Errors and Summary', {
            'fields': ('errors', 'summary'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('started_at', 'completed_at', 'duration', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'role', 'is_active', 'permission_summary', 'created_at']
    list_filter = ['role', 'is_active', 'can_approve_transactions', 'can_reconcile', 'can_print_checks', 'can_manage_users']
    search_fields = ['user__username', 'user__first_name', 'user__last_name', 'user__email', 'employee_id']
    readonly_fields = ['created_at', 'updated_at', 'created_by', 'role_description', 'permission_summary']

    fieldsets = (
        ('User Information', {
            'fields': ('user', 'role', 'is_active')
        }),
        ('Role Description', {
            'fields': ('role_description',),
            'classes': ('collapse',)
        }),
        ('Contact Information', {
            'fields': ('phone', 'employee_id', 'department')
        }),
        ('Permissions', {
            'fields': ('can_approve_transactions', 'can_reconcile', 'can_print_checks', 'can_manage_users', 'permission_summary')
        }),
        ('Audit Information', {
            'fields': ('created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def get_queryset(self, request):
        """Optimize queries with select_related"""
        return super().get_queryset(request).select_related('user', 'created_by')