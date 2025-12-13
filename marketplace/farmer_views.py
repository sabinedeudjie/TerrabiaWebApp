"""
Farmer-specific views for product and order management
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Sum, Count, Q
from django.utils import timezone
from datetime import timedelta
from .models import Product, Category
from orders.models import Order, OrderItem
from accounts.decorators import farmer_required
from accounts.models import FarmerProfile
from accounts.location_models import CoverageArea


@farmer_required
def farmer_dashboard(request):
    """Farmer dashboard with KPIs and metrics."""
    try:
        farmer = request.user.farmer_profile
    except FarmerProfile.DoesNotExist:
        messages.error(request, "Farmer profile not found.")
        return redirect('accounts:login')
    
    # Get current month
    now = timezone.now()
    month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    
    # KPIs
    monthly_sales = OrderItem.objects.filter(
        farmer=farmer,
        order__created_at__gte=month_start
    ).aggregate(total=Sum('line_total'))['total'] or 0
    
    active_orders = Order.objects.filter(
        items__farmer=farmer,
        status__in=[Order.STATUS_PENDING, Order.STATUS_PROCESSING, Order.STATUS_SHIPPED]
    ).distinct().count()
    
    products_in_stock = Product.objects.filter(farmer=farmer, is_active=True, stock_quantity__gt=0).count()
    out_of_stock = Product.objects.filter(farmer=farmer, is_active=True, stock_quantity=0).count()
    
    # Recent orders
    recent_orders = Order.objects.filter(
        items__farmer=farmer
    ).distinct().order_by('-created_at')[:10]
    
    # Revenue chart data (last 7 days)
    revenue_data = []
    for i in range(6, -1, -1):
        date = now - timedelta(days=i)
        day_revenue = OrderItem.objects.filter(
            farmer=farmer,
            order__created_at__date=date.date()
        ).aggregate(total=Sum('line_total'))['total'] or 0
        revenue_data.append({
            'date': date.strftime('%Y-%m-%d'),
            'revenue': float(day_revenue)
        })
    
    context = {
        'farmer': farmer,
        'monthly_sales': monthly_sales,
        'active_orders': active_orders,
        'products_in_stock': products_in_stock,
        'out_of_stock': out_of_stock,
        'recent_orders': recent_orders,
        'revenue_data': revenue_data,
    }
    
    return render(request, 'marketplace/farmer_dashboard.html', context)


@farmer_required
def farmer_products(request):
    """List of farmer's products."""
    try:
        farmer = request.user.farmer_profile
    except FarmerProfile.DoesNotExist:
        messages.error(request, "Farmer profile not found.")
        return redirect('accounts:login')
    
    products = Product.objects.filter(farmer=farmer).order_by('-created_at')
    
    return render(request, 'marketplace/farmer_products.html', {'products': products})


@farmer_required
def farmer_product_new(request):
    """Create new product."""
    try:
        farmer = request.user.farmer_profile
    except FarmerProfile.DoesNotExist:
        messages.error(request, "Farmer profile not found.")
        return redirect('accounts:login')
    
    if request.method == 'POST':
        category_id = request.POST.get('category')
        if not category_id:
            messages.error(request, "Category is required. Please select a category.")
            categories = Category.objects.all()
            return render(request, 'marketplace/farmer_product_form.html', {
                'categories': categories,
                'action': 'Create'
            })
        
        try:
            product = Product.objects.create(
                farmer=farmer,
                name=request.POST.get('name'),
                description=request.POST.get('description', ''),
                category_id=category_id,
                price=float(request.POST.get('price', 0)),
                currency=request.POST.get('currency', 'FCFA'),
                unit=request.POST.get('unit', 'kg'),
                stock_quantity=float(request.POST.get('stock_quantity', 0)),
                stock_unit=request.POST.get('stock_unit', 'kg'),
            )
            # Handle image upload
            if 'image' in request.FILES:
                product.image = request.FILES['image']
                product.save()
            messages.success(request, "Product created successfully!")
            return redirect('farmer:products')
        except Exception as e:
            messages.error(request, f"Error creating product: {str(e)}")
    
    categories = Category.objects.all()
    return render(request, 'marketplace/farmer_product_form.html', {
        'categories': categories,
        'action': 'Create'
    })


@farmer_required
def farmer_product_edit(request, product_id):
    """Edit product."""
    try:
        farmer = request.user.farmer_profile
    except FarmerProfile.DoesNotExist:
        messages.error(request, "Farmer profile not found.")
        return redirect('accounts:login')
    
    product = get_object_or_404(Product, id=product_id, farmer=farmer)
    
    if request.method == 'POST':
        category_id = request.POST.get('category')
        if not category_id:
            messages.error(request, "Category is required. Please select a category.")
            categories = Category.objects.all()
            return render(request, 'marketplace/farmer_product_form.html', {
                'product': product,
                'categories': categories,
                'action': 'Edit'
            })
        
        try:
            product.name = request.POST.get('name', product.name)
            product.description = request.POST.get('description', product.description)
            product.category_id = category_id
            product.price = float(request.POST.get('price', product.price))
            product.currency = request.POST.get('currency', product.currency)
            product.unit = request.POST.get('unit', product.unit)
            product.stock_quantity = float(request.POST.get('stock_quantity', product.stock_quantity))
            product.stock_unit = request.POST.get('stock_unit', product.stock_unit)
            # Handle image upload
            if 'image' in request.FILES:
                product.image = request.FILES['image']
            product.is_active = request.POST.get('is_active') == 'on'
            product.save()
            
            messages.success(request, "Product updated successfully!")
            return redirect('farmer:products')
        except Exception as e:
            messages.error(request, f"Error updating product: {str(e)}")
    
    categories = Category.objects.all()
    return render(request, 'marketplace/farmer_product_form.html', {
        'product': product,
        'categories': categories,
        'action': 'Edit'
    })


@farmer_required
def farmer_orders(request):
    """List of farmer's orders."""
    try:
        farmer = request.user.farmer_profile
    except FarmerProfile.DoesNotExist:
        messages.error(request, "Farmer profile not found.")
        return redirect('accounts:login')
    
    orders = Order.objects.filter(
        items__farmer=farmer
    ).distinct().order_by('-created_at')
    
    # Get delivery info for each order
    orders_with_delivery = []
    for order in orders:
        delivery = None
        has_delivery_agency = False
        try:
            delivery = order.delivery
            has_delivery_agency = delivery.agency is not None if delivery else False
        except:
            pass
        
        orders_with_delivery.append({
            'order': order,
            'has_delivery_agency': has_delivery_agency,
            'delivery': delivery,
        })
    
    return render(request, 'marketplace/farmer_orders.html', {'orders_data': orders_with_delivery})


@farmer_required
def farmer_order_detail(request, order_id):
    """Farmer order detail view."""
    try:
        farmer = request.user.farmer_profile
    except FarmerProfile.DoesNotExist:
        messages.error(request, "Farmer profile not found.")
        return redirect('accounts:login')
    
    order = get_object_or_404(Order, id=order_id, items__farmer=farmer)
    
    # Get only items from this farmer
    order_items = order.items.filter(farmer=farmer)
    farmer_total = sum(item.line_total for item in order_items)
    
    # Check if all items are paid
    all_paid = all(item.payment_received for item in order_items) if order_items.exists() else False
    
    # Get delivery info
    delivery = None
    try:
        delivery = order.delivery
    except:
        pass
    
    # Get available delivery agencies that cover the customer's delivery area
    available_agencies = []
    if order.delivery_coverage_area:
        from accounts.models import DeliveryAgency
        available_agencies = DeliveryAgency.objects.filter(
            coverage_area=order.delivery_coverage_area,
            status=DeliveryAgency.STATUS_VERIFIED  # Only show verified agencies
        ).order_by('agency_name')
    
    context = {
        'order': order,
        'order_items': order_items,
        'farmer_total': farmer_total,
        'delivery': delivery,
        'available_agencies': available_agencies,
        'all_paid': all_paid,
    }
    
    return render(request, 'marketplace/farmer_order_detail.html', context)


@farmer_required
def farmer_mark_payment_received(request, order_id):
    """Farmer marks payment as received for their items in an order."""
    try:
        farmer = request.user.farmer_profile
    except FarmerProfile.DoesNotExist:
        messages.error(request, "Farmer profile not found.")
        return redirect('accounts:login')
    
    order = get_object_or_404(Order, id=order_id, items__farmer=farmer)
    
    if request.method == 'POST':
        # Get all order items for this farmer
        order_items = order.items.filter(farmer=farmer)
        
        if order_items.exists():
            # Mark all items as payment received by calling save() on each item
            # This ensures the OrderItem.save() method is called, which triggers the status update
            for item in order_items:
                if not item.payment_received:
                    item.payment_received = True
                    item.save()  # This will trigger update_status_if_all_paid() if needed
            
            # Also explicitly check and update order status after all updates
            # Refresh order from database to get latest status
            order.refresh_from_db()
            order.update_status_if_all_paid()
            
            messages.success(request, f"Payment marked as received for order {order.code}!")
            
            # Check if all farmers have received payment
            all_items = order.items.all()
            all_paid = all_items.exists() and all_items.filter(payment_received=False).count() == 0
            if all_paid:
                messages.info(request, "All farmers have received payment. Order status updated to Completed.")
        else:
            messages.error(request, "No items found for this order.")
        
        return redirect('farmer:order_detail', order_id=order_id)
    
    return redirect('farmer:order_detail', order_id=order_id)


@farmer_required
def farmer_select_delivery_agency(request, order_id):
    """View to select a delivery agency for an order."""
    try:
        farmer = request.user.farmer_profile
    except FarmerProfile.DoesNotExist:
        messages.error(request, "Farmer profile not found.")
        return redirect('accounts:login')
    
    order = get_object_or_404(Order, id=order_id, items__farmer=farmer)
    
    # Check if delivery already has an agency assigned
    delivery = None
    try:
        delivery = order.delivery
        if delivery and delivery.agency:
            messages.info(request, f"Delivery agency {delivery.agency.agency_name} is already assigned to this order.")
            return redirect('farmer:order_detail', order_id=order_id)
    except:
        pass
    
    # Get available delivery agencies that cover the customer's delivery area
    available_agencies = []
    if order.delivery_coverage_area:
        from accounts.models import DeliveryAgency
        available_agencies = DeliveryAgency.objects.filter(
            coverage_area=order.delivery_coverage_area,
            status=DeliveryAgency.STATUS_VERIFIED  # Only show verified agencies
        ).order_by('agency_name')
    else:
        messages.error(request, "Order delivery address is not set. Cannot select delivery agency.")
        return redirect('farmer:order_detail', order_id=order_id)
    
    if not available_agencies:
        messages.warning(request, f"No verified delivery agencies found for {order.delivery_coverage_area.name}.")
        return redirect('farmer:order_detail', order_id=order_id)
    
    context = {
        'order': order,
        'available_agencies': available_agencies,
        'delivery': delivery,
    }
    
    return render(request, 'marketplace/farmer_select_delivery_agency.html', context)


@farmer_required
def farmer_assign_delivery_agency(request, order_id):
    """Assign a delivery agency to an order."""
    try:
        farmer = request.user.farmer_profile
    except FarmerProfile.DoesNotExist:
        messages.error(request, "Farmer profile not found.")
        return redirect('accounts:login')
    
    if request.method != 'POST':
        return redirect('farmer:select_delivery_agency', order_id=order_id)
    
    order = get_object_or_404(Order, id=order_id, items__farmer=farmer)
    
    # Check if delivery already has an agency assigned
    delivery = None
    try:
        delivery = order.delivery
        if delivery and delivery.agency:
            messages.warning(request, f"Delivery agency {delivery.agency.agency_name} is already assigned to this order.")
            return redirect('farmer:order_detail', order_id=order_id)
    except:
        pass
    
    agency_id = request.POST.get('agency_id')
    if not agency_id:
        messages.error(request, "Please select a delivery agency.")
        return redirect('farmer:select_delivery_agency', order_id=order_id)
    
    from accounts.models import DeliveryAgency
    try:
        agency = DeliveryAgency.objects.get(
            id=agency_id,
            coverage_area=order.delivery_coverage_area,
            status=DeliveryAgency.STATUS_VERIFIED
        )
    except DeliveryAgency.DoesNotExist:
        messages.error(request, "Selected delivery agency not found or not available for this area.")
        return redirect('farmer:select_delivery_agency', order_id=order_id)
    
    # Create or update delivery
    from delivery.models import Delivery
    if not delivery:
        delivery = Delivery.objects.create(order=order, agency=agency, status=Delivery.STATUS_PENDING)
    else:
        delivery.agency = agency
        delivery.status = Delivery.STATUS_PENDING
        delivery.save()
    
    messages.success(request, f"Delivery agency {agency.agency_name} has been assigned to order {order.code}.")
    return redirect('farmer:order_detail', order_id=order_id)


@farmer_required
def farmer_profile(request):
    """Farmer profile view."""
    try:
        profile = request.user.farmer_profile
    except FarmerProfile.DoesNotExist:
        messages.error(request, "Profile not found.")
        return redirect('accounts:login')
    
    return render(request, 'accounts/farmer_profile.html', {'profile': profile})


@farmer_required
def farmer_profile_edit(request):
    """Edit farmer profile."""
    try:
        profile = request.user.farmer_profile
    except FarmerProfile.DoesNotExist:
        messages.error(request, "Profile not found.")
        return redirect('accounts:login')
    
    if request.method == 'POST':
        profile.farm_name = request.POST.get('farm_name', profile.farm_name)
        profile.contact_person = request.POST.get('contact_person', profile.contact_person)
        profile.phone = request.POST.get('phone', profile.phone)
        profile.street_id = request.POST.get('street') or None
        profile.address_details = request.POST.get('address_details', '')
        profile.save()
        
        # Update user email if changed
        new_email = request.POST.get('email', '')
        if new_email and new_email != request.user.email:
            request.user.email = new_email
            request.user.username = new_email
            request.user.save()
        
        messages.success(request, "Profile updated successfully!")
        return redirect('farmer:profile')
    
    coverage_areas = CoverageArea.objects.all()
    return render(request, 'accounts/farmer_profile_edit.html', {
        'profile': profile,
        'coverage_areas': coverage_areas
    })


@farmer_required
def farmer_change_password(request):
    """Change farmer password."""
    from django.contrib.auth import update_session_auth_hash
    
    if request.method == 'POST':
        old_password = request.POST.get('old_password')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')
        
        if not old_password or not new_password or not confirm_password:
            messages.error(request, "All fields are required.")
            return render(request, 'accounts/change_password.html')
        
        if new_password != confirm_password:
            messages.error(request, "New passwords do not match.")
            return render(request, 'accounts/change_password.html')
        
        if len(new_password) < 8:
            messages.error(request, "Password must be at least 8 characters long.")
            return render(request, 'accounts/change_password.html')
        
        # Check old password
        if not request.user.check_password(old_password):
            messages.error(request, "Current password is incorrect.")
            return render(request, 'accounts/change_password.html')
        
        # Set new password
        request.user.set_password(new_password)
        request.user.save()
        
        # Update session to prevent logout
        update_session_auth_hash(request, request.user)
        
        messages.success(request, "Password changed successfully!")
        return redirect('farmer:profile')
    
    return render(request, 'accounts/change_password.html')

