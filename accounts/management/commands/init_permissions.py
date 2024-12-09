from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from assets.models import DataCenter, Server, NetworkDevice, StorageDevice, SecurityDevice
from accounts.models import User

class Command(BaseCommand):
    help = '初始化用户权限和用户组'

    def handle(self, *args, **options):
        # 创建管理员组
        admin_group, _ = Group.objects.get_or_create(name='管理员组')
        # 创建普通用户组
        user_group, _ = Group.objects.get_or_create(name='普通用户组')

        # 设置权限映射
        model_perms = {
            DataCenter: ['view', 'add', 'change', 'delete'],
            Server: ['view', 'add', 'change', 'delete', 'export', 'import'],
            NetworkDevice: ['view', 'add', 'change', 'delete', 'export', 'import'],
            StorageDevice: ['view', 'add', 'change', 'delete', 'export', 'import'],
            SecurityDevice: ['view', 'add', 'change', 'delete', 'export', 'import'],
        }

        # 为管理员组分配所有权限
        for model, actions in model_perms.items():
            content_type = ContentType.objects.get_for_model(model)
            for action in actions:
                codename = f'{action}_{model._meta.model_name}'
                try:
                    perm = Permission.objects.get(
                        codename=codename,
                        content_type=content_type,
                    )
                    admin_group.permissions.add(perm)
                except Permission.DoesNotExist:
                    self.stdout.write(f'权限不存在: {codename}')

        # 为普通用户组分配基本查看权限
        for model in model_perms.keys():
            content_type = ContentType.objects.get_for_model(model)
            perm = Permission.objects.get(
                codename=f'view_{model._meta.model_name}',
                content_type=content_type,
            )
            user_group.permissions.add(perm)

        self.stdout.write(self.style.SUCCESS('成功初始化权限和用户组')) 