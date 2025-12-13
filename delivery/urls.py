"""
Delivery app URL configuration
"""
from django.urls import path
from . import views

app_name = 'agency'

urlpatterns = [
    path('dashboard/', views.agency_dashboard, name='dashboard'),
    path('deliveries/', views.agency_deliveries, name='deliveries'),
    path('deliveries/<int:delivery_id>/', views.agency_delivery_detail, name='delivery_detail'),
    path('profile/', views.agency_profile, name='profile'),
    path('profile/edit/', views.agency_profile_edit, name='profile_edit'),
    path('profile/change-password/', views.agency_change_password, name='change_password'),
]

