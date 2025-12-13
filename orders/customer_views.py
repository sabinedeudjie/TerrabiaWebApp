"""
Customer-specific views (moved from orders for better organization)
"""
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from accounts.decorators import customer_required
from accounts.models import CustomerProfile
from orders.views import cart_view, checkout, order_list, order_detail


@customer_required
def customer_home(request):
    """Customer home page - redirects to product list."""
    return redirect('marketplace:product_list')


@customer_required
def customer_profile(request):
    """Customer profile view."""
    try:
        profile = request.user.customer_profile
    except CustomerProfile.DoesNotExist:
        messages.error(request, "Profile not found.")
        return redirect('accounts:login')
    
    return render(request, 'accounts/customer_profile.html', {'profile': profile})


@customer_required
def customer_profile_edit(request):
    """Edit customer profile."""
    try:
        profile = request.user.customer_profile
    except CustomerProfile.DoesNotExist:
        messages.error(request, "Profile not found.")
        return redirect('accounts:login')
    
    if request.method == 'POST':
        from accounts.location_models import CoverageArea
        
        profile.full_name = request.POST.get('full_name', profile.full_name)
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
        return redirect('customer:profile')
    
    from accounts.location_models import CoverageArea
    coverage_areas = CoverageArea.objects.all()
    return render(request, 'accounts/customer_profile_edit.html', {
        'profile': profile,
        'coverage_areas': coverage_areas
    })


@customer_required
def customer_change_password(request):
    """Change customer password."""
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
        return redirect('customer:profile')
    
    return render(request, 'accounts/change_password.html')
