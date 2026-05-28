from django.shortcuts import render
from django.http import JsonResponse
from django.utils import timezone
from .models import Hall, Device
import json


def halls_map(request):
    """Карта залов - отдаёт статичный HTML"""
    return render(request, 'devices/hallsMap.html')


def api_get_all_statuses(request):
    """API: возвращает статусы ВСЕХ устройств, привязанных к местам"""
    devices = Device.objects.select_related('hall', 'spot').all()

    all_statuses = {}
    for device in devices:
        if device.spot is None:
            continue   # устройства без места не показываем на карте
        # Ключ: id_зала_номерМеста
        key = f"{device.hall.id}_{device.spot.number}"
        all_statuses[key] = {
            'status': device.status,
            'status_display': device.get_status_display(),
            'type': device.device_type,
            'label': str(device),
            'inventory': device.inventory_number,
        }

    return JsonResponse({
        'success': True,
        'timestamp': timezone.now().isoformat(),
        'statuses': all_statuses,
    })