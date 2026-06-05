from django.shortcuts import render
from django.http import JsonResponse
from django.utils import timezone
from .models import Device, Computer, Console

def halls_map(request):
    devices = Device.objects.select_related(
        'hall', 'spot', 'computer_details', 'console_details'
    ).all()
    return render(request, 'devices/hallsMap.html', {'devices': devices})

def api_status_all(request):
    """API: возвращает статусы + характеристики всех устройств, привязанных к местам"""
    devices = Device.objects.select_related(
        'hall', 'spot', 'computer_details', 'console_details'
    ).all()

    all_statuses = {}
    for device in devices:
        if device.spot is None:
            continue

        key = f"{device.hall.id}_{device.spot.number}"

        # Базовые поля (как и раньше)
        data = {
            'id': device.id,               # нужно для кнопки «Забронировать»
            'status': device.status,
            'status_display': device.get_status_display(),
            'type': device.device_type,
            'label': str(device),
            'inventory': device.inventory_number,
            'hall_name': device.hall.name,
        }

        # Добавляем характеристики в зависимости от типа
        if device.device_type == Device.DeviceType.COMPUTER:
            try:
                comp = device.computer_details
                data.update({
                    'cpu': comp.cpu,
                    'gpu': comp.gpu,
                    'ram_gb': comp.ram_gb,
                    'storage_gb': comp.storage_gb,
                    'os': comp.os,
                })
            except Computer.DoesNotExist:
                pass

        elif device.device_type == Device.DeviceType.CONSOLE:
            try:
                con = device.console_details
                console_name = con.get_console_type_display() if con.console_type else ''
                data.update({
                    'console_type': console_name,
                    'controller_count': con.controller_count,
                    'storage_gb': con.storage_gb,
                    'has_vr_support': con.has_vr_support,
                })
            except Console.DoesNotExist:
                pass

        all_statuses[key] = data

    return JsonResponse({
        'success': True,
        'timestamp': timezone.now().isoformat(),
        'statuses': all_statuses,
    })