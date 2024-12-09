from django.contrib.auth.models import AbstractUser, Permission
from django.db import models
from django.contrib.contenttypes.models import ContentType
from assets.models import DataCenter

class User(AbstractUser):
    USER_TYPE_CHOICES = [
        ('admin', '管理员'),
        ('user', '普通用户'),
    ]
    
    phone = models.CharField('手机号', max_length=11, blank=True)
    department = models.CharField('部门', max_length=50, blank=True)
    position = models.CharField('职位', max_length=50, blank=True)
    user_type = models.CharField('用户类型', max_length=10, choices=USER_TYPE_CHOICES, default='user')
    data_centers = models.ManyToManyField(
        DataCenter,
        verbose_name='可访问的数据中心',
        blank=True,
        related_name='users'
    )
    created_time = models.DateTimeField('创建时间', auto_now_add=True)
    updated_time = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        verbose_name = '用户'
        verbose_name_plural = verbose_name
        ordering = ['-date_joined']
        swappable = 'AUTH_USER_MODEL'

    def __str__(self):
        return self.username

    @property
    def is_admin(self):
        """是否是管理员"""
        return self.user_type == 'admin' or self.is_superuser

    def has_datacenter_perm(self, datacenter_id):
        """检查用户是否有数据中心权限"""
        if self.is_admin:
            return True
        return self.data_centers.filter(id=datacenter_id).exists()

    def has_module_perms(self, app_label):
        """检查用户是否有指定应用的权限"""
        if self.is_admin:
            return True
        return super().has_module_perms(app_label)

    def has_perm(self, perm, obj=None):
        """检查用户是否有指定权限"""
        # 管理员拥有所有权限
        if self.is_admin:
            return True
        
        # 如果是检查具体对象的权限
        if obj and hasattr(obj, 'data_center'):
            # 先检查基本操作权限
            if not super().has_perm(perm):
                return False
            
            # 再检查数据中心权限
            return self.data_centers.filter(id=obj.data_center.id).exists()
        
        # 其他情况使用默认的权限检查
        return super().has_perm(perm)

    @classmethod
    def create_default_admin(cls):
        """创建默认管理员账户"""
        if not cls.objects.filter(username='admin').exists():
            admin = cls.objects.create_superuser(
                username='admin',
                email='admin@example.com',
                password='admin123456'
            )
            admin.user_type = 'admin'
            admin.is_staff = True
            admin.is_superuser = True
            admin.save()
            
            # 为管理员分配所有数据中心
            admin.data_centers.set(DataCenter.objects.all())
            return admin
        return None

    def can_edit_device(self, device):
        """检查用户是否可以编辑指定设备"""
        if self.is_admin:
            return True
            
        # 获取设备类型对应的权限
        model_name = device._meta.model_name
        perm = f'assets.change_{model_name}'
        
        # 检查基本权限
        if not super().has_perm(perm):
            return False
            
        # 检查数据中心权限
        return self.data_centers.filter(id=device.data_center.id).exists()