from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from decimal import Decimal
from django.urls import reverse
from django.utils import timezone
from users.models import UserBalance
from .models import Transaction, Booking
from .forms import DepositForm


@login_required
def deposit_view(request):
    """Пополнение баланса"""
    if request.method == 'POST':
        form = DepositForm(request.POST)
        if form.is_valid():
            amount = form.cleaned_data['amount']
            # Создаём транзакцию пополнения
            Transaction.objects.create(
                user=request.user,
                amount=amount,
                transaction_type='deposit',
                description='Пополнение баланса через сайт'
            )
            # Обновляем баланс пользователя
            balance_obj = request.user.balance
            balance_obj.balance += amount
            balance_obj.save()
            messages.success(request, f'Баланс успешно пополнен на {amount} ₽')
            return redirect('booking:transactions')
    else:
        form = DepositForm()
    return render(request, 'booking/deposit.html', {'form': form})


@login_required
def transaction_history(request):
    """История всех транзакций"""
    transactions = request.user.transactions.all()
    return render(request, 'booking/transactions.html', {'transactions': transactions})


@login_required
def active_bookings(request):
    """Активные бронирования пользователя"""
    bookings = request.user.bookings.filter(status='active').order_by('start_time')
    return render(request, 'booking/bookings.html', {'bookings': bookings, 'now': timezone.now()})


@login_required
def cancel_booking(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)
    if booking.status != 'active':
        messages.error(request, 'Это бронирование уже нельзя отменить.')
    elif booking.start_time <= timezone.now():
        messages.error(request, 'Нельзя отменить уже начавшуюся сессию.')
    else:
        booking.status = 'cancelled'
        booking.save()
        Transaction.objects.create(
            user=request.user,
            amount=booking.total_cost,
            transaction_type='refund',
            description=f'Возврат за отмену ПК {booking.computer_number}'
        )
        balance_obj = request.user.balance
        balance_obj.balance += booking.total_cost
        balance_obj.save()
        messages.success(request, f'Бронирование отменено. {booking.total_cost} ₽ возвращены.')

    next_url = request.GET.get('next', reverse('booking:bookings'))
    return redirect(next_url)