from django.apps import AppConfig


class AccountsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'accounts'
    verbose_name = '用户管理'
    path = 'D:\\python_file\\2\\AAA\\accounts'  # 请确保这是正确的路径 