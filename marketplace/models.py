"""
Marketplace app models - Products and Categories
"""
from django.db import models
from accounts.models import FarmerProfile
from accounts.location_models import CoverageArea, Street


class Category(models.Model):
    """
    Product category model.
    Used to organize products in the marketplace.
    """
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Categories"
        ordering = ['name']

    def __str__(self):
        return self.name


class Product(models.Model):
    """
    Product model representing items sold by farmers.
    """
    farmer = models.ForeignKey(FarmerProfile, on_delete=models.CASCADE, related_name='products')
    name = models.CharField(max_length=120)
    description = models.TextField(blank=True)
    category = models.ForeignKey(Category, on_delete=models.PROTECT)  # Required - products must have a category
    price = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=10, default="FCFA")
    unit = models.CharField(max_length=20)  # kg, piece, etc.
    stock_quantity = models.DecimalField(max_digits=10, decimal_places=2)
    stock_unit = models.CharField(max_length=20)  # kg, piece, etc.
    # Location - use coverage area and street
    location_coverage_area = models.ForeignKey(CoverageArea, on_delete=models.SET_NULL, null=True, blank=True, related_name='products')
    location_street = models.ForeignKey(Street, on_delete=models.SET_NULL, null=True, blank=True, related_name='products')
    # Keep old location field for backward compatibility
    location = models.CharField(max_length=255, blank=True, help_text="Legacy field - use location_coverage_area and location_street instead")
    rating = models.FloatField(null=True, blank=True, default=0.0)
    image = models.ImageField(upload_to='products/', blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} - {self.farmer.farm_name}"

    @property
    def is_in_stock(self):
        """Check if product has stock available."""
        return self.stock_quantity > 0
