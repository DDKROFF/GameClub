import re
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model

User = get_user_model()

class MultiFieldAuthBackend(ModelBackend):
    def authenticate(self, request, identity=None, password=None, **kwargs):
        if identity is None or password is None:
            return None

        identity = identity.strip()

        # 1. Проверяем на email
        if re.match(r'^[^@]+@[^@]+\.[^@]+$', identity):
            try:
                user = User.objects.get(email__iexact=identity)
            except User.DoesNotExist:
                return None
        # 2. Проверяем на телефон (строка из + и 11 цифр)
        elif re.match(r'^\+7\d{10}$', identity):
            try:
                user = User.objects.get(phone=identity)
            except User.DoesNotExist:
                return None
        # 3. Иначе считаем логином (username)
        else:
            try:
                user = User.objects.get(username=identity)
            except User.DoesNotExist:
                return None

        if user.check_password(password) and self.user_can_authenticate(user):
            return user
        return None