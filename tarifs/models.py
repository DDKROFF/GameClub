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
    price = models.DecimalField(max_digits=10, decimal_places=1, verbose_name='Цена (руб)')
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

    def duration_display(self):
        if self.tariff_type != 'fixed' or not self.fixed_duration_hours:
            return ''
        total_minutes = int(self.fixed_duration_hours)
        if total_minutes < 60:
            return f'{total_minutes} мин'
        hours = total_minutes // 60
        mins = total_minutes % 60
        if 11 <= hours % 100 <= 14:
            hour_word = 'часов'
        elif hours % 10 == 1:
            hour_word = 'час'
        elif 2 <= hours % 10 <= 4:
            hour_word = 'часа'
        else:
            hour_word = 'часов'
        if mins:
            return f'{hours} {hour_word} {mins} мин'
        return f'{hours} {hour_word}'