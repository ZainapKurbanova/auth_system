from rest_framework import serializers
from .models import User, AccessRoleRule, Role, BusinessElement
import bcrypt

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)  # Пароль только для записи
    password_confirm = serializers.CharField(write_only=True)  # Повтор пароля

    class Meta:
        model = User
        fields = ['id', 'first_name', 'last_name', 'patronymic', 'email', 'password', 'password_confirm']
        read_only_fields = ['id']  # ID только для чтения

    def validate(self, data):
        # Валидация: пароли совпадают
        if data.get('password') != data.get('password_confirm'):
            raise serializers.ValidationError({"password": "Passwords do not match"})
        return data

    def create(self, validated_data):
        # Хэшируем пароль
        password = validated_data.pop('password')
        validated_data.pop('password_confirm')  # Удаляем повтор
        hash_pass = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        user = User.objects.create(password_hash=hash_pass, **validated_data)
        return user

    def update(self, instance, validated_data):
        # Обновление: Если пароль, хэшируем
        if 'password' in validated_data:
            password = validated_data.pop('password')
            validated_data.pop('password_confirm')
            instance.password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance

class AccessRoleRuleSerializer(serializers.ModelSerializer):
    role_name = serializers.ReadOnlyField(source='role.name')
    element_name = serializers.ReadOnlyField(source='element.name')

    class Meta:
        model = AccessRoleRule
        fields = '__all__'  # Все поля, плюс read-only