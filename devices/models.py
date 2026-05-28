from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.auth.models import AbstractUser
from django.db.models.signals import post_save
from django.dispatch import receiver


class Hall(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name="Название зала")
    description = models.TextField(blank=True, null=True, verbose_name="Описание")
    max_capacity = models.PositiveIntegerField(
        validators=[MinValueValidator(1)],
        verbose_name="Максимальная вместимость"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")

    class Meta:
        db_table = 'halls'
        verbose_name = "Зал"
        verbose_name_plural = "Залы"
        ordering = ['name']

    def __str__(self):
        return self.name


class Spot(models.Model):
    """Место (нумерованное) внутри зала."""
    hall = models.ForeignKey(
        Hall,
        on_delete=models.CASCADE,
        related_name='spots',
        verbose_name="Зал"
    )
    number = models.PositiveIntegerField(verbose_name="Номер места")

    class Meta:
        db_table = 'spots'
        unique_together = ('hall', 'number')
        ordering = ['hall', 'number']
        verbose_name = "Место"
        verbose_name_plural = "Места"

    def __str__(self):
        return f"{self.hall.name} – место {self.number}"


@receiver(post_save, sender=Hall)
def create_spots_for_hall(sender, instance, created, **kwargs):
    """При сохранении зала автоматически создаёт/удаляет места по max_capacity."""
    # Удаляем лишние места, если вместимость уменьшена
    Spot.objects.filter(hall=instance, number__gt=instance.max_capacity).delete()
    # Создаём недостающие
    existing = set(Spot.objects.filter(hall=instance).values_list('number', flat=True))
    for n in range(1, instance.max_capacity + 1):
        if n not in existing:
            Spot.objects.create(hall=instance, number=n)


class Device(models.Model):
    class DeviceType(models.TextChoices):
        COMPUTER = 'computer', 'Компьютер'
        CONSOLE = 'console', 'Консоль'

    class DeviceStatus(models.TextChoices):
        AVAILABLE = 'available', 'Доступно'
        IN_USE = 'in_use', 'Используется'
        MAINTENANCE = 'maintenance', 'Обслуживание'
        RESERVED = 'reserved', 'Забронировано'

    hall = models.ForeignKey(
        Hall,
        on_delete=models.PROTECT,
        related_name='devices',
        verbose_name="Зал"
    )
    spot = models.OneToOneField(
        Spot,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='device',
        verbose_name="Место в зале"
    )
    device_type = models.CharField(
        max_length=20,
        choices=DeviceType.choices,
        verbose_name="Тип устройства"
    )
    status = models.CharField(
        max_length=20,
        choices=DeviceStatus.choices,
        default=DeviceStatus.AVAILABLE,
        verbose_name="Статус"
    )
    inventory_number = models.CharField(
        max_length=50,
        unique=True,
        blank=True,
        verbose_name="Инвентарный номер"
    )

    def save(self, *args, **kwargs):
        # Генерация инвентарного номера на основе pk (без гонки)
        if not self.inventory_number and self.pk is None:
            # Сначала сохраняем, чтобы получить pk
            super().save(*args, **kwargs)
            self.inventory_number = f"DEV-{self.pk:05d}"
            # Сохраняем номер, не затрагивая остальные поля
            super().save(update_fields=['inventory_number'])
        else:
            super().save(*args, **kwargs)

    class Meta:
        db_table = 'devices'
        verbose_name = "Устройство"
        verbose_name_plural = "Устройства"
        ordering = ['hall', 'inventory_number']

    def __str__(self):
        return f"{self.get_device_type_display()} - {self.inventory_number}"


class Computer(models.Model):
    device = models.OneToOneField(
        Device,
        on_delete=models.CASCADE,
        primary_key=True,
        related_name='computer_details',
        verbose_name="Устройство"
    )
    cpu = models.CharField(max_length=100, verbose_name="Процессор")
    gpu = models.CharField(max_length=100, verbose_name="Видеокарта")
    ram_gb = models.PositiveIntegerField(
        validators=[MinValueValidator(1)],
        verbose_name="ОЗУ (ГБ)"
    )
    storage_gb = models.PositiveIntegerField(
        validators=[MinValueValidator(1)],
        verbose_name="Накопитель (ГБ)"
    )
    os = models.CharField(max_length=100, default="Windows 11", verbose_name="Операционная система")
    has_webcam = models.BooleanField(default=False, verbose_name="Наличие веб-камеры")
    has_microphone = models.BooleanField(default=False, verbose_name="Наличие микрофона")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")

    class Meta:
        db_table = 'computers'
        verbose_name = "Компьютер"
        verbose_name_plural = "Компьютеры"

    def __str__(self):
        return f"Computer: {self.device.inventory_number} - {self.cpu}"


class Console(models.Model):
    class ConsoleType(models.TextChoices):
        PS5 = 'ps5', 'PlayStation 5'
        PS4 = 'ps4', 'PlayStation 4'
        XBOX_SERIES_X = 'xbox_series_x', 'Xbox Series X'
        XBOX_SERIES_S = 'xbox_series_s', 'Xbox Series S'
        XBOX_ONE = 'xbox_one', 'Xbox One'
        NINTENDO_SWITCH = 'nintendo_switch', 'Nintendo Switch'
        NINTENDO_SWITCH_LITE = 'nintendo_switch_lite', 'Nintendo Switch Lite'

    device = models.OneToOneField(
        Device,
        on_delete=models.CASCADE,
        primary_key=True,
        related_name='console_details',
        verbose_name="Устройство"
    )
    console_type = models.CharField(
        max_length=30,
        choices=ConsoleType.choices,
        verbose_name="Тип консоли"
    )
    controller_count = models.PositiveIntegerField(
        default=2,
        validators=[MinValueValidator(1), MaxValueValidator(8)],
        verbose_name="Количество контроллеров"
    )
    has_kinect = models.BooleanField(default=False, verbose_name="Наличие Kinect/камеры")
    has_vr_support = models.BooleanField(default=False, verbose_name="Поддержка VR")
    storage_gb = models.PositiveIntegerField(
        default=500,
        verbose_name="Объем накопителя (ГБ)"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")

    class Meta:
        db_table = 'consoles'
        verbose_name = "Консоль"
        verbose_name_plural = "Консоли"

    def __str__(self):
        return f"{self.get_console_type_display()} - {self.device.inventory_number}"