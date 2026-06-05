from django import forms
from devices.models import Device
from tarifs.models import Tariff


class DeviceActionForm(forms.Form):
    ACTION_CHOICES = [
        ('reserve', 'Забронировать устройство'),
        ('start', 'Начать сессию (Списание баланса)'),
        ('extend', 'Продлить сессию'),
    ]

    # Сделали поле видимым, чтобы юзер мог выбрать действие на странице
    action = forms.ChoiceField(
        choices=ACTION_CHOICES,
        label='Выберите действие',
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    device_inventory = forms.CharField(
        label='Инвентарный номер',
        max_length=50,
        widget=forms.TextInput(attrs={'readonly': 'readonly', 'class': 'form-control'})
    )
    duration_minutes = forms.IntegerField(
        label='Длительность брони (только для Бронирования, мин)',
        required=False,
        min_value=1,
        widget=forms.NumberInput(attrs={'placeholder': 'Например: 15', 'class': 'form-control'})
    )
    tariff = forms.ModelChoiceField(
        label='Тариф (для Старта и Продления)',
        queryset=Tariff.objects.filter(is_active=True),
        required=False,
        empty_label='Выберите тариф',
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    hours = forms.DecimalField(
        label='Количество часов (для Старта и Продления)',
        required=False,
        min_value=0.5,
        decimal_places=1,
        widget=forms.NumberInput(attrs={'step': '0.5', 'class': 'form-control'})
    )

    def clean(self):
        cleaned_data = super().clean()
        action = cleaned_data.get('action')

        if action == 'reserve':
            if not cleaned_data.get('duration_minutes'):
                self.add_error('duration_minutes', 'Укажите длительность брони.')

        elif action in ['start', 'extend']:
            if not cleaned_data.get('tariff'):
                self.add_error('tariff', 'Необходимо выбрать тариф.')
            if not cleaned_data.get('hours'):
                self.add_error('hours', 'Укажите количество часов.')

        return cleaned_data