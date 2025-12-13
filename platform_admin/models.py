from django.db import models
from orders.models import Order, OrderItem
from accounts.models import FarmerProfile
from decimal import Decimal


class PaymentSettings(models.Model):
    """
    Platform payment settings - stores payment numbers for mobile money.
    Only one instance should exist (singleton pattern).
    """
    orange_money_number = models.CharField(
        max_length=20,
        help_text="Orange Money phone number for payments"
    )
    mtn_money_number = models.CharField(
        max_length=20,
        help_text="MTN Mobile Money phone number for payments"
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Payment Settings"
        verbose_name_plural = "Payment Settings"

    def __str__(self):
        return "Payment Settings"

    def save(self, *args, **kwargs):
        # Ensure only one instance exists
        if self.pk is None:
            # Check if any instance exists
            if PaymentSettings.objects.exists():
                # Update the existing instance instead of creating a new one
                existing = PaymentSettings.objects.first()
                existing.orange_money_number = self.orange_money_number
                existing.mtn_money_number = self.mtn_money_number
                existing.is_active = self.is_active
                return existing.save(*args, **kwargs)
        super().save(*args, **kwargs)

    @classmethod
    def get_settings(cls):
        """Get the payment settings instance, creating one if it doesn't exist."""
        settings, created = cls.objects.get_or_create(
            defaults={
                'orange_money_number': '+237 6XX XXX XXX',
                'mtn_money_number': '+237 6XX XXX XXX',
            }
        )
        return settings


class FarmerPayment(models.Model):
    """
    Tracks payments distributed to farmers.
    """
    STATUS_PENDING = "pending"
    STATUS_SENT = "sent"
    STATUS_RECEIVED = "received"
    STATUS_CANCELLED = "cancelled"

    STATUS_CHOICES = [
        (STATUS_PENDING, "Pending"),
        (STATUS_SENT, "Sent"),
        (STATUS_RECEIVED, "Received"),
        (STATUS_CANCELLED, "Cancelled"),
    ]

    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='farmer_payments')
    order_item = models.ForeignKey(OrderItem, on_delete=models.CASCADE, related_name='payments')
    farmer = models.ForeignKey(FarmerProfile, on_delete=models.CASCADE, related_name='payments')
    amount = models.DecimalField(max_digits=12, decimal_places=2, help_text="Amount to be paid to farmer")
    platform_commission = models.DecimalField(max_digits=12, decimal_places=2, default=0.00, help_text="Platform commission deducted")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING)
    payment_method = models.CharField(max_length=50, blank=True, help_text="Method used to send payment (Orange Money, MTN Money, etc.)")
    payment_reference = models.CharField(max_length=100, blank=True, help_text="Transaction reference number")
    notes = models.TextField(blank=True)
    sent_at = models.DateTimeField(null=True, blank=True)
    received_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        unique_together = ['order_item']  # One payment per order item

    def __str__(self):
        return f"Payment {self.id} - {self.farmer.farm_name} - {self.amount} FCFA"

    def mark_as_sent(self, payment_method='', payment_reference='', notes=''):
        """Mark payment as sent to farmer."""
        from django.utils import timezone
        self.status = self.STATUS_SENT
        self.payment_method = payment_method
        self.payment_reference = payment_reference
        self.notes = notes
        self.sent_at = timezone.now()
        self.save()

    def mark_as_received(self):
        """Mark payment as received by farmer."""
        from django.utils import timezone
        self.status = self.STATUS_RECEIVED
        self.received_at = timezone.now()
        self.save()
        # Also update the order item
        self.order_item.payment_received = True
        self.order_item.save()


class PlatformCommissionSettings(models.Model):
    """
    Platform commission settings - percentage or fixed amount.
    Only one instance should exist (singleton pattern).
    """
    COMMISSION_TYPE_PERCENTAGE = "percentage"
    COMMISSION_TYPE_FIXED = "fixed"
    COMMISSION_TYPE_NONE = "none"

    COMMISSION_TYPE_CHOICES = [
        (COMMISSION_TYPE_NONE, "No Commission"),
        (COMMISSION_TYPE_PERCENTAGE, "Percentage"),
        (COMMISSION_TYPE_FIXED, "Fixed Amount"),
    ]

    commission_type = models.CharField(
        max_length=20,
        choices=COMMISSION_TYPE_CHOICES,
        default=COMMISSION_TYPE_NONE
    )
    commission_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0.00,
        help_text="Commission percentage (e.g., 5.00 for 5%)"
    )
    commission_fixed_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00,
        help_text="Fixed commission amount per order"
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Commission Settings"
        verbose_name_plural = "Commission Settings"

    def __str__(self):
        return "Platform Commission Settings"

    def save(self, *args, **kwargs):
        # Ensure only one instance exists
        if self.pk is None:
            if PlatformCommissionSettings.objects.exists():
                existing = PlatformCommissionSettings.objects.first()
                existing.commission_type = self.commission_type
                existing.commission_percentage = self.commission_percentage
                existing.commission_fixed_amount = self.commission_fixed_amount
                existing.is_active = self.is_active
                return existing.save(*args, **kwargs)
        super().save(*args, **kwargs)

    @classmethod
    def get_settings(cls):
        """Get the commission settings instance, creating one if it doesn't exist."""
        settings, created = cls.objects.get_or_create(
            defaults={
                'commission_type': cls.COMMISSION_TYPE_NONE,
                'commission_percentage': 0.00,
                'commission_fixed_amount': 0.00,
            }
        )
        return settings

    def calculate_commission(self, order_item_total):
        """Calculate commission for an order item total."""
        if not self.is_active or self.commission_type == self.COMMISSION_TYPE_NONE:
            return Decimal('0.00')
        
        if self.commission_type == self.COMMISSION_TYPE_PERCENTAGE:
            return (order_item_total * self.commission_percentage) / Decimal('100.00')
        elif self.commission_type == self.COMMISSION_TYPE_FIXED:
            return self.commission_fixed_amount
        
        return Decimal('0.00')
