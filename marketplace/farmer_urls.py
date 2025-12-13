"""
Farmer URLs
"""
from django.urls import path
from . import farmer_views

app_name = 'farmer'

urlpatterns = [
    path('dashboard/', farmer_views.farmer_dashboard, name='dashboard'),
    path('products/', farmer_views.farmer_products, name='products'),
    path('products/new/', farmer_views.farmer_product_new, name='product_new'),
    path('products/<int:product_id>/edit/', farmer_views.farmer_product_edit, name='product_edit'),
    path('orders/', farmer_views.farmer_orders, name='orders'),
    path('orders/<int:order_id>/', farmer_views.farmer_order_detail, name='order_detail'),
    path('orders/<int:order_id>/select-delivery/', farmer_views.farmer_select_delivery_agency, name='select_delivery_agency'),
    path('orders/<int:order_id>/assign-delivery/', farmer_views.farmer_assign_delivery_agency, name='assign_delivery_agency'),
    path('orders/<int:order_id>/mark-payment-received/', farmer_views.farmer_mark_payment_received, name='mark_payment_received'),
    path('profile/', farmer_views.farmer_profile, name='profile'),
    path('profile/edit/', farmer_views.farmer_profile_edit, name='profile_edit'),
    path('profile/change-password/', farmer_views.farmer_change_password, name='change_password'),
]

