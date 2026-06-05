from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.db import transaction as db_transaction
from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal
from .forms import DeviceActionForm
from devices.models import Device
from users.models import UserBalance
from booking.models import Booking, Transaction

@login_required
@require_POST
def device_action(request):
    form = DeviceActionForm(request.POST)
    if not form.is_valid():
        return JsonResponse({'errors': form.errors}, status=400)

    action = form.cleaned_data['action']
    inventory_number = form.cleaned_data['device_inventory']

    try:
        device = Device.objects.get(inventory_number=inventory_number)
    except Device.DoesNotExist:
        return JsonResponse({'error': 'Устройство не найдено.'}, status=404)

    user = request.user

    try:
        with db_transaction.atomic():
            # Блокируем баланс для изменения, чтобы не было гонки запросов
            balance_obj = UserBalance.objects.select_for_update().get(user=user)

            # === БРОНИРОВАНИЕ ===
            if action == 'reserve':
                if device.status != Device.DeviceStatus.AVAILABLE:
                    return JsonResponse({'error': 'Устройство недоступно.'}, status=400)

                device.status = Device.DeviceStatus.RESERVED
                device.save(update_fields=['status'])

                return JsonResponse({
                    'message': 'Устройство успешно забронировано.',
                    'action': 'reserve',
                    'minutes': form.cleaned_data['duration_minutes']
                })

            # === СТАРТ СЕАНСА ===
            elif action == 'start':
                if device.status not in [Device.DeviceStatus.AVAILABLE, Device.DeviceStatus.RESERVED]:
                    return JsonResponse({'error': 'Устройство занято.'}, status=400)

                tariff = form.cleaned_data['tariff']
                hours = Decimal(str(form.cleaned_data['hours']))
                total_cost = tariff.price * hours

                if balance_obj.balance < total_cost:
                    return JsonResponse({'error': f'Недостаточно средств. Нужно {total_cost} руб.'}, status=400)

                balance_obj.balance -= total_cost
                balance_obj.save(update_fields=['balance'])

                Transaction.objects.create(
                    user=user, amount=total_cost, transaction_type='withdraw',
                    description=f"Оплата сеанса ({hours} ч.) ПК {device.inventory_number}"
                )

                start_time = timezone.now()
                end_time = start_time + timedelta(hours=float(hours))

                Booking.objects.create(
                    user=user, computer_number=device.inventory_number,
                    start_time=start_time, end_time=end_time,
                    tariff_name=tariff.name, total_cost=total_cost, status='active'
                )

                device.status = Device.DeviceStatus.IN_USE
                device.save(update_fields=['status'])

                return JsonResponse({'message': 'Сеанс успешно начат.', 'action': 'start'})

            # === ПРОДЛЕНИЕ СЕАНСА ===
            elif action == 'extend':
                if device.status != Device.DeviceStatus.IN_USE:
                    return JsonResponse({'error': 'Устройство не используется.'}, status=400)

                active_booking = Booking.objects.filter(
                    user=user, computer_number=device.inventory_number, status='active'
                ).order_by('-end_time').first()

                if not active_booking:
                    return JsonResponse({'error': 'Активная сессия не найдена.'}, status=404)

                tariff = form.cleaned_data['tariff']
                hours = Decimal(str(form.cleaned_data['hours']))
                total_cost = tariff.price * hours

                if balance_obj.balance < total_cost:
                    return JsonResponse({'error': f'Недостаточно средств. Нужно {total_cost} руб.'}, status=400)

                balance_obj.balance -= total_cost
                balance_obj.save(update_fields=['balance'])

                Transaction.objects.create(
                    user=user, amount=total_cost, transaction_type='withdraw',
                    description=f"Продление сеанса (+{hours} ч.) ПК {device.inventory_number}"
                )

                active_booking.end_time += timedelta(hours=float(hours))
                active_booking.total_cost += total_cost
                active_booking.save(update_fields=['end_time', 'total_cost'])

                return JsonResponse({'message': 'Сеанс успешно продлен.', 'action': 'extend'})

    except Exception:
        return JsonResponse({'error': 'Произошла ошибка сервера.'}, status=500)

@login_required
def session_form_page(request):
    # Получаем id устройства из GET (при переходе) или из POST (при отправке формы)
    device_id = request.GET.get('device_id') or request.POST.get('device_id')
    device = get_object_or_404(Device, id=device_id)

    if request.method == 'POST':
        form = DeviceActionForm(request.POST)
        if form.is_valid():
            action = form.cleaned_data['action']
            user = request.user

            try:
                with db_transaction.atomic():
                    balance_obj = UserBalance.objects.select_for_update().get(user=user)

                    # === БРОНИРОВАНИЕ ===
                    if action == 'reserve':
                        if device.status != 'AVAILABLE':  # Поправь статус под свою модель, если у тебя там числа или Choice
                            messages.error(request, 'Устройство недоступно для бронирования.')
                            return render(request, 'booking/session_form.html', {'form': form, 'device': device})

                        device.status = 'RESERVED'
                        device.save(update_fields=['status'])
                        messages.success(request, f'Устройство {device.inventory_number} успешно забронировано!')
                        return  redirect('hallMap')  # Перенаправляем на карту залов

                    # === СТАРТ СЕАНСА ===
                    elif action == 'start':
                        if device.status not in ['AVAILABLE', 'RESERVED']:
                            messages.error(request, 'Устройство уже занято.')
                            return render(request, 'booking/session_form.html', {'form': form, 'device': device})

                        tariff = form.cleaned_data['tariff']
                        hours = Decimal(str(form.cleaned_data['hours']))
                        total_cost = tariff.price * hours

                        if balance_obj.balance < total_cost:
                            messages.error(request,
                                           f'Недостаточно средств. Нужно {total_cost} руб. Ваш баланс: {balance_obj.balance} руб.')
                            return render(request, 'booking/session_form.html', {'form': form, 'device': device})

                        # Списываем деньги
                        balance_obj.balance -= total_cost
                        balance_obj.save(update_fields=['balance'])

                        # Создаем транзакцию
                        Transaction.objects.create(
                            user=user, amount=total_cost, transaction_type='withdraw',
                            description=f"Оплата сеанса ({hours} ч.) ПК {device.inventory_number}"
                        )

                        # Создаем сессию аренды (Booking)
                        start_time = timezone.now()
                        end_time = start_time + timedelta(hours=float(hours))

                        Booking.objects.create(
                            user=user, computer_number=device.inventory_number,
                            start_time=start_time, end_time=end_time,
                            tariff_name=tariff.name, total_cost=total_cost, status='active'
                        )

                        # Меняем статус компа
                        device.status = 'IN_USE'
                        device.save(update_fields=['status'])

                        messages.success(request, 'Сеанс успешно начат! Компьютер включен.')
                        return redirect('hallMap')

                    # === ПРОДЛЕНИЕ ===
                    elif action == 'extend':
                        if device.status != 'IN_USE':
                            messages.error(request, 'Устройство сейчас не используется.')
                            return render(request, 'booking/session_form.html', {'form': form, 'device': device})

                        active_booking = Booking.objects.filter(
                            user=user, computer_number=device.inventory_number, status='active'
                        ).order_by('-end_time').first()

                        if not active_booking:
                            messages.error(request, 'Активная сессия не найдена.')
                            return render(request, 'booking/session_form.html', {'form': form, 'device': device})

                        tariff = form.cleaned_data['tariff']
                        hours = Decimal(str(form.cleaned_data['hours']))
                        total_cost = tariff.price * hours

                        if balance_obj.balance < total_cost:
                            messages.error(request, f'Недостаточно средств для продления сессии ({total_cost} руб.)')
                            return render(request, 'booking/session_form.html', {'form': form, 'device': device})

                        balance_obj.balance -= total_cost
                        balance_obj.save(update_fields=['balance'])

                        Transaction.objects.create(
                            user=user, amount=total_cost, transaction_type='withdraw',
                            description=f"Продление сеанса (+{hours} ч.) ПК {device.inventory_number}"
                        )

                        active_booking.end_time += timedelta(hours=float(hours))
                        active_booking.total_cost += total_cost
                        active_booking.save(update_fields=['end_time', 'total_cost'])

                        messages.success(request, 'Сеанс успешно продлен!')
                        return redirect('hallMap')

            except Exception as e:
                messages.error(request, f'Ошибка базы данных: {str(e)}')
                return render(request, 'booking/session_form.html', {'form': form, 'device': device})
    else:
        # GET-запрос: создаем чистую форму
        form = DeviceActionForm(initial={'device_inventory': device.inventory_number})

    return render(request, 'booking/session_form.html', {'form': form, 'device': device})