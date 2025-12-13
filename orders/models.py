"""
Orders app models - Cart, Orders, and Order Items
"""
from django.db import models
from accounts.models import CustomerProfile, FarmerProfile, CoverageArea, Street
from marketplace.models import Product
import uuid


class CartItem(models.Model):
    """
    Shopping cart item model.
    Represents products added to cart by customers.
    """
    customer = models.ForeignKey(CustomerProfile, on_delete=models.CASCADE, related_name='cart_items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['customer', 'product']
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.customer.full_name} - {self.product.name} x{self.quantity}"

    @property
    def total_price(self):
        """Calculate total price for this cart item."""
        return self.product.price * self.quantity


class Order(models.Model):
    """
    Order model representing customer purchases.
    """
    STATUS_PROCESSING = "processing"
    STATUS_SHIPPED = "shipped"
    STATUS_DELIVERED = "delivered"
    STATUS_COMPLETED = "completed"
    STATUS_PENDING = "pending"
    STATUS_CANCELLED = "cancelled"

    STATUS_CHOICES = [
        (STATUS_PENDING, "Pending"),
        (STATUS_PROCESSING, "Processing"),
        (STATUS_SHIPPED, "Shipped"),
        (STATUS_DELIVERED, "Delivered"),
        (STATUS_COMPLETED, "Completed"),
        (STATUS_CANCELLED, "Cancelled"),
    ]

    customer = models.ForeignKey(CustomerProfile, on_delete=models.CASCADE, related_name='orders')
    code = models.CharField(max_length=20, unique=True, editable=False)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PROCESSING)
    # Delivery address fields
    delivery_coverage_area = models.ForeignKey(CoverageArea, on_delete=models.SET_NULL, null=True, blank=True, related_name='orders')
    delivery_street = models.ForeignKey(Street, on_delete=models.SET_NULL, null=True, blank=True, related_name='orders')
    delivery_address_details = models.TextField(blank=True, help_text="Additional delivery address details")
    # Keep old field for backward compatibility during migration
    delivery_address = models.TextField(blank=True)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2)
    
    @property
    def formatted_delivery_address(self):
        """Get formatted delivery address."""
        parts = []
        if self.delivery_street:
            parts.append(self.delivery_street.name)
        if self.delivery_coverage_area:
            parts.append(self.delivery_coverage_area.name)
        if self.delivery_address_details:
            parts.append(self.delivery_address_details)
        if parts:
            return ", ".join(parts)
        # Fallback to old field if new fields are empty
        return self.delivery_address if self.delivery_address else "Address not set"
    payment_method = models.CharField(max_length=50, blank=True)
    payment_status = models.CharField(max_length=20, default='pending', choices=[
        ('pending', 'Pending'),
        ('received', 'Received'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
    ])
    payment_confirmed_at = models.DateTimeField(null=True, blank=True, help_text="When admin confirmed payment was received")
    payment_confirmed_by = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, null=True, blank=True, related_name='confirmed_payments', help_text="Admin who confirmed the payment")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    PAYMENT_METHOD_CHOICES = [
        ('orange_money', 'Orange Money'),
        ('mtn_money', 'MTN Mobile Money'),
        ('bank_card', 'Bank Card'),
    ]

    def get_payment_method_display(self):
        """Get display name for payment method."""
        for value, display in self.PAYMENT_METHOD_CHOICES:
            if value == self.payment_method:
                return display
        return self.payment_method or 'Not specified'

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Order {self.code} - {self.customer.full_name}"

    def save(self, *args, **kwargs):
        """Generate unique order code if not set."""
        if not self.code:
            self.code = f"ORD{str(uuid.uuid4())[:8].upper()}"
        super().save(*args, **kwargs)
    
    def update_status_if_all_paid(self):
        """Update order status to completed if all farmers have received payment."""
        # Check if all order items have payment_received = True
        all_items = self.items.all()
        if all_items.exists() and all_items.filter(payment_received=False).count() == 0:
            # All farmers have received payment
            if self.status != self.STATUS_COMPLETED:
                self.status = self.STATUS_COMPLETED
                self.save(update_fields=['status'])


class OrderItem(models.Model):
    """
    Order item model representing individual products in an order.
    """
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    farmer = models.ForeignKey(FarmerProfile, on_delete=models.PROTECT)
    quantity = models.DecimalField(max_digits=10, decimal_places=2)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    line_total = models.DecimalField(max_digits=12, decimal_places=2)
    payment_received = models.BooleanField(default=False, help_text="Whether the farmer has received payment for this item")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.order.code} - {self.product.name} x{self.quantity}"

    def save(self, *args, **kwargs):
        """Calculate line_total before saving."""
        # Check if payment_received is being changed
        payment_changed = False
        if self.pk:
            try:
                old_item = OrderItem.objects.get(pk=self.pk)
                payment_changed = old_item.payment_received != self.payment_received
            except OrderItem.DoesNotExist:
                payment_changed = self.payment_received
        
        self.line_total = self.unit_price * self.quantity
        super().save(*args, **kwargs)
        
        # Check if all items in the order are paid, then update order status
        if payment_changed and self.payment_received:
            self.order.update_status_if_all_paid()
