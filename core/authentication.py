# core/authentication.py

import jwt
from django.conf import settings
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
# Импорт вашей кастомной модели User
from .models import User


class JWTAuthentication(BaseAuthentication):
    """
    Кастомный класс аутентификации DRF для обработки Bearer JWT.
    """

    def authenticate(self, request):
        auth_header = request.headers.get('Authorization')

        # 1. Проверка наличия заголовка
        if not auth_header or not auth_header.startswith('Bearer '):
            # Важно: Возвращаем None. DRF интерпретирует это как
            # "аутентификация не выполнена" и переходит к проверке permissions.
            return None

        token = auth_header.split(' ')[1]

        try:
            # 2. Декодирование токена
            payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=['HS256'])
            user_id = payload.get('user_id')

            # 3. Получение пользователя (только активного)
            user = User.objects.get(id=user_id, is_active=True)

            # 4. Успешный результат: Возвращаем кортеж (пользователь, токен)
            return (user, token)

        except jwt.ExpiredSignatureError:
            # Бросаем исключение DRF, которое будет преобразовано в ответ 401
            raise AuthenticationFailed('Token has expired')
        except (jwt.InvalidTokenError, User.DoesNotExist, jwt.InvalidSignatureError):
            raise AuthenticationFailed('Invalid token or user not found')
        except Exception as e:
            # Обработка других ошибок (например, проблема с JWT_SECRET_KEY)
            raise AuthenticationFailed(f'Authentication failed: {e}')