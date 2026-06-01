from django.contrib import admin
from django import forms
from django.utils.html import format_html
from django.db import models as db_models
from .models import Hall, Spot, Device, Computer, Console


# -------------------------------------------------------
# Вспомогательный список ОС
# -------------------------------------------------------
class OperatingSystem:
    CHOICES = [
        ('windows_11', 'Windows 11'),
        ('windows_10', 'Windows 10'),
        ('macos_sonoma', 'macOS Sonoma'),
        ('macos_ventura', 'macOS Ventura'),
        ('other', 'Другая (указать вручную)'),
    ]


# -------------------------------------------------------
# Единая форма для создания/редактирования Устройства
# -------------------------------------------------------
class DeviceForm(forms.ModelForm):
    # Поля из Device (в модели они есть, но дублируем для полного контроля)
    hall = forms.ModelChoiceField(
        queryset=Hall.objects.all(),
        label="Зал",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    spot = forms.ModelChoiceField(
        queryset=Spot.objects.none(),
        label="Место в зале",
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    device_type = forms.ChoiceField(
        choices=Device.DeviceType.choices,
        label="Тип устройства",
        widget=forms.Select(attrs={'class': 'form-control type-select'})
    )
    status = forms.ChoiceField(
        choices=Device.DeviceStatus.choices,
        initial=Device.DeviceStatus.AVAILABLE,
        label="Статус",
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    # ---------- Поля компьютера ----------
    cpu = forms.CharField(max_length=100, required=False, label="Процессор",
                          widget=forms.TextInput(attrs={'class': 'form-control'}))
    gpu = forms.CharField(max_length=100, required=False, label="Видеокарта",
                          widget=forms.TextInput(attrs={'class': 'form-control'}))
    ram_gb = forms.IntegerField(min_value=1, required=False, label="ОЗУ (ГБ)",
                                widget=forms.NumberInput(attrs={'class': 'form-control'}))
    storage_gb = forms.IntegerField(min_value=1, required=False, label="Накопитель (ГБ)",
                                    widget=forms.NumberInput(attrs={'class': 'form-control'}))
    os_choice = forms.ChoiceField(
        choices=OperatingSystem.CHOICES,
        label="Операционная система",
        required=False,
        widget=forms.Select(attrs={'class': 'form-control os-select'})
    )
    os_custom = forms.CharField(
        max_length=100, required=False, label="Другая ОС",
        widget=forms.TextInput(attrs={'class': 'form-control os-custom', 'placeholder': 'Введите название ОС'})
    )
    has_webcam = forms.BooleanField(required=False, label="Веб-камера",
                                    widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}))
    has_microphone = forms.BooleanField(required=False, label="Микрофон",
                                        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}))

    # ---------- Поля консоли ----------
    console_type = forms.ChoiceField(
        choices=Console.ConsoleType.choices,
        required=False,
        label="Тип консоли",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    controller_count = forms.IntegerField(
        min_value=1, max_value=8, initial=2, required=False,
        label="Кол-во контроллеров",
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )
    has_kinect = forms.BooleanField(required=False, label="Kinect/камера",
                                    widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}))
    has_vr_support = forms.BooleanField(required=False, label="Поддержка VR",
                                        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}))
    console_storage_gb = forms.IntegerField(
        min_value=1, initial=500, required=False,
        label="Накопитель (ГБ)",
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )

    class Meta:
        model = Device
        fields = []  # все поля объявлены явно

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        instance = kwargs.get('instance')

        # Если редактируем существующее устройство – заполняем начальные значения
        if instance and instance.pk:
            self.fields['device_type'].initial = instance.device_type
            self.fields['hall'].initial = instance.hall
            self.fields['status'].initial = instance.status

            # Место – кверисет с учётом текущего зала и возможности оставить занятое место
            spot_qs = Spot.objects.filter(hall=instance.hall).filter(
                db_models.Q(device__isnull=True) | db_models.Q(device=instance)
            )
            self.fields['spot'].queryset = spot_qs
            if instance.spot:
                self.fields['spot'].initial = instance.spot

            # Заполняем поля компьютера или консоли, если они есть
            if instance.device_type == Device.DeviceType.COMPUTER:
                try:
                    comp = instance.computer_details
                    self.fields['cpu'].initial = comp.cpu
                    self.fields['gpu'].initial = comp.gpu
                    self.fields['ram_gb'].initial = comp.ram_gb
                    self.fields['storage_gb'].initial = comp.storage_gb
                    os_val = comp.os
                    found = False
                    for code, name in OperatingSystem.CHOICES:
                        if code == os_val or name == os_val:
                            self.fields['os_choice'].initial = code
                            found = True
                            break
                    if not found:
                        self.fields['os_choice'].initial = 'other'
                        self.fields['os_custom'].initial = os_val
                    self.fields['has_webcam'].initial = comp.has_webcam
                    self.fields['has_microphone'].initial = comp.has_microphone
                except Computer.DoesNotExist:
                    pass

            elif instance.device_type == Device.DeviceType.CONSOLE:
                try:
                    cons = instance.console_details
                    self.fields['console_type'].initial = cons.console_type
                    self.fields['controller_count'].initial = cons.controller_count
                    self.fields['has_kinect'].initial = cons.has_kinect
                    self.fields['has_vr_support'].initial = cons.has_vr_support
                    self.fields['console_storage_gb'].initial = cons.storage_gb
                except Console.DoesNotExist:
                    pass

            # После создания тип устройства менять нельзя
            self.fields['device_type'].disabled = True
        else:
            # При создании spot изначально пустой
            self.fields['spot'].queryset = Spot.objects.none()

    def clean_spot(self):
        spot = self.cleaned_data.get('spot')
        hall = self.cleaned_data.get('hall')
        if spot and hall and spot.hall != hall:
            raise forms.ValidationError("Место не принадлежит выбранному залу.")
        if spot and hasattr(spot, 'device') and spot.device is not None:
            # При редактировании разрешаем то же устройство
            if self.instance.pk and spot.device == self.instance:
                pass
            else:
                raise forms.ValidationError("Это место уже занято другим устройством.")
        return spot

    def clean(self):
        cleaned_data = super().clean()
        device_type = cleaned_data.get('device_type')

        # Валидация обязательных полей в зависимости от типа
        if device_type == Device.DeviceType.COMPUTER:
            if not cleaned_data.get('cpu'):
                self.add_error('cpu', 'Укажите процессор.')
            if not cleaned_data.get('gpu'):
                self.add_error('gpu', 'Укажите видеокарту.')
            if not cleaned_data.get('ram_gb'):
                self.add_error('ram_gb', 'Укажите объём ОЗУ.')
            if not cleaned_data.get('storage_gb'):
                self.add_error('storage_gb', 'Укажите объём накопителя.')
            os_choice = cleaned_data.get('os_choice')
            os_custom = cleaned_data.get('os_custom')
            if os_choice == 'other' and not os_custom:
                self.add_error('os_custom', 'Укажите название ОС.')
            if os_choice and os_choice != 'other':
                for code, name in OperatingSystem.CHOICES:
                    if code == os_choice:
                        cleaned_data['os'] = name
                        break
            else:
                cleaned_data['os'] = os_custom
        elif device_type == Device.DeviceType.CONSOLE:
            if not cleaned_data.get('console_type'):
                self.add_error('console_type', 'Выберите тип консоли.')
            if not cleaned_data.get('controller_count'):
                self.add_error('controller_count', 'Укажите количество контроллеров.')
            if not cleaned_data.get('console_storage_gb'):
                self.add_error('console_storage_gb', 'Укажите объём накопителя.')

        return cleaned_data

    def save(self, commit=True):
        # Сначала сохраняем Device
        device = super().save(commit=False)
        device.hall = self.cleaned_data['hall']
        device.device_type = self.cleaned_data['device_type']
        device.status = self.cleaned_data['status']
        device.spot = self.cleaned_data.get('spot')
        if commit:
            device.save()  # здесь сгенерируется inventory_number
        else:
            # Если commit=False (редко в админке), всё равно надо сохранить, чтобы получить pk
            device.save()

        # Удаляем старые связанные записи, если тип поменялся (хотя мы запретили смену)
        if device.device_type == Device.DeviceType.COMPUTER:
            # Удаляем возможную консоль
            Console.objects.filter(device=device).delete()
            computer, _ = Computer.objects.update_or_create(
                device=device,
                defaults={
                    'cpu': self.cleaned_data.get('cpu', ''),
                    'gpu': self.cleaned_data.get('gpu', ''),
                    'ram_gb': self.cleaned_data.get('ram_gb', 1),
                    'storage_gb': self.cleaned_data.get('storage_gb', 1),
                    'os': self.cleaned_data.get('os', ''),
                    'has_webcam': self.cleaned_data.get('has_webcam', False),
                    'has_microphone': self.cleaned_data.get('has_microphone', False),
                }
            )
        elif device.device_type == Device.DeviceType.CONSOLE:
            Computer.objects.filter(device=device).delete()
            Console.objects.update_or_create(
                device=device,
                defaults={
                    'console_type': self.cleaned_data.get('console_type', 'ps5'),
                    'controller_count': self.cleaned_data.get('controller_count', 2),
                    'has_kinect': self.cleaned_data.get('has_kinect', False),
                    'has_vr_support': self.cleaned_data.get('has_vr_support', False),
                    'storage_gb': self.cleaned_data.get('console_storage_gb', 500),
                }
            )
        return device


# -------------------------------------------------------
# Inline для отображения мест в зале
# -------------------------------------------------------
class SpotInline(admin.TabularInline):
    model = Spot
    fields = ('number', 'device_type_info', 'device_status_info')
    readonly_fields = ('device_type_info', 'device_status_info')
    can_delete = False
    extra = 0

    def device_type_info(self, obj):
        if hasattr(obj, 'device') and obj.device:
            return obj.device.get_device_type_display()
        return "—"
    device_type_info.short_description = "Тип устройства"

    def device_status_info(self, obj):
        if hasattr(obj, 'device') and obj.device:
            return obj.device.get_status_display()
        return "—"
    device_status_info.short_description = "Статус"

    def has_add_permission(self, request, obj=None):
        return False


# -------------------------------------------------------
# Админ-класс для залов
# -------------------------------------------------------
@admin.register(Hall)
class HallAdmin(admin.ModelAdmin):
    list_display = ('name', 'max_capacity', 'created_at')
    search_fields = ('name',)
    inlines = [SpotInline]


# -------------------------------------------------------
# Админ-класс для устройств (единственная точка управления)
# -------------------------------------------------------
@admin.register(Device)
class DeviceAdmin(admin.ModelAdmin):
    form = DeviceForm
    list_display = ('inventory_number', 'device_type', 'status', 'hall', 'spot_info')
    list_filter = ('device_type', 'status', 'hall')
    search_fields = ('inventory_number',)
    readonly_fields = ('inventory_number',)

    fieldsets = (
        ('Общая информация', {
            'fields': ('device_type', 'hall', 'spot', 'status')
        }),
        ('Характеристики компьютера', {
            'fields': (
                'cpu', 'gpu', 'ram_gb', 'storage_gb',
                'os_choice', 'os_custom',
                'has_webcam', 'has_microphone',
            ),
            'classes': ('computer-fields',),
        }),
        ('Характеристики консоли', {
            'fields': (
                'console_type', 'controller_count', 'console_storage_gb',
                'has_kinect', 'has_vr_support',
            ),
            'classes': ('console-fields',),
        }),
    )

    class Media:
        js = ('js/device_admin.js',)
        css = {
            'all': ('css/device_admin.css',)
        }

    def spot_info(self, obj):
        if obj.spot:
            return f"Место {obj.spot.number}"
        return "Склад"
    spot_info.short_description = "Место"

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        # При создании скрываем ненужные секции через JS, здесь просто возвращаем форму
        return form