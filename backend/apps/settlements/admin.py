from django.contrib import admin
from .models import Settlement, SettlementDistribution, SettlementReconciliation


class SettlementDistributionInline(admin.TabularInline):
    model = SettlementDistribution
    extra = 1
    fields = ('distribution_type', 'vendor', 'client', 'amount', 'description', 'reference_number', 'is_paid')
    readonly_fields = ('created_at', 'updated_at')


class SettlementReconciliationInline(admin.StackedInline):
    model = SettlementReconciliation
    extra = 0
    fields = (
        'reconciliation_status', 'bank_balance_before', 'bank_balance_after',
        'client_balance_before', 'client_balance_after', 'total_distributions',
        'reconciled_by', 'reconciled_at', 'notes'
    )
    readonly_fields = ('reconciled_at', 'created_at', 'updated_at')


@admin.register(Settlement)
class SettlementAdmin(admin.ModelAdmin):
    list_display = (
        'settlement_number', 'settlement_date', 'client', 'case', 
        'total_amount', 'status', 'is_balanced', 'created_at'
    )
    list_filter = ('status', 'settlement_date', 'created_at')
    search_fields = ('settlement_number', 'client__first_name', 'client__last_name', 'case__case_number')
    readonly_fields = ('settlement_number', 'created_at', 'updated_at', 'is_balanced', 'remaining_balance')
    
    fieldsets = (
        ('Settlement Information', {
            'fields': ('settlement_number', 'settlement_date', 'client', 'case', 'bank_account')
        }),
        ('Financial Details', {
            'fields': ('total_amount', 'is_balanced', 'remaining_balance')
        }),
        ('Status & Notes', {
            'fields': ('status', 'notes', 'created_by')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    inlines = [SettlementDistributionInline, SettlementReconciliationInline]
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('client', 'case', 'bank_account')


@admin.register(SettlementDistribution)
class SettlementDistributionAdmin(admin.ModelAdmin):
    list_display = (
        'settlement', 'distribution_type', 'get_recipient', 'amount', 
        'reference_number', 'is_paid', 'paid_date'
    )
    list_filter = ('distribution_type', 'is_paid', 'paid_date', 'created_at')
    search_fields = (
        'settlement__settlement_number', 'vendor__vendor_name', 
        'client__first_name', 'client__last_name', 'description'
    )
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Distribution Details', {
            'fields': ('settlement', 'distribution_type', 'amount', 'description')
        }),
        ('Recipient', {
            'fields': ('vendor', 'client'),
            'description': 'Select either a vendor OR a client, not both.'
        }),
        ('Payment Information', {
            'fields': ('reference_number', 'is_paid', 'paid_date')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def get_recipient(self, obj):
        if obj.vendor:
            return f"Vendor: {obj.vendor.vendor_name}"
        elif obj.client:
            return f"Client: {obj.client.full_name}"
        return "No recipient"
    get_recipient.short_description = 'Recipient'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('settlement', 'vendor', 'client')


@admin.register(SettlementReconciliation)
class SettlementReconciliationAdmin(admin.ModelAdmin):
    list_display = (
        'settlement', 'reconciliation_status', 'is_balanced', 
        'balance_difference', 'reconciled_by', 'reconciled_at'
    )
    list_filter = ('reconciliation_status', 'reconciled_at', 'created_at')
    search_fields = ('settlement__settlement_number', 'reconciled_by', 'notes')
    readonly_fields = ('is_balanced', 'balance_difference', 'created_at', 'updated_at')
    
    fieldsets = (
        ('Settlement', {
            'fields': ('settlement',)
        }),
        ('Balance Information', {
            'fields': (
                'bank_balance_before', 'bank_balance_after',
                'client_balance_before', 'client_balance_after',
                'total_distributions'
            )
        }),
        ('Reconciliation Status', {
            'fields': (
                'reconciliation_status', 'is_balanced', 'balance_difference',
                'reconciled_by', 'reconciled_at'
            )
        }),
        ('Notes', {
            'fields': ('notes',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('settlement')