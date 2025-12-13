"""
Location API views for loading streets dynamically
"""
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from .location_models import CoverageArea, Street


@require_http_methods(["GET"])
def get_streets(request):
    """API endpoint to get streets for a coverage area."""
    coverage_area_id = request.GET.get('coverage_area')
    
    if not coverage_area_id:
        return JsonResponse({'streets': []})
    
    try:
        streets = Street.objects.filter(coverage_area_id=coverage_area_id).order_by('name')
        streets_data = [{'id': street.id, 'name': street.name} for street in streets]
        return JsonResponse({'streets': streets_data})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


