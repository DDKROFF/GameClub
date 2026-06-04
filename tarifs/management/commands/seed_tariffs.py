from decimal import Decimal
from django.core.management.base import BaseCommand
from faker import Faker
from tarifs.models import Tariff

fake = Faker('ru_RU')

class Command(BaseCommand):
    help = 'Заполняет базу тестовыми данными (залы, места, устройства, тарифы, новости)'

    def handle(self, *args, **options):
        self.stdout.write('Начало наполнения тарифов...')

        self.clean_old_data()

        self.create_tariffs()

        self.stdout.write(self.style.SUCCESS('База данных успешно наполнена!'))

    def clean_old_data(self):
        Tariff.objects.all().delete()
        self.stdout.write('Старые данные удалены.')

    def create_tariffs(self):

        tariffs_data = []

        base_price_normal = Decimal('90')
        base_price_vip = Decimal('150')

        tariffs_data.append({
            'name': 'Стандарт (обычный зал, час)',
            'tariff_type': 'hourly',
            'price': base_price_normal,
            'fixed_duration_hours': None,
            'device_type': 'computer',
            'description': 'Оплата поминутно. 1.5 руб/мин. Подходит для быстрой игры.'
        })
        tariffs_data.append({
            'name': 'VIP (премиум зал, час)',
            'tariff_type': 'hourly',
            'price': base_price_vip,
            'fixed_duration_hours': None,
            'device_type': 'computer',
            'description': 'VIP зона, лучшие кресла, повышенная скорость. 2.5 руб/мин.'
        })

        for hours, price_mul in [(1, 1), (3, 3), (8, 8)]:
            total_price = base_price_normal * price_mul
            tariffs_data.append({
                'name': f'{hours} час{"а" if hours>1 else ""} (обычный)',
                'tariff_type': 'fixed',
                'price': total_price,
                'fixed_duration_hours': hours,
                'device_type': 'computer',
                'description': f'Фиксированная сессия {hours} ч. Выгоднее почасового.'
            })

        night_price_normal = base_price_normal * 8 * Decimal('0.8')  # 20% скидка
        tariffs_data.append({
            'name': 'Ночной (обычный, 8ч)',
            'tariff_type': 'fixed',
            'price': night_price_normal.quantize(Decimal('1.00')),
            'fixed_duration_hours': 8,
            'device_type': 'computer',
            'description': 'С 22:00 до 06:00. Идеально для ночных клан-баттлов.'
        })

        for hours, price_mul in [(1, 1), (3, 3), (8, 8)]:
            total_price = base_price_vip * price_mul
            tariffs_data.append({
                'name': f'{hours} час{"а" if hours>1 else ""} (VIP)',
                'tariff_type': 'fixed',
                'price': total_price,
                'fixed_duration_hours': hours,
                'device_type': 'computer',
                'description': f'VIP сессия {hours} ч. Максимальный комфорт.'
            })
        night_price_vip = base_price_vip * 8 * Decimal('0.8')
        tariffs_data.append({
            'name': 'Ночной (VIP, 8ч)',
            'tariff_type': 'fixed',
            'price': night_price_vip.quantize(Decimal('1.00')),
            'fixed_duration_hours': 8,
            'device_type': 'computer',
            'description': 'VIP ночь с 22:00 до 06:00, особые условия.'
        })

        tariffs_data.append({
            'name': 'Консоль (обычный зал)',
            'tariff_type': 'hourly',
            'price': Decimal('300'),
            'fixed_duration_hours': None,
            'device_type': 'console',
            'description': 'PlayStation / Xbox, 2 геймпада в комплекте.'
        })

        tariffs_data.append({
            'name': 'Консоль VIP',
            'tariff_type': 'hourly',
            'price': Decimal('400'),
            'fixed_duration_hours': None,
            'device_type': 'console',
            'description': 'VIP зона с консолью, отдельный диван, 4 геймпада, VR.'
        })

        for tariff_data in tariffs_data:
            tariff, created = Tariff.objects.get_or_create(
                name=tariff_data['name'],
                defaults=tariff_data
            )
            if created:
                self.stdout.write(f'Создан тариф: {tariff.name}')