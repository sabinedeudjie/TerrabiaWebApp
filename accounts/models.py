"""
Accounts app models - Custom User model and user profiles
"""
from django.contrib.auth.models import AbstractUser
from django.db import models
from .location_models import CoverageArea, Street


class User(AbstractUser):
    """
    Custom User model with role-based access control.
    Extends Django's AbstractUser to add role field.
    """
    ROLE_CUSTOMER = "customer"
    ROLE_FARMER = "farmer"
    ROLE_ADMIN = "admin"
    ROLE_AGENCY = "delivery_agency"

    ROLE_CHOICES = [
        (ROLE_CUSTOMER, "Customer"),
        (ROLE_FARMER, "Farmer"),
        (ROLE_ADMIN, "Administrator"),
        (ROLE_AGENCY, "Delivery agency"),
    ]

    role = models.CharField(max_length=20, choices=ROLE_CHOICES, null=True, blank=True)

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"


class CustomerProfile(models.Model):
    """
    Profile model for Customer users.
    Stores additional customer-specific information.
    Note: Customers have street but not coverage_area - coverage areas are only for delivery agencies.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='customer_profile')
    full_name = models.CharField(max_length=120)
    phone = models.CharField(max_length=30)
    street = models.ForeignKey(Street, on_delete=models.SET_NULL, null=True, blank=True, related_name='customers', help_text="Street/neighborhood where the customer is located")
    address_details = models.TextField(blank=True, help_text="Additional address details (house number, building, etc.)")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Customer: {self.full_name}"
    
    @property
    def full_address(self):
        """Get formatted full address."""
        parts = []
        if self.street:
            parts.append(self.street.name)
        if self.address_details:
            parts.append(self.address_details)
        return ", ".join(parts) if parts else "Address not set"


class FarmerProfile(models.Model):
    """
    Profile model for Farmer users.
    Stores farm and contact information.
    Note: Farmers have street but not coverage_area - coverage areas are only for delivery agencies.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='farmer_profile')
    farm_name = models.CharField(max_length=120)
    contact_person = models.CharField(max_length=120)
    phone = models.CharField(max_length=30)
    # Location fields
    street = models.ForeignKey(Street, on_delete=models.SET_NULL, null=True, blank=True, related_name='farmers', help_text="Street/neighborhood where the farm is located")
    address_details = models.TextField(blank=True, help_text="Additional address details (farm location, etc.)")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Farmer: {self.farm_name}"
    
    @property
    def full_address(self):
        """Get formatted full address."""
        parts = []
        if self.street:
            parts.append(self.street.name)
        if self.address_details:
            parts.append(self.address_details)
        return ", ".join(parts) if parts else "Address not set"


class DeliveryAgency(models.Model):
    """
    Profile model for Delivery Agency users.
    Agencies are created by administrators and cannot self-register.
    """
    STATUS_PENDING = "pending"
    STATUS_VERIFIED = "verified"
    STATUS_REJECTED = "rejected"

    STATUS_CHOICES = [
        (STATUS_PENDING, "Pending"),
        (STATUS_VERIFIED, "Verified"),
        (STATUS_REJECTED, "Rejected"),
    ]

    # account refers to the User account
    account = models.OneToOneField(User, on_delete=models.CASCADE, related_name='agency_profile', help_text="User account")
    email = models.EmailField(unique=True, help_text="Email for login")
    agency_name = models.CharField(max_length=120, help_text="Agency name")
    phone_number = models.CharField(max_length=30, blank=True, null=True, help_text="Phone number")
    address = models.TextField(blank=True, null=True, help_text="Agency address")
    # Coverage area - single area (can be extended to multiple if needed)
    coverage_area = models.ForeignKey(CoverageArea, on_delete=models.SET_NULL, null=True, blank=True, related_name='agencies', help_text="Primary coverage area")
    license_number = models.CharField(max_length=50)
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_PENDING,
    )
    member_since = models.DateTimeField(auto_now_add=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Delivery Agency"
        verbose_name_plural = "Delivery Agencies"

    def __str__(self):
        return f"Agency: {self.agency_name}"
    
    @property
    def name(self):
        """Alias for agency_name for backward compatibility."""
        return self.agency_name
    
    @property
    def user(self):
        """Alias for account for backward compatibility."""
        try:
            return self.account
        except User.DoesNotExist:
            return None
