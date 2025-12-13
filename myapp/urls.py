"""
URL configuration for myapp project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('django-admin/', admin.site.urls),  # Django admin (changed to avoid conflict)
    path('', include('accounts.urls')),  # Landing, auth, and location API
    path('customer/', include('orders.customer_urls')),  # Customer routes
    path('farmer/', include('marketplace.farmer_urls')),  # Farmer routes
    path('agency/', include('delivery.urls')),  # Delivery agency routes
    path('platform-admin/', include('platform_admin.urls')),  # Platform admin routes (not Django admin)
    path('marketplace/', include('marketplace.urls')),  # Marketplace (products)
    path('orders/', include('orders.urls')),  # Orders and cart
    path('messages/', include('messaging.urls')),  # Messaging
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
