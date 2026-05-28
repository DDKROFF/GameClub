from django.urls import path
from . import views
from django.http import JsonResponse
from .models import Spot, Device

def available_spots(request):
    hall_id = request.GET.get('hall_id')
    if not hall_id:
        return JsonResponse({'spots': []})
    # Возвращаем свободные места + место текущего устройства (если редактируется)
    device_id = request.GET.get('device_id')  # можно передавать опционально
    spots = Spot.objects.filter(hall_id=hall_id, device__isnull=True)
    if device_id:
        spots = Spot.objects.filter(
            hall_id=hall_id
        ).filter(
            models.Q(device__isnull=True) | models.Q(device_id=device_id)
        )
    data = [{'id': spot.id, 'label': f'Место {spot.number}'} for spot in spots]
    return JsonResponse({'spots': data})
urlpatterns = [
    path('halls/map/', views.halls_map, name='halls_map'),
    path('api/statuses/all/', views.api_get_all_statuses, name='api_all_statuses'),
    path('js/spots/available/', available_spots, name='available_spots'),
]