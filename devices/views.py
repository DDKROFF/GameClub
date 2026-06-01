from django.shortcuts import render
from django.http import JsonResponse
from django.utils import timezone
from .models import Device

def halls_map(request):
    devices = Device.objects.select_related(
        'hall', 'spot', 'computer_details', 'console_details'
    ).all()
    return render(request, 'devices/hallsMap.html', {'devices': devices})

def api_status_all(request):
    """API: возвращает статусы ВСЕХ устройств, привязанных к местам"""
    devices = Device.objects.select_related('hall', 'spot').all()

    all_statuses = {}
    for device in devices:
        if device.spot is None:
            continue
        key = f"{device.hall.id}_{device.spot.number}"
        all_statuses[key] = {
            'status': device.status,
            'status_display': device.get_status_display(),
            'type': device.device_type,
            'label': str(device),
            'inventory': device.inventory_number,
            'hall_name': device.hall.name,
        }

    return JsonResponse({
        'success': True,
        'timestamp': timezone.now().isoformat(),
        'statuses': all_statuses,
    })