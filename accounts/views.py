"""
Accounts app views - Authentication and user management
"""
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from .models import User, CustomerProfile, FarmerProfile
from .decorators import role_required
import secrets
import string


def landing_page(request):
    """Landing page for Terrabia."""
    return render(request, 'accounts/landing.html')


def join_page(request):
    """Role selection page."""
    return render(request, 'accounts/join.html')


def register_customer(request):
    """Customer registration view."""
    from .location_models import CoverageArea
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
                'hypothesisId': 'A',
                'location': 'accounts/views.py:25',
                'message': 'register_customer entry',
                'data': {'method': request.method, 'has_post_data': bool(request.POST)},
                'timestamp': int(datetime.now().timestamp() * 1000)
            }) + '\n')
    except: pass
    # #endregion
    
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        password_confirm = request.POST.get('password_confirm')
        full_name = request.POST.get('full_name')
        phone = request.POST.get('phone')
        zone_id = request.POST.get('zone')  # This is actually coverage_area_id, but we call it "zone" in the form
        street_id = request.POST.get('street')
        address_details = request.POST.get('address_details', '')
        
        # #region agent log
        try:
            with open(log_path, 'a', encoding='utf-8') as f:
                f.write(json.dumps({
                    'sessionId': 'debug-session',
                    'runId': 'run1',
                    'hypothesisId': 'A',
                    'location': 'accounts/views.py:38',
                    'message': 'POST data extracted',
                    'data': {'email': bool(email), 'has_password': bool(password), 'street_id': street_id, 'zone_id': zone_id},
                    'timestamp': int(datetime.now().timestamp() * 1000)
                }) + '\n')
        except: pass
        # #endregion

        # Validation
        if password != password_confirm:
            messages.error(request, "Passwords do not match.")
            coverage_areas = CoverageArea.objects.all()
            return render(request, 'accounts/register_customer.html', {'coverage_areas': coverage_areas})

        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already exists.")
            coverage_areas = CoverageArea.objects.all()
            return render(request, 'accounts/register_customer.html', {'coverage_areas': coverage_areas})

        if not street_id:
            messages.error(request, "Please select a street.")
            coverage_areas = CoverageArea.objects.all()
            return render(request, 'accounts/register_customer.html', {'coverage_areas': coverage_areas})

        try:
            with transaction.atomic():
                # #region agent log
                try:
                    with open(log_path, 'a', encoding='utf-8') as f:
                        f.write(json.dumps({
                            'sessionId': 'debug-session',
                            'runId': 'run1',
                            'hypothesisId': 'A',
                            'location': 'accounts/views.py:56',
                            'message': 'Before user creation',
                            'data': {'email': email, 'street_id': street_id},
                            'timestamp': int(datetime.now().timestamp() * 1000)
                        }) + '\n')
                except: pass
                # #endregion
                
                # Create user
                user = User.objects.create_user(
                    username=email,
                    email=email,
                    password=password,
                    role=User.ROLE_CUSTOMER
                )
                
                # #region agent log
                try:
                    with open(log_path, 'a', encoding='utf-8') as f:
                        f.write(json.dumps({
                            'sessionId': 'debug-session',
                            'runId': 'run1',
                            'hypothesisId': 'A',
                            'location': 'accounts/views.py:70',
                            'message': 'User created',
                            'data': {'user_id': user.id, 'user_role': user.role},
                            'timestamp': int(datetime.now().timestamp() * 1000)
                        }) + '\n')
                except: pass
                # #endregion
                
                # Create customer profile
                profile = CustomerProfile.objects.create(
                    user=user,
                    full_name=full_name,
                    phone=phone,
                    street_id=street_id,
                    address_details=address_details
                )
                
                # #region agent log
                try:
                    with open(log_path, 'a', encoding='utf-8') as f:
                        f.write(json.dumps({
                            'sessionId': 'debug-session',
                            'runId': 'run1',
                            'hypothesisId': 'A',
                            'location': 'accounts/views.py:85',
                            'message': 'Profile created',
                            'data': {'profile_id': profile.id, 'has_street': bool(profile.street)},
                            'timestamp': int(datetime.now().timestamp() * 1000)
                        }) + '\n')
                except: pass
                # #endregion
                
                # Auto login
                auth_user = authenticate(request, username=email, password=password)
                
                # #region agent log
                try:
                    with open(log_path, 'a', encoding='utf-8') as f:
                        f.write(json.dumps({
                            'sessionId': 'debug-session',
                            'runId': 'run1',
                            'hypothesisId': 'A',
                            'location': 'accounts/views.py:95',
                            'message': 'After authenticate',
                            'data': {'auth_success': auth_user is not None},
                            'timestamp': int(datetime.now().timestamp() * 1000)
                        }) + '\n')
                except: pass
                # #endregion
                
                if auth_user:
                    login(request, auth_user)
                    messages.success(request, "Registration successful!")
                    return redirect('customer:home')
        except Exception as e:
            # #region agent log
            try:
                with open(log_path, 'a', encoding='utf-8') as f:
                    f.write(json.dumps({
                        'sessionId': 'debug-session',
                        'runId': 'run1',
                        'hypothesisId': 'A',
                        'location': 'accounts/views.py:108',
                        'message': 'Exception caught',
                        'data': {'error_type': type(e).__name__, 'error_msg': str(e)},
                        'timestamp': int(datetime.now().timestamp() * 1000)
                    }) + '\n')
            except: pass
            # #endregion
            messages.error(request, f"Registration failed: {str(e)}")

    coverage_areas = CoverageArea.objects.all()
    return render(request, 'accounts/register_customer.html', {'coverage_areas': coverage_areas})


def register_farmer(request):
    """Farmer registration view."""
    from .location_models import CoverageArea
    
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        password_confirm = request.POST.get('password_confirm')
        farm_name = request.POST.get('farm_name')
        contact_person = request.POST.get('contact_person')
        phone = request.POST.get('phone')
        zone_id = request.POST.get('zone')  # This is actually coverage_area_id, but we call it "zone" in the form
        street_id = request.POST.get('street')
        address_details = request.POST.get('address_details', '')

        # Validation
        if password != password_confirm:
            messages.error(request, "Passwords do not match.")
            coverage_areas = CoverageArea.objects.all()
            return render(request, 'accounts/register_farmer.html', {'coverage_areas': coverage_areas})

        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already exists.")
            coverage_areas = CoverageArea.objects.all()
            return render(request, 'accounts/register_farmer.html', {'coverage_areas': coverage_areas})

        if not street_id:
            messages.error(request, "Please select a street.")
            coverage_areas = CoverageArea.objects.all()
            return render(request, 'accounts/register_farmer.html', {'coverage_areas': coverage_areas})

        try:
            with transaction.atomic():
                # Create user
                user = User.objects.create_user(
                    username=email,
                    email=email,
                    password=password,
                    role=User.ROLE_FARMER
                )
                
                # Create farmer profile
                FarmerProfile.objects.create(
                    user=user,
                    farm_name=farm_name,
                    contact_person=contact_person,
                    phone=phone,
                    street_id=street_id,
                    address_details=address_details
                )
                
                # Auto login
                user = authenticate(request, username=email, password=password)
                if user:
                    login(request, user)
                    messages.success(request, "Registration successful!")
                    return redirect('farmer:dashboard')
        except Exception as e:
            messages.error(request, f"Registration failed: {str(e)}")

    coverage_areas = CoverageArea.objects.all()
    return render(request, 'accounts/register_farmer.html', {'coverage_areas': coverage_areas})


def login_view(request):
    """Login view for all user roles."""
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
                'hypothesisId': 'C',
                'location': 'accounts/views.py:151',
                'message': 'login_view entry',
                'data': {'is_authenticated': request.user.is_authenticated, 'method': request.method},
                'timestamp': int(datetime.now().timestamp() * 1000)
            }) + '\n')
    except: pass
    # #endregion
    
    if request.user.is_authenticated:
        # Redirect based on role
        role = request.user.role
        
        # #region agent log
        try:
            with open(log_path, 'a', encoding='utf-8') as f:
                f.write(json.dumps({
                    'sessionId': 'debug-session',
                    'runId': 'run1',
                    'hypothesisId': 'C',
                    'location': 'accounts/views.py:165',
                    'message': 'Already authenticated redirect',
                    'data': {'role': role, 'role_is_none': role is None},
                    'timestamp': int(datetime.now().timestamp() * 1000)
                }) + '\n')
        except: pass
        # #endregion
        
        if role == User.ROLE_CUSTOMER:
            return redirect('customer:home')
        elif role == User.ROLE_FARMER:
            return redirect('farmer:dashboard')
        elif role == User.ROLE_ADMIN:
            return redirect('platform_admin:dashboard')
        elif role == User.ROLE_AGENCY:
            return redirect('agency:dashboard')
        return redirect('/')

    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        user = authenticate(request, username=email, password=password)
        
        # #region agent log
        try:
            with open(log_path, 'a', encoding='utf-8') as f:
                f.write(json.dumps({
                    'sessionId': 'debug-session',
                    'runId': 'run1',
                    'hypothesisId': 'C',
                    'location': 'accounts/views.py:185',
                    'message': 'After authenticate',
                    'data': {'auth_success': user is not None, 'user_role': user.role if user else None, 'role_is_none': user.role is None if user else None},
                    'timestamp': int(datetime.now().timestamp() * 1000)
                }) + '\n')
        except: pass
        # #endregion
        
        if user is not None:
            login(request, user)
            messages.success(request, f"Welcome back, {user.username}!")
            
            # Redirect based on role
            role = user.role
            
            # #region agent log
            try:
                with open(log_path, 'a', encoding='utf-8') as f:
                    f.write(json.dumps({
                        'sessionId': 'debug-session',
                        'runId': 'run1',
                        'hypothesisId': 'C',
                        'location': 'accounts/views.py:197',
                        'message': 'Before role redirect',
                        'data': {'role': role, 'role_is_none': role is None},
                        'timestamp': int(datetime.now().timestamp() * 1000)
                    }) + '\n')
            except: pass
            # #endregion
            
            if role == User.ROLE_CUSTOMER:
                return redirect('customer:home')
            elif role == User.ROLE_FARMER:
                return redirect('farmer:dashboard')
            elif role == User.ROLE_ADMIN:
                return redirect('platform_admin:dashboard')
            elif role == User.ROLE_AGENCY:
                return redirect('agency:dashboard')
            return redirect('/')
        else:
            messages.error(request, "Invalid email or password.")

    return render(request, 'accounts/login.html')


@login_required
def logout_view(request):
    """Logout view."""
    from django.contrib.auth import logout
    logout(request)
    messages.success(request, "You have been logged out successfully.")
    return redirect('accounts:landing')


def generate_password(length=12):
    """Generate a random password."""
    alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
    return ''.join(secrets.choice(alphabet) for i in range(length))
