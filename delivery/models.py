"""
Delivery app models - Delivery tracking
"""
from django.db import models
from accounts.models import DeliveryAgency
from orders.models import Order
import uuid


class Delivery(models.Model):
    """
    Delivery model tracking order deliveries by agencies.
    """
    STATUS_PENDING = "pending"
    STATUS_IN_PROGRESS = "in_progress"
    STATUS_COMPLETED = "completed"
    STATUS_CANCELLED = "cancelled"
    STATUS_NOT_DELIVERED = "not_delivered"  # When customer marks as not delivered

    STATUS_CHOICES = [
        (STATUS_PENDING, "Pending"),
        (STATUS_IN_PROGRESS, "In Progress"),
        (STATUS_COMPLETED, "Completed"),
        (STATUS_CANCELLED, "Cancelled"),
        (STATUS_NOT_DELIVERED, "Not Delivered"),
    ]

    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='delivery')
    agency = models.ForeignKey(DeliveryAgency, on_delete=models.SET_NULL, null=True, blank=True, related_name='deliveries')
    code = models.CharField(max_length=20, unique=True, editable=False)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING)
    customer_confirmed = models.BooleanField(default=False, help_text="Whether customer has confirmed delivery")
    fee = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Deliveries"
        ordering = ['-created_at']

    def __str__(self):
        return f"Delivery {self.code} - {self.order.code}"

    def save(self, *args, **kwargs):
        """Generate unique delivery code if not set."""
        if not self.code:
            self.code = f"DEL{str(uuid.uuid4())[:8].upper()}"
        super().save(*args, **kwargs)
