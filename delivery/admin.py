"""
Admin configuration for delivery app
"""
from django.contrib import admin
from .models import Delivery


@admin.register(Delivery)
class DeliveryAdmin(admin.ModelAdmin):
    """Delivery admin."""
    list_display = ['code', 'order', 'agency', 'status', 'fee', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['code', 'order__code']
