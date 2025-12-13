"""
Customer URLs
"""
from django.urls import path
from . import customer_views

app_name = 'customer'

urlpatterns = [
    path('home/', customer_views.customer_home, name='home'),
    path('cart/', customer_views.cart_view, name='cart'),
    path('checkout/', customer_views.checkout, name='checkout'),
    path('orders/', customer_views.order_list, name='orders'),
    path('orders/<int:order_id>/', customer_views.order_detail, name='order_detail'),
    path('profile/', customer_views.customer_profile, name='profile'),
    path('profile/edit/', customer_views.customer_profile_edit, name='profile_edit'),
    path('profile/change-password/', customer_views.customer_change_password, name='change_password'),
]

