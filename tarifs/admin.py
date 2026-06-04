from django.contrib import admin
from .models import Tariff

@admin.register(Tariff)
class TariffAdmin(admin.ModelAdmin):
    list_display = ('name', 'tariff_type', 'price', 'fixed_duration_hours', 'device_type', 'is_active')
    list_filter = ('tariff_type', 'device_type', 'is_active')
    fieldsets = (
        (None, {
            'fields': ('name', 'tariff_type', 'device_type', 'is_active', 'description')
        }),
        ('Цены и время', {
            'fields': ('price', 'fixed_duration_hours'),
            'description': 'Для почасового тарифа цена указывается за 1 час, поле длительности игнорируется. Для фиксированного — общая стоимость сеанса и его длительность.'
        })
    )