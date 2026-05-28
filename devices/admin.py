from django.contrib import admin
from django import forms
from django.utils.html import format_html
from django.db import models as db_models
from .models import Hall, Spot, Device, Computer, Console


# ---------- Вспомогательный список ОС ----------
class OperatingSystem:
    CHOICES = [
        ('windows_11', 'Windows 11'),
        ('windows_10', 'Windows 10'),
        ('macos_sonoma', 'macOS Sonoma'),
        ('macos_ventura', 'macOS Ventura'),
        ('other', 'Другая (указать вручную)'),
    ]


# ---------- Форма создания/редактирования компьютера ----------
class ComputerCreationForm(forms.ModelForm):
    hall = forms.ModelChoiceField(
        queryset=Hall.objects.all(),
        label="Зал",
        required=True,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    spot = forms.ModelChoiceField(
        queryset=Spot.objects.none(),
        label="Место в зале",
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    status = forms.ChoiceField(
        choices=Device.DeviceStatus.choices,
        label="Статус",
        initial=Device.DeviceStatus.AVAILABLE,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    os_choice = forms.ChoiceField(
        choices=OperatingSystem.CHOICES,
        label="Операционная система",
        required=False,
        initial='windows_11',
        widget=forms.Select(attrs={'class': 'form-control os-select'})
    )
    os_custom = forms.CharField(
        max_length=100,
        label="Другая ОС",
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control os-custom',
            'placeholder': 'Введите название ОС'
        })
    )

    class Meta:
        model = Computer
        fields = ['cpu', 'gpu', 'ram_gb', 'storage_gb', 'has_webcam', 'has_microphone']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['ram_gb'].widget.attrs['min'] = 1
        self.fields['storage_gb'].widget.attrs['min'] = 1

        # При редактировании: подставляем текущий зал и место
        if self.instance and self.instance.pk and hasattr(self.instance, 'device'):
            device = self.instance.device
            self.fields['hall'].initial = device.hall
            self.fields['status'].initial = device.status
            if device.spot:
                self.fields['spot'].queryset = Spot.objects.filter(
                    hall=device.hall
                ).filter(
                    db_models.Q(device__isnull=True) | db_models.Q(device=device)
                )
                self.fields['spot'].initial = device.spot
            else:
                self.fields['spot'].queryset = Spot.objects.filter(
                    hall=device.hall, device__isnull=True
                )

            # Определяем значение для os_choice
            os_value = device.computer_details.os if hasattr(device, 'computer_details') else ''
            found = False
            for code, name in OperatingSystem.CHOICES:
                if code == os_value or name == os_value:
                    self.fields['os_choice'].initial = code
                    found = True
                    break
            if not found:
                self.fields['os_choice'].initial = 'other'
                self.fields['os_custom'].initial = os_value

    def clean_spot(self):
        spot = self.cleaned_data.get('spot')
        hall = self.cleaned_data.get('hall')
        if spot and hall and spot.hall != hall:
            raise forms.ValidationError("Выбранное место не принадлежит указанному залу.")
        if spot and hasattr(spot, 'device') and spot.device is not None:
            # Если редактируем существующий компьютер, допускаем своё же место
            if self.instance.pk and hasattr(self.instance, 'device') and spot.device == self.instance.device:
                pass
            else:
                raise forms.ValidationError("Это место уже занято другим устройством.")
        return spot

    def clean(self):
        cleaned_data = super().clean()
        os_choice = cleaned_data.get('os_choice')
        os_custom = cleaned_data.get('os_custom')
        if os_choice == 'other':
            if not os_custom:
                self.add_error('os_custom', 'Укажите название операционной системы')
            else:
                cleaned_data['os'] = os_custom
        else:
            for code, name in OperatingSystem.CHOICES:
                if code == os_choice:
                    cleaned_data['os'] = name
                    break
        return cleaned_data

    def save(self, commit=True):
        device = Device(
            hall=self.cleaned_data['hall'],
            device_type='computer',
            status=self.cleaned_data['status'],
            spot=self.cleaned_data.get('spot')
        )
        if commit:
            device.save()
            computer = super().save(commit=False)
            computer.device = device
            computer.os = self.cleaned_data['os']
            computer.save()
            return computer
        else:
            computer = super().save(commit=False)
            computer.device = device
            computer.os = self.cleaned_data['os']
            return computer


# ---------- Форма создания/редактирования консоли ----------
class ConsoleCreationForm(forms.ModelForm):
    hall = forms.ModelChoiceField(
        queryset=Hall.objects.all(),
        label="Зал",
        required=True,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    spot = forms.ModelChoiceField(
        queryset=Spot.objects.none(),
        label="Место в зале",
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    status = forms.ChoiceField(
        choices=Device.DeviceStatus.choices,
        label="Статус",
        initial=Device.DeviceStatus.AVAILABLE,
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    class Meta:
        model = Console
        fields = ['console_type', 'controller_count', 'has_kinect', 'has_vr_support', 'storage_gb']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['controller_count'].initial = 2
        self.fields['storage_gb'].initial = 500
        self.fields['console_type'].widget.attrs['class'] = 'form-control'
        self.fields['controller_count'].widget.attrs['class'] = 'form-control'
        self.fields['storage_gb'].widget.attrs['class'] = 'form-control'

        # При редактировании
        if self.instance and self.instance.pk and hasattr(self.instance, 'device'):
            device = self.instance.device
            self.fields['hall'].initial = device.hall
            self.fields['status'].initial = device.status
            if device.spot:
                self.fields['spot'].queryset = Spot.objects.filter(
                    hall=device.hall
                ).filter(
                    db_models.Q(device__isnull=True) | db_models.Q(device=device)
                )
                self.fields['spot'].initial = device.spot
            else:
                self.fields['spot'].queryset = Spot.objects.filter(
                    hall=device.hall, device__isnull=True
                )

    def clean_spot(self):
        spot = self.cleaned_data.get('spot')
        hall = self.cleaned_data.get('hall')
        if spot and hall and spot.hall != hall:
            raise forms.ValidationError("Выбранное место не принадлежит указанному залу.")
        if spot and hasattr(spot, 'device') and spot.device is not None:
            if self.instance.pk and hasattr(self.instance, 'device') and spot.device == self.instance.device:
                pass
            else:
                raise forms.ValidationError("Это место уже занято другим устройством.")
        return spot

    def save(self, commit=True):
        device = Device(
            hall=self.cleaned_data['hall'],
            device_type='console',
            status=self.cleaned_data['status'],
            spot=self.cleaned_data.get('spot')
        )
        if commit:
            device.save()
            console = super().save(commit=False)
            console.device = device
            console.save()
            return console
        else:
            console = super().save(commit=False)
            console.device = device
            return console


# ---------- Inline для отображения мест в зале ----------
class SpotInline(admin.TabularInline):
    model = Spot
    fields = ('number', 'device_info', 'device_status')
    readonly_fields = ('device_info', 'device_status')
    can_delete = False
    extra = 0

    def device_info(self, obj):
        if hasattr(obj, 'device') and obj.device:
            return obj.device.get_device_type_display()
        return "—"
    device_info.short_description = "Тип устройства"

    def device_status(self, obj):
        if hasattr(obj, 'device') and obj.device:
            return obj.device.get_status_display()
        return "—"
    device_status.short_description = "Статус"

    def has_add_permission(self, request, obj=None):
        return False


# ---------- Админ-класс для залов ----------
@admin.register(Hall)
class HallAdmin(admin.ModelAdmin):
    list_display = ('name', 'max_capacity', 'created_at')
    search_fields = ('name',)
    inlines = [SpotInline]


# ---------- Админ-класс для устройств ----------
@admin.register(Device)
class DeviceAdmin(admin.ModelAdmin):
    list_display = ('inventory_number', 'device_type', 'status', 'hall', 'spot_info', 'get_details_link')
    list_filter = ('device_type', 'status', 'hall')
    search_fields = ('inventory_number',)
    readonly_fields = ('inventory_number', 'device_type')

    def spot_info(self, obj):
        if obj.spot:
            return f"Место {obj.spot.number}"
        return "Склад (без места)"
    spot_info.short_description = "Место"

    def get_details_link(self, obj):
        if obj.device_type == 'computer' and hasattr(obj, 'computer_details'):
            url = f'/js/devices/computer/{obj.computer_details.pk}/change/'
            return format_html('<a href="{}">Просмотр компьютера</a>', url)
        elif obj.device_type == 'console' and hasattr(obj, 'console_details'):
            url = f'/js/devices/console/{obj.console_details.pk}/change/'
            return format_html('<a href="{}">Просмотр консоли</a>', url)
        return '-'
    get_details_link.short_description = 'Детали'


# ---------- Админ-класс для компьютеров ----------
@admin.register(Computer)
class ComputerAdmin(admin.ModelAdmin):
    form = ComputerCreationForm
    list_display = ('device', 'cpu', 'ram_gb', 'storage_gb', 'get_os_display', 'get_inventory_number',
                    'get_hall', 'get_status')
    list_filter = ('device__hall', 'device__status', 'os')
    search_fields = ('device__inventory_number', 'cpu', 'os')
    raw_id_fields = ('device',)
    readonly_fields = ('device',)

    fieldsets = (
        ('Общая информация', {
            'fields': ('hall', 'spot', 'status')
        }),
        ('Технические характеристики', {
            'fields': ('cpu', 'gpu', 'ram_gb', 'storage_gb')
        }),
        ('Операционная система', {
            'fields': ('os_choice', 'os_custom'),
            'description': 'Выберите операционную систему из списка или укажите свою'
        }),
        ('Дополнительно', {
            'fields': ('has_webcam', 'has_microphone')
        }),
    )

    class Media:
        js = ('js/computer_admin.js',)
        css = {
            'all': ('css/computer_admin.css',)
        }

    def get_inventory_number(self, obj):
        return obj.device.inventory_number
    get_inventory_number.short_description = 'Инвентарный номер'

    def get_hall(self, obj):
        return obj.device.hall
    get_hall.short_description = 'Зал'

    def get_status(self, obj):
        return obj.device.get_status_display()
    get_status.short_description = 'Статус'

    def get_os_display(self, obj):
        return obj.os
    get_os_display.short_description = 'ОС'

    def save_model(self, request, obj, form, change):
        if change:
            device = obj.device
            device.hall = form.cleaned_data['hall']
            device.status = form.cleaned_data['status']
            device.spot = form.cleaned_data.get('spot')
            device.save()
            obj.os = form.cleaned_data['os']
            obj.save()
        else:
            # При создании форма уже всё сохраняет
            form.save(commit=True)


# ---------- Админ-класс для консолей ----------
@admin.register(Console)
class ConsoleAdmin(admin.ModelAdmin):
    form = ConsoleCreationForm
    list_display = ('device', 'console_type', 'controller_count', 'get_inventory_number', 'get_hall', 'get_status')
    list_filter = ('device__hall', 'device__status', 'console_type')
    search_fields = ('device__inventory_number', 'console_type')
    raw_id_fields = ('device',)
    readonly_fields = ('device',)

    fieldsets = (
        ('Общая информация', {
            'fields': ('hall', 'spot', 'status')
        }),
        ('Характеристики консоли', {
            'fields': ('console_type', 'controller_count', 'storage_gb')
        }),
        ('Дополнительно', {
            'fields': ('has_kinect', 'has_vr_support')
        }),
    )

    class Media:
        js = ('js/console_admin.js',)

    def get_inventory_number(self, obj):
        return obj.device.inventory_number
    get_inventory_number.short_description = 'Инвентарный номер'

    def get_hall(self, obj):
        return obj.device.hall
    get_hall.short_description = 'Зал'

    def get_status(self, obj):
        return obj.device.get_status_display()
    get_status.short_description = 'Статус'

    def save_model(self, request, obj, form, change):
        if change:
            device = obj.device
            device.hall = form.cleaned_data['hall']
            device.status = form.cleaned_data['status']
            device.spot = form.cleaned_data.get('spot')
            device.save()
            obj.save()
        else:
            form.save(commit=True)