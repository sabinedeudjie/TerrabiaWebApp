from django.contrib import admin
from .models import PaymentSettings, FarmerPayment, PlatformCommissionSettings


@admin.register(PaymentSettings)
class PaymentSettingsAdmin(admin.ModelAdmin):
    """Admin interface for payment settings."""
    list_display = ('orange_money_number', 'mtn_money_number', 'is_active', 'updated_at')
    fields = ('orange_money_number', 'mtn_money_number', 'is_active')
    
    def has_add_permission(self, request):
        # Only allow one instance
        if PaymentSettings.objects.exists():
            return False
        return super().has_add_permission(request)
    
    def has_delete_permission(self, request, obj=None):
        # Prevent deletion of the only instance
        return False


@admin.register(FarmerPayment)
class FarmerPaymentAdmin(admin.ModelAdmin):
    """Admin interface for farmer payments."""
    list_display = ('id', 'order', 'farmer', 'amount', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('order__code', 'farmer__farm_name', 'payment_reference')
    readonly_fields = ('created_at', 'updated_at', 'sent_at', 'received_at')


@admin.register(PlatformCommissionSettings)
class PlatformCommissionSettingsAdmin(admin.ModelAdmin):
    """Admin interface for commission settings."""
    list_display = ('commission_type', 'commission_percentage', 'commission_fixed_amount', 'is_active', 'updated_at')
    fields = ('commission_type', 'commission_percentage', 'commission_fixed_amount', 'is_active')
    
    def has_add_permission(self, request):
        # Only allow one instance
        if PlatformCommissionSettings.objects.exists():
            return False
        return super().has_add_permission(request)
    
    def has_delete_permission(self, request, obj=None):
        # Prevent deletion of the only instance
        return False
