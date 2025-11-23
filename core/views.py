from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.http import JsonResponse
import jwt
from django.conf import settings
from datetime import datetime, timedelta
import bcrypt

from .models import User, AccessRoleRule, BusinessElement
from .serializers import UserSerializer, AccessRoleRuleSerializer
from rest_framework.permissions import IsAuthenticated # <-- Новый импорт
from .authentication import JWTAuthentication

# ===================== АУТЕНТИФИКАЦИЯ =====================
class RegisterView(APIView):
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response({"message": "User created", "user_id": user.id}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')
        try:
            user = User.objects.get(email=email, is_active=True)
            if bcrypt.checkpw(password.encode('utf-8'), user.password_hash.encode('utf-8')):
                payload = {
                    'user_id': user.id,
                    'exp': datetime.utcnow() + timedelta(hours=24),
                    'iat': datetime.utcnow()
                }
                token = jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm='HS256')
                return Response({"token": token}, status=status.HTTP_200_OK)
            else:
                return Response({"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)
        except User.DoesNotExist:
            return Response({"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)

# core/views.py

class ProfileView(APIView):
    # 🔥 Добавляем классы аутентификации и разрешений 🔥
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Ручная проверка 'if not request.user:' больше не нужна.
        serializer = UserSerializer(request.user)
        return Response(serializer.data)

    def put(self, request):
        # Ручная проверка 'if not request.user:' больше не нужна.
        serializer = UserSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Profile updated"})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# core/views.py

class DeleteAccountView(APIView):
    # 🔥 Добавляем классы аутентификации и разрешений 🔥
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def delete(self, request):
        # 🔥 Ручная проверка "if not request.user:" БОЛЬШЕ НЕ НУЖНА 🔥
        # IsAuthenticated уже гарантировал, что request.user — это реальный User.

        # Проверка is_active также не нужна, т.к. JWTAuthentication ищет только активных.

        # Логика мягкого удаления (теперь она гарантированно сработает)
        request.user.is_active = False
        request.user.save()

        return Response({"message": "Account deactivated"}, status=status.HTTP_200_OK)

class LogoutView(APIView):
    def post(self, request):
        # JWT — stateless, клиент просто удаляет токен
        return Response({"message": "Logged out successfully"}, status=status.HTTP_200_OK)


# ===================== АВТОРИЗАЦИЯ =====================
def check_permission(request, element_name: str, action: str) -> bool:
    """
    Проверяет, есть ли у пользователя право на действие с элементом.
    action: 'read', 'read_all', 'create', 'update', 'update_all', 'delete', 'delete_all'
    """
    if not request.user or not request.user.is_active or not request.user.role:
        return False

    try:
        rule = AccessRoleRule.objects.get(
            role=request.user.role,
            element__name=element_name
        )
        # Словарь соответствия action → поле в модели
        permissions = {
            'read': rule.read_permission or rule.read_all_permission,
            'read_all': rule.read_all_permission,
            'create': rule.create_permission,
            'update': rule.update_permission or rule.update_all_permission,
            'update_all': rule.update_all_permission,
            'delete': rule.delete_permission or rule.delete_all_permission,
            'delete_all': rule.delete_all_permission,
        }
        return permissions.get(action, False)
    except AccessRoleRule.DoesNotExist:
        return False


# ===================== ADMIN API (управление правилами) =====================
class AdminRulesView(APIView):
    def get(self, request):
        if not request.user or not request.user.role or request.user.role.name != 'admin':
            return Response({"error": "Forbidden"}, status=status.HTTP_403_FORBIDDEN)
        rules = AccessRoleRule.objects.all()
        serializer = AccessRoleRuleSerializer(rules, many=True)
        return Response(serializer.data)

    def post(self, request):
        if not request.user or not request.user.role or request.user.role.name != 'admin':
            return Response({"error": "Forbidden"}, status=status.HTTP_403_FORBIDDEN)
        serializer = AccessRoleRuleSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, pk):
        if not request.user or not request.user.role or request.user.role.name != 'admin':
            return Response({"error": "Forbidden"}, status=status.HTTP_403_FORBIDDEN)
        try:
            rule = AccessRoleRule.objects.get(pk=pk)
        except AccessRoleRule.DoesNotExist:
            return Response({"error": "Rule not found"}, status=status.HTTP_404_NOT_FOUND)
        serializer = AccessRoleRuleSerializer(rule, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        if not request.user or not request.user.role or request.user.role.name != 'admin':
            return Response({"error": "Forbidden"}, status=status.HTTP_403_FORBIDDEN)
        try:
            rule = AccessRoleRule.objects.get(pk=pk)
            rule.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except AccessRoleRule.DoesNotExist:
            return Response({"error": "Rule not found"}, status=status.HTTP_404_NOT_FOUND)


# ===================== MOCK ВЬЮХИ (бизнес-объекты) =====================
class ProductsMockView(APIView):
    def get(self, request):
        if not check_permission(request, 'products', 'read'):
            return Response({"error": "Forbidden"}, status=status.HTTP_403_FORBIDDEN)
        return Response({"message": "Access granted to products", "data": ["product1", "product2", "product3"]})

    def post(self, request):
        if not check_permission(request, 'products', 'create'):
            return Response({"error": "Forbidden"}, status=status.HTTP_403_FORBIDDEN)
        return Response({"message": "Product created (mock)"}, status=status.HTTP_201_CREATED)


class OrdersMockView(APIView):
    def get(self, request):
        if not check_permission(request, 'orders', 'read'):
            return Response({"error": "Forbidden"}, status=status.HTTP_403_FORBIDDEN)
        return Response({"message": "Access granted to orders", "data": ["order101", "order102"]})


class ShopsMockView(APIView):
    def get(self, request):
        if not check_permission(request, 'shops', 'read'):
            return Response({"error": "Forbidden"}, status=status.HTTP_403_FORBIDDEN)
        return Response({"message": "Access granted to shops", "data": ["shopA", "shopB"]})