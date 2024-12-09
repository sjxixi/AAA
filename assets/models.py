from django.db import models
from django.utils import timezone

class BaseDevice(models.Model):
    """设备基类"""
    STATUS_CHOICES = [
        ('running', '运行中'),
        ('stopped', '已停止'),
        ('maintenance', '维护中'),
        ('fault', '故障'),
    ]

    name = models.CharField('名称', max_length=50)
    # ... 其他字段 ...
    status = models.CharField(
        '状态',
        max_length=20,
        choices=STATUS_CHOICES,
        default='running'
    )

    class Meta:
        abstract = True

class DataCenter(models.Model):
    name = models.CharField('名称', max_length=50, unique=True)
    location = models.CharField('位置', max_length=100)
    contact_name = models.CharField('联系人', max_length=50)
    contact_phone = models.CharField('联系电话', max_length=20)
    area = models.DecimalField('面积(平方米)', max_digits=10, decimal_places=2)
    power_capacity = models.DecimalField('电力容量(KW)', max_digits=10, decimal_places=2)
    cooling_capacity = models.DecimalField('制冷能力(KW)', max_digits=10, decimal_places=2)
    created_time = models.DateTimeField('创建时间', default=timezone.now)
    updated_time = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        verbose_name = '数据中心'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name 