"""
Orders app views - Cart, checkout, and orders
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db import transaction
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from .models import CartItem, Order, OrderItem
from marketplace.models import Product
from accounts.decorators import customer_required
from accounts.models import CustomerProfile
from accounts.location_models import CoverageArea
import json


@customer_required
def cart_view(request):
    """Shopping cart view."""
    try:
        customer = request.user.customer_profile
    except CustomerProfile.DoesNotExist:
        messages.error(request, "Customer profile not found.")
        return redirect('accounts:login')
    
    cart_items = CartItem.objects.filter(customer=customer)
    
    # Calculate totals
    subtotal = sum(item.total_price for item in cart_items)
    delivery_fee = 2000  # Fixed delivery fee for now
    total = subtotal + delivery_fee
    
    context = {
        'cart_items': cart_items,
        'subtotal': subtotal,
        'delivery_fee': delivery_fee,
        'total': total,
    }
    
    return render(request, 'orders/cart.html', context)


@customer_required
@require_http_methods(["POST"])
def add_to_cart(request):
    """Add product to cart (AJAX endpoint)."""
    try:
        customer = request.user.customer_profile
    except CustomerProfile.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Customer profile not found'}, status=400)
    
    product_id = request.POST.get('product_id')
    quantity = float(request.POST.get('quantity', 1))
    
    try:
        product = Product.objects.get(id=product_id, is_active=True)
        
        if product.stock_quantity < quantity:
            return JsonResponse({'success': False, 'error': 'Insufficient stock'}, status=400)
        
        cart_item, created = CartItem.objects.get_or_create(
            customer=customer,
            product=product,
            defaults={'quantity': quantity}
        )
        
        if not created:
            cart_item.quantity += quantity
            cart_item.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Product added to cart',
            'cart_count': CartItem.objects.filter(customer=customer).count()
        })
    except Product.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Product not found'}, status=404)


@customer_required
@require_http_methods(["POST"])
def update_cart_item(request, item_id):
    """Update cart item quantity (AJAX endpoint)."""
    try:
        customer = request.user.customer_profile
        cart_item = CartItem.objects.get(id=item_id, customer=customer)
        
        quantity = float(request.POST.get('quantity', 1))
        
        if quantity <= 0:
            cart_item.delete()
            return JsonResponse({'success': True, 'message': 'Item removed from cart'})
        
        if cart_item.product.stock_quantity < quantity:
            return JsonResponse({'success': False, 'error': 'Insufficient stock'}, status=400)
        
        cart_item.quantity = quantity
        cart_item.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Cart updated',
            'item_total': float(cart_item.total_price)
        })
    except CartItem.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Cart item not found'}, status=404)


@customer_required
@require_http_methods(["POST"])
def remove_cart_item(request, item_id):
    """Remove item from cart (AJAX endpoint)."""
    try:
        customer = request.user.customer_profile
        cart_item = CartItem.objects.get(id=item_id, customer=customer)
        cart_item.delete()
        
        return JsonResponse({'success': True, 'message': 'Item removed from cart'})
    except CartItem.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Cart item not found'}, status=404)


@customer_required
def checkout(request):
    """Checkout page."""
    import json
    import os
    from datetime import datetime
    
    # #region agent log
    try:
        log_path = r'c:\Users\DRAGON FLY\OneDrive\Desktop\Terrabia Web\.cursor\debug.log'
        with open(log_path, 'a', encoding='utf-8') as f:
            f.write(json.dumps({
                'sessionId': 'debug-session',
                'runId': 'run1',
                'hypothesisId': 'B',
                'location': 'orders/views.py:123',
                'message': 'checkout entry',
                'data': {'method': request.method},
                'timestamp': int(datetime.now().timestamp() * 1000)
            }) + '\n')
    except: pass
    # #endregion
    
    try:
        customer = request.user.customer_profile
    except CustomerProfile.DoesNotExist:
        messages.error(request, "Customer profile not found.")
        return redirect('accounts:login')
    
    cart_items = CartItem.objects.filter(customer=customer)
    
    if not cart_items.exists():
        messages.warning(request, "Your cart is empty.")
        return redirect('orders:cart')
    
    # Calculate totals
    subtotal = sum(item.total_price for item in cart_items)
    delivery_fee = 2000
    total = subtotal + delivery_fee
    
    if request.method == 'POST':
        delivery_coverage_area_id = request.POST.get('delivery_coverage_area')
        delivery_street_id = request.POST.get('delivery_street')
        delivery_address_details = request.POST.get('delivery_address_details', '')
        payment_method = request.POST.get('payment_method')
        
        # #region agent log
        try:
            with open(log_path, 'a', encoding='utf-8') as f:
                f.write(json.dumps({
                    'sessionId': 'debug-session',
                    'runId': 'run1',
                    'hypothesisId': 'B',
                    'location': 'orders/views.py:150',
                    'message': 'POST data extracted',
                    'data': {'has_coverage_area': bool(delivery_coverage_area_id), 'has_street': bool(delivery_street_id), 'has_payment_method': bool(payment_method)},
                    'timestamp': int(datetime.now().timestamp() * 1000)
                }) + '\n')
        except: pass
        # #endregion
        
        if not delivery_coverage_area_id or not delivery_street_id:
            messages.error(request, "Please select both coverage area and street for delivery.")
            coverage_areas = CoverageArea.objects.all()
            from platform_admin.models import PaymentSettings
            payment_settings = PaymentSettings.get_settings()
            return render(request, 'orders/checkout.html', {
                'cart_items': cart_items,
                'subtotal': subtotal,
                'delivery_fee': delivery_fee,
                'total': total,
                'coverage_areas': coverage_areas,
                'customer_address_details': customer.address_details,
                'payment_settings': payment_settings,
            })
        
        try:
            with transaction.atomic():
                # #region agent log
                try:
                    with open(log_path, 'a', encoding='utf-8') as f:
                        f.write(json.dumps({
                            'sessionId': 'debug-session',
                            'runId': 'run1',
                            'hypothesisId': 'B',
                            'location': 'orders/views.py:164',
                            'message': 'Before order creation',
                            'data': {'cart_items_count': cart_items.count(), 'total': float(total)},
                            'timestamp': int(datetime.now().timestamp() * 1000)
                        }) + '\n')
                except: pass
                # #endregion
                
                # Create order
                order = Order.objects.create(
                    customer=customer,
                    delivery_coverage_area_id=delivery_coverage_area_id,
                    delivery_street_id=delivery_street_id,
                    delivery_address_details=delivery_address_details,
                    total_amount=total,
                    payment_method=payment_method,
                    payment_status='pending'
                )
                
                # #region agent log
                try:
                    with open(log_path, 'a', encoding='utf-8') as f:
                        f.write(json.dumps({
                            'sessionId': 'debug-session',
                            'runId': 'run1',
                            'hypothesisId': 'B',
                            'location': 'orders/views.py:180',
                            'message': 'Order created',
                            'data': {'order_id': order.id, 'order_code': order.code},
                            'timestamp': int(datetime.now().timestamp() * 1000)
                        }) + '\n')
                except: pass
                # #endregion
                
                # Create order items grouped by farmer
                for idx, cart_item in enumerate(cart_items):
                    # #region agent log
                    try:
                        with open(log_path, 'a', encoding='utf-8') as f:
                            f.write(json.dumps({
                                'sessionId': 'debug-session',
                                'runId': 'run1',
                                'hypothesisId': 'E',
                                'location': 'orders/views.py:188',
                                'message': 'Before OrderItem creation',
                                'data': {'item_idx': idx, 'product_id': cart_item.product.id, 'farmer_id': cart_item.product.farmer.id if cart_item.product.farmer else None},
                                'timestamp': int(datetime.now().timestamp() * 1000)
                            }) + '\n')
                    except: pass
                    # #endregion
                    
                    OrderItem.objects.create(
                        order=order,
                        product=cart_item.product,
                        farmer=cart_item.product.farmer,
                        quantity=cart_item.quantity,
                        unit_price=cart_item.product.price,
                    )
                    
                    # Update product stock
                    cart_item.product.stock_quantity -= cart_item.quantity
                    cart_item.product.save()
                
                # Clear cart
                cart_items.delete()
                
                # Create delivery record
                from delivery.models import Delivery
                delivery = Delivery.objects.create(
                    order=order,
                    fee=delivery_fee
                )
                
                # #region agent log
                try:
                    with open(log_path, 'a', encoding='utf-8') as f:
                        f.write(json.dumps({
                            'sessionId': 'debug-session',
                            'runId': 'run1',
                            'hypothesisId': 'B',
                            'location': 'orders/views.py:210',
                            'message': 'Checkout success',
                            'data': {'order_id': order.id, 'delivery_id': delivery.id},
                            'timestamp': int(datetime.now().timestamp() * 1000)
                        }) + '\n')
                except: pass
                # #endregion
                
                messages.success(request, f"Order placed successfully! Order code: {order.code}")
                return redirect('orders:order_detail', order_id=order.id)
        except Exception as e:
            # #region agent log
            try:
                with open(log_path, 'a', encoding='utf-8') as f:
                    f.write(json.dumps({
                        'sessionId': 'debug-session',
                        'runId': 'run1',
                        'hypothesisId': 'B',
                        'location': 'orders/views.py:220',
                        'message': 'Checkout exception',
                        'data': {'error_type': type(e).__name__, 'error_msg': str(e)},
                        'timestamp': int(datetime.now().timestamp() * 1000)
                    }) + '\n')
            except: pass
            # #endregion
            messages.error(request, f"Checkout failed: {str(e)}")
    
    coverage_areas = CoverageArea.objects.all()
    
    # Get payment settings
    from platform_admin.models import PaymentSettings
    payment_settings = PaymentSettings.get_settings()
    
    context = {
        'cart_items': cart_items,
        'subtotal': subtotal,
        'delivery_fee': delivery_fee,
        'total': total,
        'coverage_areas': coverage_areas,
        'customer_address_details': customer.address_details,
        'payment_settings': payment_settings,
    }
    
    return render(request, 'orders/checkout.html', context)


@customer_required
def order_list(request):
    """Customer order list."""
    try:
        customer = request.user.customer_profile
    except CustomerProfile.DoesNotExist:
        messages.error(request, "Customer profile not found.")
        return redirect('accounts:login')
    
    orders = Order.objects.filter(customer=customer).order_by('-created_at')
    
    return render(request, 'orders/order_list.html', {'orders': orders})


@customer_required
def order_detail(request, order_id):
    """Order detail and tracking page."""
    try:
        customer = request.user.customer_profile
    except CustomerProfile.DoesNotExist:
        messages.error(request, "Customer profile not found.")
        return redirect('accounts:login')
    
    order = get_object_or_404(Order, id=order_id, customer=customer)
    
    # Get delivery info if exists
    delivery = None
    try:
        delivery = order.delivery
    except:
        pass
    
    # Get payment settings for display
    from platform_admin.models import PaymentSettings
    payment_settings = PaymentSettings.get_settings()
    
    # Status timeline
    status_timeline = [
        ('Placed', order.status in [Order.STATUS_PENDING, Order.STATUS_PROCESSING, Order.STATUS_SHIPPED, Order.STATUS_DELIVERED, Order.STATUS_COMPLETED]),
        ('Processing', order.status in [Order.STATUS_PROCESSING, Order.STATUS_SHIPPED, Order.STATUS_DELIVERED, Order.STATUS_COMPLETED]),
        ('Shipped', order.status in [Order.STATUS_SHIPPED, Order.STATUS_DELIVERED, Order.STATUS_COMPLETED]),
        ('Delivered', order.status in [Order.STATUS_DELIVERED, Order.STATUS_COMPLETED]),
        ('Completed', order.status == Order.STATUS_COMPLETED),
    ]
    
    context = {
        'order': order,
        'delivery': delivery,
        'status_timeline': status_timeline,
        'payment_settings': payment_settings,
    }
    
    return render(request, 'orders/order_detail.html', context)


@customer_required
def customer_confirm_delivery(request, order_id):
    """Customer confirms or rejects delivery."""
    try:
        customer = request.user.customer_profile
    except CustomerProfile.DoesNotExist:
        messages.error(request, "Customer profile not found.")
        return redirect('accounts:login')
    
    order = get_object_or_404(Order, id=order_id, customer=customer)
    
    # Get delivery
    try:
        delivery = order.delivery
    except:
        messages.error(request, "Delivery not found for this order.")
        return redirect('orders:order_detail', order_id=order_id)
    
    if request.method == 'POST':
        action = request.POST.get('action')  # 'confirm' or 'reject'
        
        if action == 'confirm':
            delivery.status = delivery.STATUS_COMPLETED
            delivery.customer_confirmed = True
            delivery.save()
            
            # Update order status to delivered if delivery is confirmed
            if order.status != order.STATUS_DELIVERED and order.status != order.STATUS_COMPLETED:
                order.status = order.STATUS_DELIVERED
                order.save()
            
            messages.success(request, "Delivery confirmed successfully! Your order has been marked as delivered.")
        elif action == 'reject':
            delivery.status = delivery.STATUS_NOT_DELIVERED
            delivery.customer_confirmed = False
            delivery.save()
            messages.warning(request, "Delivery marked as not delivered. Please contact the delivery agency to resolve this issue.")
        else:
            messages.error(request, "Invalid action.")
        
        return redirect('orders:order_detail', order_id=order_id)
    
    return redirect('orders:order_detail', order_id=order_id)
