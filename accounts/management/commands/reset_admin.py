from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

User = get_user_model()

class Command(BaseCommand):
    help = '重置管理员密码'

    def add_arguments(self, parser):
        parser.add_argument('--password', type=str, help='新密码')

    def handle(self, *args, **options):
        try:
            admin = User.objects.get(username='admin')
            password = options['password'] or 'admin123456'
            admin.set_password(password)
            admin.save()
            self.stdout.write(self.style.SUCCESS(f'管理员密码已重置为: {password}'))
        except User.DoesNotExist:
            self.stdout.write(self.style.ERROR('管理员用户不存在')) 