"""
Marketplace app views - Products and categories
"""
from django.shortcuts import render, get_object_or_404
from django.db.models import Q
from .models import Product, Category
from accounts.decorators import customer_required, farmer_required
from accounts.models import FarmerProfile


@customer_required
def product_list(request):
    """Product listing page for customers with search and filters."""
    products = Product.objects.filter(is_active=True)
    
    # Search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        products = products.filter(
            Q(name__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(farmer__farm_name__icontains=search_query)
        )
    
    # Category filter
    category_id = request.GET.get('category', '')
    if category_id:
        products = products.filter(category_id=category_id)
    
    # Location filter - search in both new location fields and legacy field
    location = request.GET.get('location', '')
    if location:
        from accounts.location_models import CoverageArea, Street
        # Try to find matching coverage area or street
        matching_areas = CoverageArea.objects.filter(name__icontains=location)
        matching_streets = Street.objects.filter(name__icontains=location)
        if matching_areas.exists() or matching_streets.exists():
            products = products.filter(
                Q(location_coverage_area__in=matching_areas) |
                Q(location_street__in=matching_streets) |
                Q(location__icontains=location)
            )
        else:
            products = products.filter(location__icontains=location)
    
    categories = Category.objects.all()
    
    context = {
        'products': products,
        'categories': categories,
        'search_query': search_query,
        'selected_category': category_id,
        'selected_location': location,
    }
    
    return render(request, 'marketplace/product_list.html', context)


@customer_required
def product_detail(request, product_id):
    """Product detail page."""
    product = get_object_or_404(Product, id=product_id, is_active=True)
    return render(request, 'marketplace/product_detail.html', {'product': product})
