from django.db import models
from django.core.exceptions import ValidationError
from devices.models import Device

class Tariff(models.Model):
    DEVICE_TYPES = Device.DeviceType.choices
    DEVICE_TYPES_WITH_ALL = list(DEVICE_TYPES) + [('all', 'Все устройства')]

    TARIFF_TYPES = [
        ('hourly', 'Поминутная оплата'),
        ('fixed', 'Фиксированное время'),
    ]

    name = models.CharField(max_length=100, unique=True, verbose_name='Название тарифа')
    tariff_type = models.CharField(max_length=10, choices=TARIFF_TYPES, default='hourly', verbose_name='Тип тарифа')
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Цена (руб)')
    fixed_duration_hours = models.DecimalField(
        max_digits=5, decimal_places=2, null=True, blank=True,
        verbose_name='Длительность (минуты) для фиксированного тарифа'
    )
    device_type = models.CharField(
        max_length=20, choices=DEVICE_TYPES_WITH_ALL, default='all',
        verbose_name='Тип устройства'
    )
    is_active = models.BooleanField(default=True, verbose_name='Активен')
    description = models.TextField(blank=True, null=True, verbose_name='Описание')

    class Meta:
        verbose_name = 'Тариф'
        verbose_name_plural = 'Тарифы'
        ordering = ['price']

    def __str__(self):
        if self.tariff_type == 'minutes':
            return f"{self.name} – {self.price}₽/минута ({self.get_device_type_display()})"
        else:
            minutes = self.fixed_duration_hours or 0
            if minutes >= 1:
                return f"{self.name} – {minutes} ч / {self.price}₽ ({self.get_device_type_display()})"
            else:
                minutes_display = int(minutes * 60)
                return f"{self.name} – {minutes_display} мин / {self.price}₽ ({self.get_device_type_display()})"

    def clean(self):
        if self.price < 0:
            raise ValidationError('Цена не может быть отрицательной')
        if self.tariff_type == 'fixed' and not self.fixed_duration_hours:
            raise ValidationError('Для фиксированного тарифа укажите длительность')
        if self.tariff_type == 'fixed' and self.fixed_duration_hours <= 0:
            raise ValidationError('Длительность должна быть положительной')

"""

from django.db import models
from devices.models import Device
from tarifs.models import Tariff

class Booking(models.Model):
    device = models.ForeignKey(Device, on_delete=models.CASCADE, verbose_name='Устройство')
    tariff = models.ForeignKey(Tariff, on_delete=models.SET_NULL, null=True, verbose_name='Тариф')
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    Вариант для реализации сеанса или бронирования
    def clean(self):
    if not self.tariff.is_active:
        raise ValidationError('Тариф не активен')
    if self.tariff.device_type != 'all' and self.tariff.device_type != self.device.device_type:
        raise ValidationError('Тариф не подходит для этого типа устройства')
"""