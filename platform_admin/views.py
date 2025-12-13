"""
Platform Admin views - Admin dashboard and management
"""
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
def admin_dashboard(request):
    """Admin platform overview dashboard."""
    # Statistics
    total_users = User.objects.count()
    total_customers = User.objects.filter(role=User.ROLE_CUSTOMER).count()
    total_farmers = User.objects.filter(role=User.ROLE_FARMER).count()
    total_agencies = User.objects.filter(role=User.ROLE_AGENCY).count()
    total_orders = Order.objects.count()
    
    # Revenue
    total_revenue = Order.objects.aggregate(total=Sum('total_amount'))['total'] or 0
    
    # Today's stats
    today = timezone.now().date()
    today_orders = Order.objects.filter(created_at__date=today).count()
    active_agencies = DeliveryAgency.objects.filter(status=DeliveryAgency.STATUS_VERIFIED).count()
    
    # Recent orders
    recent_orders = Order.objects.order_by('-created_at')[:10]
    
    # Revenue chart data (last 7 days)
    revenue_data = []
    for i in range(6, -1, -1):
        date = timezone.now() - timedelta(days=i)
        day_revenue = Order.objects.filter(
            created_at__date=date.date()
        ).aggregate(total=Sum('total_amount'))['total'] or 0
        revenue_data.append({
            'date': date.strftime('%Y-%m-%d'),
            'revenue': float(day_revenue)
        })
    
    context = {
        'total_users': total_users,
        'total_customers': total_customers,
        'total_farmers': total_farmers,
        'total_agencies': total_agencies,
        'total_orders': total_orders,
        'total_revenue': total_revenue,
        'today_orders': today_orders,
        'active_agencies': active_agencies,
        'recent_orders': recent_orders,
        'revenue_data': revenue_data,
    }
    
    return render(request, 'platform_admin/admin_dashboard.html', context)


@admin_required
def admin_users(request):
    """User management page."""
    users = User.objects.all()
    
    # Role filter
    role_filter = request.GET.get('role', '')
    if role_filter:
        users = users.filter(role=role_filter)
    
    users = users.order_by('-date_joined')
    
    context = {
        'users': users,
        'role_filter': role_filter,
    }
    
    return render(request, 'platform_admin/admin_users.html', context)


@admin_required
def admin_agencies(request):
    """Delivery agency management page."""
    agencies = DeliveryAgency.objects.all().order_by('-created_at')
    
    context = {
        'agencies': agencies,
    }
    
    return render(request, 'platform_admin/admin_agencies.html', context)


@admin_required
def admin_agency_new(request):
    """Create new delivery agency."""
    if request.method == 'POST':
        email = request.POST.get('email')
        agency_name = request.POST.get('name')  # Form field name is 'name', maps to agency_name
        phone_number = request.POST.get('phone')
        address = request.POST.get('address', '')
        coverage_area_id = request.POST.get('coverage_area')  # Single selection
        license_number = request.POST.get('license_number')
        
        if User.objects.filter(email=email).exists() or DeliveryAgency.objects.filter(email=email).exists():
            messages.error(request, "Email already exists.")
            coverage_areas = CoverageArea.objects.all()
            return render(request, 'platform_admin/admin_agency_form.html', {'coverage_areas': coverage_areas})
        
        if not coverage_area_id:
            messages.error(request, "Please select a coverage area.")
            coverage_areas = CoverageArea.objects.all()
            return render(request, 'platform_admin/admin_agency_form.html', {'coverage_areas': coverage_areas})
        
        try:
            # Generate random password
            password = generate_password()
            
            # Create user account
            user = User.objects.create_user(
                username=email,
                email=email,
                password=password,
                role=User.ROLE_AGENCY
            )
            
            # Get coverage area
            coverage_area = CoverageArea.objects.get(id=coverage_area_id)
            
            # Create agency profile with all required fields
            agency = DeliveryAgency.objects.create(
                account=user,  # account refers to User
                email=email,
                agency_name=agency_name,
                phone_number=phone_number or None,
                address=address or None,
                coverage_area=coverage_area,
                license_number=license_number,
                status=DeliveryAgency.STATUS_PENDING
            )
            
            # Send credentials email (in production, use proper email backend)
            try:
                send_mail(
                    subject='Terrabia - Your Delivery Agency Account',
                    message=f'Your account has been created.\n\nEmail: {email}\nPassword: {password}\n\nPlease change your password after first login.',
                    from_email=settings.DEFAULT_FROM_EMAIL if hasattr(settings, 'DEFAULT_FROM_EMAIL') else 'noreply@terrabia.com',
                    recipient_list=[email],
                    fail_silently=True,
                )
            except:
                pass  # Email sending might fail in development
            
            messages.success(request, f"Agency created successfully! Credentials sent to {email}")
            messages.info(request, f"Generated password: {password} (also sent via email)")
            return redirect('platform_admin:agencies')
        except Exception as e:
            messages.error(request, f"Error creating agency: {str(e)}")
    
    coverage_areas = CoverageArea.objects.all()
    return render(request, 'platform_admin/admin_agency_form.html', {'coverage_areas': coverage_areas})


@admin_required
def admin_agency_verify(request, agency_id):
    """Verify a delivery agency."""
    agency = get_object_or_404(DeliveryAgency, id=agency_id)
    agency.status = DeliveryAgency.STATUS_VERIFIED
    agency.save()
    messages.success(request, f"Agency {agency.name} verified successfully!")
    return redirect('platform_admin:agencies')


@admin_required
def admin_agency_reject(request, agency_id):
    """Reject a delivery agency."""
    agency = get_object_or_404(DeliveryAgency, id=agency_id)
    agency.status = DeliveryAgency.STATUS_REJECTED
    agency.save()
    messages.success(request, f"Agency {agency.name} rejected.")
    return redirect('platform_admin:agencies')


@admin_required
def admin_agency_resend_credentials(request, agency_id):
    """Resend credentials to agency."""
    agency = get_object_or_404(DeliveryAgency, id=agency_id)
    
    # Generate new password
    new_password = generate_password()
    agency.account.set_password(new_password)
    agency.account.save()
    
    # Send email
    try:
        send_mail(
            subject='Terrabia - Your Updated Credentials',
            message=f'Your password has been reset.\n\nEmail: {agency.email}\nNew Password: {new_password}\n\nPlease change your password after first login.',
            from_email=settings.DEFAULT_FROM_EMAIL if hasattr(settings, 'DEFAULT_FROM_EMAIL') else 'noreply@terrabia.com',
            recipient_list=[agency.email],
            fail_silently=True,
        )
        messages.success(request, f"New credentials sent to {agency.email}")
    except:
        messages.info(request, f"New password: {new_password} (email sending failed)")
    
    return redirect('platform_admin:agencies')
