"""
Admin configuration for orders app
"""
from django.contrib import admin
from .models import CartItem, Order, OrderItem


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    """Cart Item admin."""
    list_display = ['customer', 'product', 'quantity', 'created_at']
    list_filter = ['created_at']


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    """Order admin."""
    list_display = ['code', 'customer', 'status', 'total_amount', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['code', 'customer__full_name']


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    """Order Item admin."""
    list_display = ['order', 'product', 'farmer', 'quantity', 'line_total']
    list_filter = ['order__status']
