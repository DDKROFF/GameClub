from django.db import models
from django.conf import settings
from django.utils import timezone
from django.core.validators import MinValueValidator

class Transaction(models.Model):
    TYPE_CHOICES = (
        ('deposit', 'Пополнение'),
        ('withdraw', 'Списание'),
        ('refund', 'Возврат'),
        ('bonus', 'Бонус'),
    )
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='transactions')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    transaction_type = models.CharField(max_length=10, choices=TYPE_CHOICES)
    description = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Транзакция'
        verbose_name_plural = 'Транзакции'

    def __str__(self):
        return f"{self.user.username} | {self.get_transaction_type_display()} | {self.amount}"


class Booking(models.Model):
    STATUS_CHOICES = (
        ('active', 'Активна'),
        ('completed', 'Завершена'),
        ('cancelled', 'Отменена'),
    )
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='bookings')
    computer_number = models.CharField(max_length=10, verbose_name='Номер ПК')
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    tariff_name = models.CharField(max_length=50, verbose_name='Тариф')
    total_cost = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='active')
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['-start_time']
        verbose_name = 'Бронирование'
        verbose_name_plural = 'Бронирования'

    def __str__(self):
        return f"{self.user.username} | ПК {self.computer_number} | {self.start_time} - {self.end_time}"