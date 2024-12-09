from django.db import models
from django.utils import timezone

class Server(models.Model):
    STATUS_CHOICES = [
        ('running', '运行中'),
        ('stopped', '已停止'),
        ('maintenance', '维护中'),
        ('fault', '故障'),
    ]
    
    name = models.CharField('名称', max_length=100)
    hostname = models.CharField('主机名', max_length=100)
    ip_address = models.GenericIPAddressField('IP地址')
    mac_address = models.CharField('MAC地址', max_length=17)
    status = models.CharField('状态', max_length=20, choices=STATUS_CHOICES, default='running')
    data_center = models.ForeignKey('DataCenter', on_delete=models.CASCADE, verbose_name='所属数据中心')
    manufacturer = models.CharField('制造商', max_length=50)
    model = models.CharField('型号', max_length=50)
    sn = models.CharField('序列号', max_length=100)
    purchase_date = models.DateField('采购日期')
    warranty_date = models.DateField('保修期限')
    rack_position = models.CharField('机架位置', max_length=50)
    os_type = models.CharField('操作系统', max_length=50)
    os_version = models.CharField('系统版本', max_length=50)
    cpu_model = models.CharField('CPU型号', max_length=100)
    cpu_count = models.IntegerField('CPU数量')
    cpu_cores = models.IntegerField('CPU核心数')
    memory_size = models.IntegerField('内存大小(GB)')
    disk_info = models.TextField('磁盘信息')
    business_system = models.CharField('业务系统', max_length=100)
    description = models.TextField('描述', blank=True)
    created_time = models.DateTimeField('创建时间', default=timezone.now)
    updated_time = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        verbose_name = '服务器'
        verbose_name_plural = verbose_name
        ordering = ['-created_time']

    def __str__(self):
        return self.name 