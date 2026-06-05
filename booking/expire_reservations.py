from django.core.management.base import BaseCommand
from django.utils import timezone

from booking.models import Reservation


class Command(BaseCommand):
    help = 'Expire reservations that passed their expire time'

    def handle(self, *args, **options):
        now = timezone.now()
        qs = Reservation.objects.filter(status='active', expires_at__lte=now)
        count = qs.count()
        for r in qs:
            r.expire()
        self.stdout.write(self.style.SUCCESS(f'Expired {count} reservations'))
