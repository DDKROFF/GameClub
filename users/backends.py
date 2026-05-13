import re
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model
import logging

logger = logging.getLogger(__name__)
User = get_user_model()


class MultiFieldAuthBackend(ModelBackend):
    def authenticate(self, request, identity=None, password=None, **kwargs):
        if identity is None or password is None:
            return None

        identity = identity.strip()

        try:
            # 1. Проверяем на email
            if re.match(r'^[^@]+@[^@]+\.[^@]+$', identity):
                try:
                    user = User.objects.get(email__iexact=identity)
                except User.DoesNotExist:
                    return None
                except User.MultipleObjectsReturned:
                    logger.error(f"Multiple users found with email: {identity}")
                    return None

            # 2. Проверяем на телефон
            elif re.match(r'^(\+7|8)?[\s\-]?\(?\d{3}\)?[\s\-]?\d{3}[\s\-]?\d{2}[\s\-]?\d{2}$', identity):
                # Очищаем от лишних символов
                phone = re.sub(r'[\s\-\(\)]', '', identity)
                # Приводим к формату +7XXXXXXXXXX
                if phone.startswith('8'):
                    phone = '+7' + phone[1:]
                elif not phone.startswith('+'):
                    phone = '+7' + phone

                try:
                    user = User.objects.get(phone=phone)
                except User.DoesNotExist:
                    return None
                except User.MultipleObjectsReturned:
                    logger.error(f"Multiple users found with phone: {phone}")
                    return None

            # 3. Иначе ищем по username
            else:
                try:
                    user = User.objects.get(username__iexact=identity)
                except User.DoesNotExist:
                    return None
                except User.MultipleObjectsReturned:
                    logger.error(f"Multiple users found with username: {identity}")
                    return None

            # Проверяем пароль и активность пользователя
            if user.check_password(password) and self.user_can_authenticate(user):
                return user

        except Exception as e:
            logger.error(f"Authentication error: {e}")
            return None

        return None