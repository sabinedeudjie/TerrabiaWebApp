"""
Marketplace app URL configuration
"""
from django.urls import path
from . import views

app_name = 'marketplace'

urlpatterns = [
    path('products/', views.product_list, name='product_list'),
    path('products/<int:product_id>/', views.product_detail, name='product_detail'),
]


