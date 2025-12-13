"""
Location models - Coverage areas and streets/neighborhoods for Yaoundé
"""
from django.db import models


class CoverageArea(models.Model):
    """
    Coverage area model representing different zones in Yaoundé.
    """
    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=20, unique=True)  # YAOUNDE_1, YAOUNDE_2, etc.
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Coverage Areas"
        ordering = ['code']

    def __str__(self):
        return self.name


class Street(models.Model):
    """
    Street/Neighborhood model representing specific areas within coverage zones.
    """
    name = models.CharField(max_length=100)
    coverage_area = models.ForeignKey(CoverageArea, on_delete=models.CASCADE, related_name='streets')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['name', 'coverage_area']
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.coverage_area.name})"


