from django.db import models
from django.utils import timezone
from simple_history.models import HistoricalRecords

class DataCenter(models.Model):
    """数据中心模型"""
    name = models.CharField('名称', max_length=50, unique=True)
    location = models.CharField('位置', max_length=100)
    contact_name = models.CharField('联系人', max_length=50)
    contact_phone = models.CharField('联系电话', max_length=20)
    area = models.DecimalField('面积(平方米)', max_digits=10, decimal_places=2)
    power_capacity = models.DecimalField('电力容量(KW)', max_digits=10, decimal_places=2)
    cooling_capacity = models.DecimalField('制冷能力(KW)', max_digits=10, decimal_places=2)
    created_time = models.DateTimeField('创建时间', default=timezone.now)
    updated_time = models.DateTimeField('更新时间', auto_now=True)
    
    # 添加历史记录配置
    history = HistoricalRecords(
        verbose_name='历史记录',
        verbose_name_plural='历史记录',
        excluded_fields=['created_time', 'updated_time'],  # 排除这些字段的变更记录
        table_name='assets_datacenter_history'  # 指定历史记录表名
    )

    class Meta:
        verbose_name = '数据中心'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name

    def get_field_verbose_name(self, field_name):
        """获取字段的中文名称"""
        return self._meta.get_field(field_name).verbose_name