"""
Accounts app URL configuration
"""
from django.urls import path
from . import views
from . import location_views

app_name = 'accounts'

urlpatterns = [
    path('', views.landing_page, name='landing'),
    path('join/', views.join_page, name='join'),
    path('auth/register/customer/', views.register_customer, name='register_customer'),
    path('auth/register/farmer/', views.register_farmer, name='register_farmer'),
    path('auth/login/', views.login_view, name='login'),
    path('auth/logout/', views.logout_view, name='logout'),
    # API endpoints
    path('api/locations/streets/', location_views.get_streets, name='get_streets'),
]

