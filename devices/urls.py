from django.urls import path
from . import views
from django.http import JsonResponse
from .models import Spot, Device

urlpatterns = [
    path('halls/map/', views.halls_map, name='halls_map'),
    path('api/statuses/all/', views.api_get_all_statuses, name='api_all_statuses'),
]

def available_spots(request):
    hall_id = request.GET.get('hall_id')
    if not hall_id:
        return JsonResponse({'spots': []})
    spots = Spot.objects.filter(hall_id=hall_id, device__isnull=True)
    data = [{'id': spot.id, 'label': f'Место {spot.number}'} for spot in spots]
    return JsonResponse({'spots': data})