from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError
import re
from .models import CustomUser

class RegisterForm(UserCreationForm):
    phone = forms.CharField(label='Телефон', max_length=16)
    email = forms.EmailField(label='Email')

    class Meta:
        model = CustomUser
        fields = ('username', 'phone', 'email', 'password1', 'password2')
        labels = {
            'username': 'Логин'
        }

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if not re.fullmatch(r'[A-Za-z0-9]+', username):
            raise ValidationError('Логин должен содержать только латинские буквы и цифры')
        if CustomUser.objects.filter(username=username).exists():
            raise ValidationError('Пользователь с таким логином уже существует')
        return username

    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        match = re.fullmatch(r'8\((\d{3})\)(\d{3})-(\d{2})-(\d{2})', phone)
        if not match:
            raise ValidationError('Телефон должен быть в формате 8(XXX)XXX-XX-XX')
        normalized = '+7' + match.group(1) + match.group(2) + match.group(3) + match.group(4)
        if CustomUser.objects.filter(phone=normalized).exists():
            raise ValidationError('Пользователь с таким телефоном уже существует')
        return normalized

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if CustomUser.objects.filter(email__iexact=email).exists():
            raise ValidationError('Пользователь с таким email уже существует')
        return email.lower()

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.phone = self.cleaned_data['phone']
        if commit:
            user.save()
        return user