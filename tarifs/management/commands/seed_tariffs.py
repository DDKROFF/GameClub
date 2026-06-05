from decimal import Decimal
from django.core.management.base import BaseCommand
from tarifs.models import Tariff


class Command(BaseCommand):
    help = 'Создаёт 4 тарифа: Поминутный, (VIP) Поминутный, Консоль, (VIP) Консоль'

    def handle(self, *args, **options):
        self.stdout.write('Начало наполнения тарифов...')
        self.clean_old_data()
        self.create_tariffs()
        self.stdout.write(self.style.SUCCESS('Готово! Создано 4 тарифа.'))

    def clean_old_data(self):
        Tariff.objects.all().delete()
        self.stdout.write('Старые тарифы удалены.')

    def create_tariffs(self):
        tariffs = [
            {
                'name': 'Поминутный',
                'tariff_type': 'hourly',
                'price': Decimal('1.5'),
                'fixed_duration_hours': None,
                'device_type': 'computer',
                'description': 'Поминутная оплата в обычном зале. 1.5 руб/мин.',
            },
            {
                'name': '(VIP) Поминутный',
                'tariff_type': 'hourly',
                'price': Decimal('2.5'),
                'fixed_duration_hours': None,
                'device_type': 'computer',
                'description': 'Поминутная оплата в VIP-зоне. 2.5 руб/мин.',
            },
            {
                'name': 'Консоль',
                'tariff_type': 'fixed',
                'price': Decimal('300'),
                'fixed_duration_hours': Decimal('60.0'),   # 1 час = 60 минут
                'device_type': 'console',
                'description': 'PlayStation 5, обычный зал. 300 руб/час.',
            },
            {
                'name': '(VIP) Консоль',
                'tariff_type': 'fixed',
                'price': Decimal('400'),
                'fixed_duration_hours': Decimal('60.0'),   # 1 час = 60 минут
                'device_type': 'console',
                'description': 'PlayStation 5, приватная комната с диваном.',
            },
        ]

        for data in tariffs:
            tariff, created = Tariff.objects.get_or_create(
                name=data['name'],
                defaults=data
            )
            if created:
                self.stdout.write(f'Создан тариф: {tariff.name}')