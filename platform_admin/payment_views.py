from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Count, Sum, Q
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal
from accounts.models import User, DeliveryAgency
from accounts.location_models import CoverageArea
from orders.models import Order, OrderItem
from platform_admin.models import FarmerPayment, PlatformCommissionSettings
from accounts.decorators import admin_required
from accounts.views import generate_password
from django.core.mail import send_mail
from django.conf import settings


@admin_required
def admin_payments(request):
    """Payment management page - view pending and processed payments."""
    # Get payment status filter
    payment_status_filter = request.GET.get('payment_status', 'all')
    
    # Orders with pending customer payments
    orders_query = Order.objects.all()
    
    if payment_status_filter == 'pending_customer':
        orders_query = orders_query.filter(payment_status='pending')
    elif payment_status_filter == 'received_customer':
        orders_query = orders_query.filter(payment_status='received')
    elif payment_status_filter == 'pending_farmer':
        # Orders where customer paid but farmers haven't been paid
        orders_query = orders_query.filter(
            payment_status='received'
        ).exclude(
            items__payments__status=FarmerPayment.STATUS_SENT
        ).distinct()
    
    orders = orders_query.order_by('-created_at')[:50]
    
    # Calculate totals
    total_pending_customer = Order.objects.filter(payment_status='pending').count()
    total_received_customer = Order.objects.filter(payment_status='received').count()
    total_pending_farmer = Order.objects.filter(
        payment_status='received'
    ).exclude(
        items__payments__status=FarmerPayment.STATUS_SENT
    ).distinct().count()
    
    context = {
        'orders': orders,
        'payment_status_filter': payment_status_filter,
        'total_pending_customer': total_pending_customer,
        'total_received_customer': total_received_customer,
        'total_pending_farmer': total_pending_farmer,
    }
    
    return render(request, 'platform_admin/admin_payments.html', context)


@admin_required
def admin_payment_confirm(request, order_id):
    """Confirm that customer payment has been received."""
    order = get_object_or_404(Order, id=order_id)
    
    if request.method == 'POST':
        order.payment_status = 'received'
        order.payment_confirmed_at = timezone.now()
        order.payment_confirmed_by = request.user
        order.save()
        
        messages.success(request, f"Payment confirmed for order {order.code}")
        return redirect('platform_admin:payment_detail', order_id=order_id)
    
    return redirect('platform_admin:payments')


@admin_required
def admin_payment_detail(request, order_id):
    """View payment details for an order and distribute to farmers."""
    order = get_object_or_404(Order, id=order_id)
    
    # Get commission settings
    commission_settings = PlatformCommissionSettings.get_settings()
    
    # Calculate amounts for each farmer
    farmer_amounts = []
    for item in order.items.all():
        commission = commission_settings.calculate_commission(item.line_total)
        farmer_amount = item.line_total - commission
        
        # Check if payment already exists
        payment = FarmerPayment.objects.filter(order_item=item).first()
        
        farmer_amounts.append({
            'item': item,
            'line_total': item.line_total,
            'commission': commission,
            'farmer_amount': farmer_amount,
            'payment': payment,
        })
    
    # Total calculations
    total_order = order.total_amount
    total_commissions = sum(amt['commission'] for amt in farmer_amounts)
    total_farmer_payments = sum(amt['farmer_amount'] for amt in farmer_amounts)
    
    context = {
        'order': order,
        'farmer_amounts': farmer_amounts,
        'commission_settings': commission_settings,
        'total_order': total_order,
        'total_commissions': total_commissions,
        'total_farmer_payments': total_farmer_payments,
    }
    
    return render(request, 'platform_admin/admin_payment_detail.html', context)


@admin_required
def admin_payment_distribute(request, order_id):
    """Distribute payments to farmers for an order."""
    order = get_object_or_404(Order, id=order_id)
    
    if order.payment_status != 'received':
        messages.error(request, "Customer payment must be confirmed first.")
        return redirect('platform_admin:payment_detail', order_id=order_id)
    
    if request.method == 'POST':
        commission_settings = PlatformCommissionSettings.get_settings()
        
        # Process each order item
        for item in order.items.all():
            # Check if payment already exists
            payment = FarmerPayment.objects.filter(order_item=item).first()
            
            if payment and payment.status != FarmerPayment.STATUS_PENDING:
                continue  # Skip if already processed
            
            # Calculate amounts
            commission = commission_settings.calculate_commission(item.line_total)
            farmer_amount = item.line_total - commission
            
            # Get payment details from form
            payment_method = request.POST.get(f'payment_method_{item.id}', '')
            payment_reference = request.POST.get(f'payment_reference_{item.id}', '')
            notes = request.POST.get(f'notes_{item.id}', '')
            
            if payment:
                # Update existing payment
                payment.amount = farmer_amount
                payment.platform_commission = commission
                payment.mark_as_sent(payment_method, payment_reference, notes)
            else:
                # Create new payment
                payment = FarmerPayment.objects.create(
                    order=order,
                    order_item=item,
                    farmer=item.farmer,
                    amount=farmer_amount,
                    platform_commission=commission,
                    status=FarmerPayment.STATUS_SENT,
                    payment_method=payment_method,
                    payment_reference=payment_reference,
                    notes=notes,
                )
                payment.mark_as_sent(payment_method, payment_reference, notes)
        
        messages.success(request, f"Payments distributed for order {order.code}")
        return redirect('platform_admin:payment_detail', order_id=order_id)
    
    return redirect('platform_admin:payment_detail', order_id=order_id)


@admin_required
def admin_commission_settings(request):
    """Manage platform commission settings."""
    settings_obj = PlatformCommissionSettings.get_settings()
    
    if request.method == 'POST':
        settings_obj.commission_type = request.POST.get('commission_type', PlatformCommissionSettings.COMMISSION_TYPE_NONE)
        settings_obj.commission_percentage = Decimal(request.POST.get('commission_percentage', 0))
        settings_obj.commission_fixed_amount = Decimal(request.POST.get('commission_fixed_amount', 0))
        settings_obj.is_active = request.POST.get('is_active') == 'on'
        settings_obj.save()
        
        messages.success(request, "Commission settings updated successfully!")
        return redirect('platform_admin:commission_settings')
    
    context = {
        'settings': settings_obj,
    }
    
    return render(request, 'platform_admin/admin_commission_settings.html', context)

