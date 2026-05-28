import random
from django.core.management.base import BaseCommand
from faker import Faker
from devices.models import Hall, Spot, Device, Computer, Console  # замените на ваш путь

fake = Faker()

# Наборы правдоподобных процессоров и видеокарт для двух уровней
MID_CPU = [
    "Intel Core i5-11400", "Intel Core i5-12400F", "AMD Ryzen 5 5600",
    "AMD Ryzen 5 3600", "Intel Core i5-10400F", "Intel Core i5-10600K"
]
MID_GPU = [
    "NVIDIA GeForce GTX 1660 Super", "NVIDIA GeForce RTX 2060",
    "AMD Radeon RX 6600", "NVIDIA GeForce GTX 1070 Ti", "AMD Radeon RX 5600 XT"
]

HIGH_CPU = [
    "Intel Core i7-12700K", "Intel Core i9-11900K", "AMD Ryzen 7 5800X3D",
    "AMD Ryzen 9 5900X", "Intel Core i7-13700K", "AMD Ryzen 7 7700X"
]
HIGH_GPU = [
    "NVIDIA GeForce RTX 3080", "NVIDIA GeForce RTX 4070",
    "AMD Radeon RX 6900 XT", "NVIDIA GeForce RTX 3090", "AMD Radeon RX 7900 XT"
]


def random_computer_specs(tier='mid'):
    """Возвращает словарь с характеристиками ПК."""
    if tier == 'high':
        cpu = random.choice(HIGH_CPU)
        gpu = random.choice(HIGH_GPU)
        ram = random.choice([16, 32, 32, 64])
        storage = random.choice([1024, 2048, 1000])
        os_choice = random.choice(['windows_11', 'windows_10'])
    else:  # mid
        cpu = random.choice(MID_CPU)
        gpu = random.choice(MID_GPU)
        ram = random.choice([8, 16, 16, 32])
        storage = random.choice([512, 1024, 256])
        os_choice = random.choice(['windows_11', 'windows_10'])
    # разрешаем другое, если захочется – оставим как есть
    return {
        'cpu': cpu,
        'gpu': gpu,
        'ram_gb': ram,
        'storage_gb': storage,
        'os': os_choice,
        'has_webcam': random.choice([True, False]),
        'has_microphone': True,   # по заданию микрофоны у всех ПК
    }


class Command(BaseCommand):
    help = 'Заполняет залы и устройства согласно сценарию'

    def handle(self, *args, **options):
        # ---------- 1. Зал «Стандарт» ----------
        hall_std, created = Hall.objects.get_or_create(
            name='Стандарт',
            defaults={'description': 'Обычный зал', 'max_capacity': 13}
        )
        if not created:
            # если зал уже был, убедимся, что max_capacity = 13 (могут быть лишние места)
            hall_std.max_capacity = 13
            hall_std.save()  # сигнал пересоздаст Spot'ы

        # Места 1-10: компьютеры (средние)
        for spot_num in range(1, 11):
            spot = Spot.objects.get(hall=hall_std, number=spot_num)
            # создаём устройство
            device = Device.objects.create(
                hall=hall_std,
                spot=spot,
                device_type=Device.DeviceType.COMPUTER,
                status=Device.DeviceStatus.AVAILABLE,
            )
            specs = random_computer_specs(tier='mid')
            Computer.objects.create(device=device, **specs)

        # Места 11-12: PlayStation 5 (2 консоли)
        for spot_num in [11, 12]:
            spot = Spot.objects.get(hall=hall_std, number=spot_num)
            device = Device.objects.create(
                hall=hall_std,
                spot=spot,
                device_type=Device.DeviceType.CONSOLE,
                status=Device.DeviceStatus.AVAILABLE,
            )
            Console.objects.create(
                device=device,
                console_type=Console.ConsoleType.PS5,
                controller_count=2,
                has_kinect=False,
                has_vr_support=False,
                storage_gb=825  # стандартный SSD PS5
            )

        # Место 13: PlayStation 4
        spot = Spot.objects.get(hall=hall_std, number=13)
        device = Device.objects.create(
            hall=hall_std,
            spot=spot,
            device_type=Device.DeviceType.CONSOLE,
            status=Device.DeviceStatus.AVAILABLE,
        )
        Console.objects.create(
            device=device,
            console_type=Console.ConsoleType.PS4,
            controller_count=2,
            has_kinect=False,
            has_vr_support=False,
            storage_gb=500
        )

        # ---------- 2. Зал «VIP» ----------
        hall_vip, created = Hall.objects.get_or_create(
            name='VIP',
            defaults={'description': 'VIP-зал для турниров', 'max_capacity': 12}
        )
        if not created:
            hall_vip.max_capacity = 12
            hall_vip.save()

        # Места 1-5: компьютеры (высокая производительность)
        for spot_num in range(1, 6):
            spot = Spot.objects.get(hall=hall_vip, number=spot_num)
            device = Device.objects.create(
                hall=hall_vip,
                spot=spot,
                device_type=Device.DeviceType.COMPUTER,
                status=Device.DeviceStatus.AVAILABLE,
            )
            specs = random_computer_specs(tier='high')
            Computer.objects.create(device=device, **specs)

        # Место 6: консоль (пусть будет PS5)
        spot = Spot.objects.get(hall=hall_vip, number=6)
        device = Device.objects.create(
            hall=hall_vip,
            spot=spot,
            device_type=Device.DeviceType.CONSOLE,
            status=Device.DeviceStatus.AVAILABLE,
        )
        Console.objects.create(
            device=device,
            console_type=Console.ConsoleType.PS5,
            controller_count=2,
            storage_gb=825
        )

        # Места 7-11: компьютеры (высокая производительность)
        for spot_num in range(7, 12):
            spot = Spot.objects.get(hall=hall_vip, number=spot_num)
            device = Device.objects.create(
                hall=hall_vip,
                spot=spot,
                device_type=Device.DeviceType.COMPUTER,
                status=Device.DeviceStatus.AVAILABLE,
            )
            specs = random_computer_specs(tier='high')
            Computer.objects.create(device=device, **specs)

        # Место 12: консоль (например, Xbox Series X)
        spot = Spot.objects.get(hall=hall_vip, number=12)
        device = Device.objects.create(
            hall=hall_vip,
            spot=spot,
            device_type=Device.DeviceType.CONSOLE,
            status=Device.DeviceStatus.AVAILABLE,
        )
        Console.objects.create(
            device=device,
            console_type=Console.ConsoleType.XBOX_SERIES_X,
            controller_count=2,
            storage_gb=1024
        )

        # ---------- 3. Зал «Склад» ----------
        hall_stock, created = Hall.objects.get_or_create(
            name='Склад',
            defaults={'description': 'Резервное оборудование', 'max_capacity': 30}
        )
        if not created:
            hall_stock.max_capacity = 30
            hall_stock.save()

        # Одна Xbox Series S (место 1)
        spot = Spot.objects.get(hall=hall_stock, number=1)
        device = Device.objects.create(
            hall=hall_stock,
            spot=spot,
            device_type=Device.DeviceType.CONSOLE,
            status=Device.DeviceStatus.AVAILABLE,
        )
        Console.objects.create(
            device=device,
            console_type=Console.ConsoleType.XBOX_SERIES_S,
            controller_count=2,
            storage_gb=512
        )

        # Два-три компьютера (места 2, 3 и 4)
        for spot_num in [2, 3, 4]:
            spot = Spot.objects.get(hall=hall_stock, number=spot_num)
            device = Device.objects.create(
                hall=hall_stock,
                spot=spot,
                device_type=Device.DeviceType.COMPUTER,
                status=Device.DeviceStatus.AVAILABLE,
            )
            specs = random_computer_specs(tier='mid')
            Computer.objects.create(device=device, **specs)

        self.stdout.write(self.style.SUCCESS('Все устройства успешно созданы!'))