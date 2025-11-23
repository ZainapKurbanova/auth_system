from django.db import models


class User(models.Model):
    first_name = models.CharField(max_length=100, blank=True)  # Имя
    last_name = models.CharField(max_length=100, blank=True)  # Фамилия
    patronymic = models.CharField(max_length=100, blank=True)  # Отчество (опционально)
    email = models.EmailField(unique=True)  # Email, уникальный
    password_hash = models.CharField(max_length=255)  # Хэш пароля (bcrypt)
    is_active = models.BooleanField(default=True)  # Статус для мягкого удаления
    role = models.ForeignKey('Role', on_delete=models.SET_NULL, null=True, blank=True)  # Роль пользователя

    def __str__(self):
        return self.email

    # =========================================================
    # 🔥 СВОЙСТВА ДЛЯ СОВМЕСТИМОСТИ С DJANGO/DRF 🔥
    # =========================================================
    @property
    def is_authenticated(self):
        """
        Все экземпляры нашей модели User считаются аутентифицированными.
        Используется классом rest_framework.permissions.IsAuthenticated.
        """
        return True

    @property
    def is_anonymous(self):
        """
        Все экземпляры нашей модели User не являются анонимными.
        """
        return False

    @property
    def is_staff(self):
        """
        Определяет, является ли пользователь сотрудником (админом).
        Полезно для интеграции с другими компонентами Django.
        """
        return self.role.name == 'admin' if self.role else False

    def get_username(self):
        """
        Метод, который Django ожидает для получения имени пользователя.
        """
        return self.email
    # =========================================================


class Role(models.Model):
    name = models.CharField(max_length=50, unique=True)  # Название роли, уникальное

    def __str__(self):
        return self.name


class BusinessElement(models.Model):
    name = models.CharField(max_length=100, unique=True)  # Название элемента (e.g., 'products')

    def __str__(self):
        return self.name


class AccessRoleRule(models.Model):
    role = models.ForeignKey(Role, on_delete=models.CASCADE)  # Ссылка на роль
    element = models.ForeignKey(BusinessElement, on_delete=models.CASCADE)  # Ссылка на элемент
    read_permission = models.BooleanField(default=False)  # Читать свой
    read_all_permission = models.BooleanField(default=False)  # Читать все
    create_permission = models.BooleanField(default=False)  # Создавать
    update_permission = models.BooleanField(default=False)  # Обновлять свой
    update_all_permission = models.BooleanField(default=False)  # Обновлять все
    delete_permission = models.BooleanField(default=False)  # Удалять свой
    delete_all_permission = models.BooleanField(default=False)  # Удалять все

    class Meta:
        unique_together = ('role', 'element')  # Уникальность комбинации роль+элемент

    def __str__(self):
        return f"{self.role.name} - {self.element.name}"