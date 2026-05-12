from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    phone = models.CharField(max_length=16, verbose_name='Телефон',unique=True)
    email = models.EmailField(verbose_name='Email' ,unique=True)

    def __str__(self):
        return self.username