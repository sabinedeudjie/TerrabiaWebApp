"""
Messaging app URL configuration
"""
from django.urls import path
from . import views

app_name = 'messaging'

urlpatterns = [
    # Farmer messaging routes
    path('farmer/messages/', views.farmer_messages, name='farmer_messages'),
    path('farmer/messages/<int:thread_id>/', views.farmer_message_thread, name='farmer_thread'),
    path('farmer/messages/start/<int:agency_id>/', views.farmer_start_conversation, name='farmer_start_conversation'),
    path('farmer/agencies/', views.farmer_agencies, name='farmer_agencies'),
    
    # Agency messaging routes
    path('agency/messages/', views.agency_messages, name='agency_messages'),
    path('agency/messages/<int:thread_id>/', views.agency_message_thread, name='agency_thread'),
]

