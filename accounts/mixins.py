"""
Mixin classes for role-based access control in class-based views
"""
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied


class RoleRequiredMixin(LoginRequiredMixin):
    """
    Mixin to restrict access to class-based views based on user role.
    
    Usage:
        class MyView(RoleRequiredMixin, View):
            allowed_roles = ['customer', 'farmer']
    """
    allowed_roles = []

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        
        if request.user.role not in self.allowed_roles:
            raise PermissionDenied("You don't have permission to access this page.")
        
        return super().dispatch(request, *args, **kwargs)


class CustomerRequiredMixin(RoleRequiredMixin):
    """Mixin for customer-only views."""
    allowed_roles = ['customer']


class FarmerRequiredMixin(RoleRequiredMixin):
    """Mixin for farmer-only views."""
    allowed_roles = ['farmer']


class AdminRequiredMixin(RoleRequiredMixin):
    """Mixin for admin-only views."""
    allowed_roles = ['admin']


class AgencyRequiredMixin(RoleRequiredMixin):
    """Mixin for delivery agency-only views."""
    allowed_roles = ['delivery_agency']



