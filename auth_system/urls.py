"""
URL configuration for auth_system project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from core.views import (
    RegisterView, LoginView, ProfileView, DeleteAccountView, LogoutView,
    AdminRulesView, ProductsMockView, OrdersMockView, ShopsMockView
)

urlpatterns = [
    path('admin/', admin.site.urls),

    # Аутентификация
    path('api/register/', RegisterView.as_view(), name='register'),
    path('api/login/', LoginView.as_view(), name='login'),
    path('api/profile/', ProfileView.as_view(), name='profile'),
    path('api/delete-account/', DeleteAccountView.as_view(), name='delete_account'),
    path('api/logout/', LogoutView.as_view(), name='logout'),

    # Админка правил доступа
    path('api/admin/rules/', AdminRulesView.as_view(), name='admin_rules_list'),
    path('api/admin/rules/<int:pk>/', AdminRulesView.as_view(), name='admin_rules_detail'),

    # Mock-объекты
    path('api/mock/products/', ProductsMockView.as_view(), name='mock_products'),
    path('api/mock/orders/', OrdersMockView.as_view(), name='mock_orders'),
    path('api/mock/shops/', ShopsMockView.as_view(), name='mock_shops'),
]