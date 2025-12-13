"""
Delivery app views - Agency dashboard and delivery management
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Count, Q
from .models import Delivery
from accounts.decorators import agency_required
from accounts.models import DeliveryAgency
from accounts.location_models import CoverageArea


@agency_required
def agency_dashboard(request):
    """Delivery agency dashboard."""
    try:
        agency = request.user.agency_profile
    except DeliveryAgency.DoesNotExist:
        messages.error(request, "Agency profile not found.")
        return redirect('accounts:login')
    
    # Get deliveries for this agency
    deliveries = Delivery.objects.filter(agency=agency)
    
    # Statistics
    total_deliveries = deliveries.count()
    pending = deliveries.filter(status=Delivery.STATUS_PENDING).count()
    in_progress = deliveries.filter(status=Delivery.STATUS_IN_PROGRESS).count()
    completed = deliveries.filter(status=Delivery.STATUS_COMPLETED).count()
    
    # Recent deliveries
    recent_deliveries = deliveries.order_by('-created_at')[:10]
    
    context = {
        'agency': agency,
        'total_deliveries': total_deliveries,
        'pending': pending,
        'in_progress': in_progress,
        'completed': completed,
        'recent_deliveries': recent_deliveries,
    }
    
    return render(request, 'delivery/agency_dashboard.html', context)


@agency_required
def agency_deliveries(request):
    """List of agency deliveries with status filter."""
    try:
        agency = request.user.agency_profile
    except DeliveryAgency.DoesNotExist:
        messages.error(request, "Agency profile not found.")
        return redirect('accounts:login')
    
    deliveries = Delivery.objects.filter(agency=agency)
    
    # Status filter
    status_filter = request.GET.get('status', '')
    if status_filter:
        deliveries = deliveries.filter(status=status_filter)
    
    deliveries = deliveries.order_by('-created_at')
    
    context = {
        'deliveries': deliveries,
        'status_filter': status_filter,
    }
    
    return render(request, 'delivery/agency_deliveries.html', context)


@agency_required
def agency_delivery_detail(request, delivery_id):
    """Delivery detail page with status update."""
    try:
        agency = request.user.agency_profile
    except DeliveryAgency.DoesNotExist:
        messages.error(request, "Agency profile not found.")
        return redirect('accounts:login')
    
    delivery = get_object_or_404(Delivery, id=delivery_id, agency=agency)
    
    if request.method == 'POST':
        new_status = request.POST.get('status')
        if new_status in [Delivery.STATUS_PENDING, Delivery.STATUS_IN_PROGRESS, Delivery.STATUS_COMPLETED]:
            delivery.status = new_status
            delivery.save()
            
            # Update order status if delivery is completed
            if new_status == Delivery.STATUS_COMPLETED:
                delivery.order.status = delivery.order.STATUS_DELIVERED
                delivery.order.save()
            
            messages.success(request, "Delivery status updated successfully!")
            return redirect('agency:delivery_detail', delivery_id=delivery.id)
    
    context = {
        'delivery': delivery,
        'order': delivery.order,
    }
    
    return render(request, 'delivery/agency_delivery_detail.html', context)


@agency_required
def agency_profile(request):
    """Agency profile view."""
    try:
        agency = request.user.agency_profile
    except DeliveryAgency.DoesNotExist:
        messages.error(request, "Agency profile not found.")
        return redirect('accounts:login')
    
    return render(request, 'accounts/agency_profile.html', {'agency': agency})


@agency_required
def agency_profile_edit(request):
    """Edit agency profile."""
    try:
        agency = request.user.agency_profile
    except DeliveryAgency.DoesNotExist:
        messages.error(request, "Agency profile not found.")
        return redirect('accounts:login')
    
    if request.method == 'POST':
        agency.agency_name = request.POST.get('agency_name', agency.agency_name)
        agency.phone_number = request.POST.get('phone_number', '')
        agency.address = request.POST.get('address', '')
        agency.coverage_area_id = request.POST.get('coverage_area') or None
        agency.license_number = request.POST.get('license_number', agency.license_number)
        agency.save()
        
        # Update user email if changed (but keep username for login)
        new_email = request.POST.get('email', '')
        if new_email and new_email != request.user.email:
            # Check if email is already taken by another user
            from accounts.models import User
            if not User.objects.filter(email=new_email).exclude(id=request.user.id).exists():
                agency.email = new_email
                agency.save()
                request.user.email = new_email
                request.user.save()
            else:
                messages.error(request, "Email is already taken by another user.")
                coverage_areas = CoverageArea.objects.all()
                return render(request, 'accounts/agency_profile_edit.html', {
                    'agency': agency,
                    'coverage_areas': coverage_areas
                })
        
        messages.success(request, "Profile updated successfully!")
        return redirect('agency:profile')
    
    coverage_areas = CoverageArea.objects.all()
    return render(request, 'accounts/agency_profile_edit.html', {
        'agency': agency,
        'coverage_areas': coverage_areas
    })


@agency_required
def agency_change_password(request):
    """Change agency password."""
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
        return redirect('agency:profile')
    
    return render(request, 'accounts/change_password.html')


@agency_required
def agency_dashboard(request):
    """Delivery agency dashboard."""
    try:
        agency = request.user.agency_profile
    except DeliveryAgency.DoesNotExist:
        messages.error(request, "Agency profile not found.")
        return redirect('accounts:login')
    
    # Get deliveries for this agency
    deliveries = Delivery.objects.filter(agency=agency)
    
    # Statistics
    total_deliveries = deliveries.count()
    pending = deliveries.filter(status=Delivery.STATUS_PENDING).count()
    in_progress = deliveries.filter(status=Delivery.STATUS_IN_PROGRESS).count()
    completed = deliveries.filter(status=Delivery.STATUS_COMPLETED).count()
    
    # Recent deliveries
    recent_deliveries = deliveries.order_by('-created_at')[:10]
    
    context = {
        'agency': agency,
        'total_deliveries': total_deliveries,
        'pending': pending,
        'in_progress': in_progress,
        'completed': completed,
        'recent_deliveries': recent_deliveries,
    }
    
    return render(request, 'delivery/agency_dashboard.html', context)


@agency_required
def agency_deliveries(request):
    """List of agency deliveries with status filter."""
    try:
        agency = request.user.agency_profile
    except DeliveryAgency.DoesNotExist:
        messages.error(request, "Agency profile not found.")
        return redirect('accounts:login')
    
    deliveries = Delivery.objects.filter(agency=agency)
    
    # Status filter
    status_filter = request.GET.get('status', '')
    if status_filter:
        deliveries = deliveries.filter(status=status_filter)
    
    deliveries = deliveries.order_by('-created_at')
    
    context = {
        'deliveries': deliveries,
        'status_filter': status_filter,
    }
    
    return render(request, 'delivery/agency_deliveries.html', context)


@agency_required
def agency_delivery_detail(request, delivery_id):
    """Delivery detail page with status update."""
    try:
        agency = request.user.agency_profile
    except DeliveryAgency.DoesNotExist:
        messages.error(request, "Agency profile not found.")
        return redirect('accounts:login')
    
    delivery = get_object_or_404(Delivery, id=delivery_id, agency=agency)
    
    if request.method == 'POST':
        new_status = request.POST.get('status')
        if new_status in [Delivery.STATUS_PENDING, Delivery.STATUS_IN_PROGRESS, Delivery.STATUS_COMPLETED]:
            delivery.status = new_status
            delivery.save()
            
            # Update order status if delivery is completed
            if new_status == Delivery.STATUS_COMPLETED:
                delivery.order.status = delivery.order.STATUS_DELIVERED
                delivery.order.save()
            
            messages.success(request, "Delivery status updated successfully!")
            return redirect('agency:delivery_detail', delivery_id=delivery.id)
    
    context = {
        'delivery': delivery,
        'order': delivery.order,
    }
    
    return render(request, 'delivery/agency_delivery_detail.html', context)
