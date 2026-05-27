from django.shortcuts import render
from django.http import JsonResponse
from django.utils import timezone
from .models import Hall, Device
import json


def halls_map(request):
    """Карта залов - отдаёт статичный HTML"""
    return render(request, 'devices/hallsMap.html')


def api_get_all_statuses(request):
    """API: возвращает статусы ВСЕХ устройств"""
    devices = Device.objects.select_related('hall').all()

    all_statuses = {}
    for device in devices:
        row = device.row if device.row is not None else 0
        col = device.column if device.column is not None else 0
        key = f"{device.hall.id}_{row}_{col}"

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