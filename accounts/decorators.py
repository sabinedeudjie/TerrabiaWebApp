"""
Decorators and mixins for role-based access control
"""
from functools import wraps
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied


def role_required(*allowed_roles):
    """
    Decorator to restrict access to views based on user role.
    
    Usage:
        @role_required('customer')
        def customer_view(request):
            ...
    """
    def decorator(view_func):
        @wraps(view_func)
        @login_required
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('login')
            
            if request.user.role not in allowed_roles:
                raise PermissionDenied("You don't have permission to access this page.")
            
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator


# Convenience decorators for each role
def customer_required(view_func):
    """Decorator to restrict access to customers only."""
    return role_required('customer')(view_func)


def farmer_required(view_func):
    """Decorator to restrict access to farmers only."""
    return role_required('farmer')(view_func)


def admin_required(view_func):
    """Decorator to restrict access to administrators only."""
    return role_required('admin')(view_func)


def agency_required(view_func):
    """Decorator to restrict access to delivery agencies only."""
    return role_required('delivery_agency')(view_func)


