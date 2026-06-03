from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import MinValueValidator   # ← добавить
from django.db.models.signals import post_save
from django.dispatch import receiver

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

class UserBalance(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='balance')
    balance = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00,
        validators=[MinValueValidator(0)]
    )
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} — {self.balance} руб."

    class Meta:
        verbose_name = 'Баланс пользователя'
        verbose_name_plural = 'Балансы пользователей'

# Сигнал для автоматического создания баланса при регистрации
@receiver(post_save, sender=CustomUser)
def create_user_balance(sender, instance, created, **kwargs):
    if created:
        UserBalance.objects.create(user=instance)