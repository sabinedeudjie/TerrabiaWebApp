"""
Platform Admin URL configuration
"""
from django.urls import path
from . import views
from . import payment_views

app_name = 'platform_admin'

urlpatterns = [
    path('dashboard/', views.admin_dashboard, name='dashboard'),
    path('users/', views.admin_users, name='users'),
    path('agencies/', views.admin_agencies, name='agencies'),
    path('agencies/new/', views.admin_agency_new, name='agency_new'),
    path('agencies/<int:agency_id>/verify/', views.admin_agency_verify, name='agency_verify'),
    path('agencies/<int:agency_id>/reject/', views.admin_agency_reject, name='agency_reject'),
    path('agencies/<int:agency_id>/resend-credentials/', views.admin_agency_resend_credentials, name='agency_resend_credentials'),
    # Payment management
    path('payments/', payment_views.admin_payments, name='payments'),
    path('payments/<int:order_id>/', payment_views.admin_payment_detail, name='payment_detail'),
    path('payments/<int:order_id>/confirm/', payment_views.admin_payment_confirm, name='payment_confirm'),
    path('payments/<int:order_id>/distribute/', payment_views.admin_payment_distribute, name='payment_distribute'),
    path('commission-settings/', payment_views.admin_commission_settings, name='commission_settings'),
]

