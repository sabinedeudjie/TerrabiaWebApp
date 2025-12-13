"""
Admin configuration for accounts app
"""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib import messages
from django.utils.html import format_html
from .models import User, CustomerProfile, FarmerProfile, DeliveryAgency
from .location_models import CoverageArea, Street
from accounts.views import generate_password


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Custom User admin."""
    list_display = ['username', 'email', 'role', 'is_staff', 'date_joined']
    list_filter = ['role', 'is_staff', 'is_superuser']
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Role', {'fields': ('role',)}),
    )


@admin.register(CustomerProfile)
class CustomerProfileAdmin(admin.ModelAdmin):
    """Customer Profile admin."""
    list_display = ['full_name', 'user', 'phone', 'street', 'created_at']
    search_fields = ['full_name', 'user__email', 'phone']
    list_filter = ['street__coverage_area']


@admin.register(FarmerProfile)
class FarmerProfileAdmin(admin.ModelAdmin):
    """Farmer Profile admin."""
    list_display = ['farm_name', 'contact_person', 'user', 'phone', 'street', 'created_at']
    search_fields = ['farm_name', 'contact_person', 'user__email', 'phone']
    list_filter = ['street__coverage_area']


@admin.register(DeliveryAgency)
class DeliveryAgencyAdmin(admin.ModelAdmin):
    """Delivery Agency admin."""
    list_display = ['agency_name', 'email', 'phone_number', 'coverage_area', 'status', 'member_since']
    list_filter = ['status', 'coverage_area']
    search_fields = ['agency_name', 'email', 'phone_number', 'license_number', 'address']
    fieldsets = (
        ('Account Information', {
            'fields': ('account', 'email')
        }),
        ('Basic Information', {
            'fields': ('agency_name', 'phone_number', 'address')
        }),
        ('Coverage & License', {
            'fields': ('coverage_area', 'license_number')
        }),
        ('Status', {
            'fields': ('status', 'member_since', 'created_at', 'updated_at')
        }),
    )
    readonly_fields = ['member_since', 'created_at', 'updated_at']
    
    def get_fieldsets(self, request, obj=None):
        """Customize fieldsets to hide account field when creating."""
        fieldsets = list(super().get_fieldsets(request, obj))
        if obj is None:  # Creating a new agency
            # Remove account from Account Information section
            for fieldset in fieldsets:
                if fieldset[0] == 'Account Information':
                    fields = list(fieldset[1]['fields'])
                    if 'account' in fields:
                        fields.remove('account')
                    fieldset[1]['fields'] = tuple(fields)
        return fieldsets
    
    def get_form(self, request, obj=None, **kwargs):
        """Make account field optional when creating a new agency."""
        form = super().get_form(request, obj, **kwargs)
        if obj is None:  # Creating a new agency
            # Check if account field exists before modifying it
            if 'account' in form.base_fields:
                form.base_fields['account'].required = False
                form.base_fields['account'].widget.attrs['style'] = 'display:none;'  # Hide the field
        return form
    
    def save_model(self, request, obj, form, change):
        """Override save_model to handle password generation for new agencies."""
        if not change:  # Creating a new agency
            # Check if account already exists (use hasattr to avoid RelatedObjectDoesNotExist)
            has_account = False
            try:
                has_account = obj.account is not None
            except User.DoesNotExist:
                has_account = False
            except:
                # If account doesn't exist yet, has_account is False
                has_account = False
            
            if not has_account:
                if not obj.email:
                    messages.error(request, "Email is required to create an agency account.")
                    return
                
                # Check if email already exists
                if User.objects.filter(email=obj.email).exists():
                    messages.error(request, f"User with email {obj.email} already exists.")
                    return
                
                # Generate random password
                password = generate_password()
                
                # Create user account
                user = User.objects.create_user(
                    username=obj.email,
                    email=obj.email,
                    password=password,
                    role=User.ROLE_AGENCY
                )
                obj.account = user
                
                # Save the agency
                super().save_model(request, obj, form, change)
                
                # Display password in success message
                messages.success(
                    request,
                    format_html(
                        '<strong>Agency created successfully!</strong><br>'
                        '<strong>Email:</strong> {}<br>'
                        '<strong>Generated Password:</strong> <code style="background: #f0f0f0; padding: 2px 6px; border-radius: 3px; font-weight: bold; color: #d63384;">{}</code><br>'
                        '<small style="color: #666;">Please save this password. The agency will need it to log in at /auth/login/</small>',
                        obj.email,
                        password
                    )
                )
            else:
                # Account already exists, just save
                super().save_model(request, obj, form, change)
        else:
            # Updating existing agency
            super().save_model(request, obj, form, change)


@admin.register(CoverageArea)
class CoverageAreaAdmin(admin.ModelAdmin):
    """Coverage Area admin."""
    list_display = ['name', 'code', 'created_at']
    search_fields = ['name', 'code']


@admin.register(Street)
class StreetAdmin(admin.ModelAdmin):
    """Street admin."""
    list_display = ['name', 'coverage_area', 'created_at']
    list_filter = ['coverage_area']
    search_fields = ['name']
