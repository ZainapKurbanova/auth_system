from django.core.management.base import BaseCommand
from core.models import Role, BusinessElement, AccessRoleRule, User
import bcrypt


class Command(BaseCommand):
    help = 'Заполняет БД начальными правилами доступа и тестовыми пользователями'

    def handle(self, *args, **kwargs):
        # 1. Создаем Роли
        admin_role, _ = Role.objects.get_or_create(name='admin')
        user_role, _ = Role.objects.get_or_create(name='user')

        # 2. Создаем Ресурсы (то, что мы защищаем)
        products, _ = BusinessElement.objects.get_or_create(name='products')
        orders, _ = BusinessElement.objects.get_or_create(name='orders')
        shops, _ = BusinessElement.objects.get_or_create(name='shops')

        # 3. Создаем Правила (Связываем Роли и Ресурсы)

        # Правило: Админ может делать всё с заказами
        AccessRoleRule.objects.get_or_create(
            role=admin_role,
            element=orders,
            defaults={
                'read_permission': True, 'read_all_permission': True,
                'create_permission': True, 'update_permission': True,
                'delete_permission': True
            }
        )
        # Также дадим админу права на продукты и магазины
        AccessRoleRule.objects.get_or_create(role=admin_role, element=products,
                                             defaults={'read_permission': True, 'create_permission': True})
        AccessRoleRule.objects.get_or_create(role=admin_role, element=shops, defaults={'read_permission': True})

        # Правило: Обычный юзер может ТОЛЬКО ЧИТАТЬ заказы и магазины
        AccessRoleRule.objects.get_or_create(
            role=user_role,
            element=orders,
            defaults={'read_permission': True, 'create_permission': False}
        )
        AccessRoleRule.objects.get_or_create(
            role=user_role,
            element=shops,
            defaults={'read_permission': True}
        )

        # 4. Создаем Пользователей
        # Пароль '12345'
        hashed_pw = bcrypt.hashpw('12345'.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

        if not User.objects.filter(email='admin@test.com').exists():
            User.objects.create(
                email='admin@test.com', password_hash=hashed_pw, role=admin_role, first_name='Admin'
            )
            self.stdout.write('Создан пользователь: admin@test.com / 12345')

        if not User.objects.filter(email='user@test.com').exists():
            User.objects.create(
                email='user@test.com', password_hash=hashed_pw, role=user_role, first_name='Simple User'
            )
            self.stdout.write('Создан пользователь: user@test.com / 12345')

        self.stdout.write(self.style.SUCCESS('База данных успешно инициализирована!'))