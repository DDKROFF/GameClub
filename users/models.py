from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    phone = models.CharField(
        max_length=16,
        verbose_name='Телефон',
        unique=True,
    )
    email = models.EmailField(
        verbose_name='Email',
        unique=True,
    )
    # Новые поля
    birth_date = models.DateField(
        verbose_name='Дата рождения',
        null=True,
        blank=True,
        help_text='Формат: ГГГГ-ММ-ДД'
    )
    STATUS_CHOICES = [
        ('active', 'Активен'),
        ('blocked', 'Заблокирован'),
        ('on_hold', 'На удержании'),
    ]
    account_status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='active',
        verbose_name='Статус учётной записи'
    )

    def __str__(self):
        return self.username

    class Meta:
        permissions = [
            ("can_book_computer", "Может бронировать компьютер"),
            ("manage_tariffs", "Управляет тарифами"),
            ("view_analytics", "Просматривает аналитику"),
        ]