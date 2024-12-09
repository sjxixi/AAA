from django.db import models
from django.conf import settings
from django.utils import timezone
from simple_history.models import HistoricalRecords
from .datacenter import DataCenter

class Device(models.Model):
    """设备基类"""
    name = models.CharField('名称', max_length=100)
    model = models.CharField('型号', max_length=100)
    sn = models.CharField('序列号', max_length=100, unique=True)
    manufacturer = models.CharField('制造商', max_length=100)
    purchase_date = models.DateField('采购日期')
    warranty_date = models.DateField('保修期限')
    STATUS_CHOICES = [
        ('running', '运行中'),
        ('stopped', '已停止'),
        ('maintenance', '维护中'),
        ('fault', '故障'),
    ]

    status = models.CharField(
        '状态',
        max_length=20,
        choices=STATUS_CHOICES,
        default='running'
    )
    data_center = models.ForeignKey(DataCenter, on_delete=models.PROTECT, verbose_name='所属数据中心')
    rack_position = models.CharField('机架位置', max_length=50)
    ip_address = models.GenericIPAddressField('IP地址', unique=True)
    mac_address = models.CharField('MAC地址', max_length=17, unique=True)
    description = models.TextField('描述', blank=True)
    created_time = models.DateTimeField('创建时间', default=timezone.now)
    updated_time = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        abstract = True
        default_permissions = ('view', 'add', 'change', 'delete')
        permissions = [
            ('export_device', '导出设备信息'),
            ('import_device', '导入设备信息'),
        ]

    def can_edit(self, user):
        """检查用户是否可以编辑该设备"""
        if user.is_admin:
            return True
        model_name = self._meta.model_name
        return user.has_perm(f'assets.change_{model_name}', self)

    def can_edit_by(self, user):
        """模板友好的编辑权限检查方法"""
        if user.is_admin:
            return True
        model_name = self._meta.model_name
        return user.has_perm(f'assets.change_{model_name}', self)

class Server(Device):
    """服务器模型"""
    hostname = models.CharField('主机名', max_length=50)
    os_type = models.CharField('操作系统类型', max_length=50)
    os_version = models.CharField('操作系统版本', max_length=50)
    cpu_model = models.CharField('CPU型号', max_length=100)
    cpu_count = models.IntegerField('CPU数量')
    cpu_cores = models.IntegerField('CPU核心数')
    memory_size = models.IntegerField('内存大小(GB)')
    disk_info = models.TextField('硬盘信息')
    business_system = models.CharField('业务系统', max_length=50)

    class Meta:
        verbose_name = '服务器'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.hostname

class NetworkDevice(Device):
    """网络设备模型"""
    device_type = models.CharField('设备类型', max_length=50)  # 如交换机、路由器等
    port_count = models.IntegerField('端口数量')
    port_info = models.TextField('端口信息')
    management_ip = models.GenericIPAddressField('管理IP', unique=True)
    vlan_info = models.TextField('VLAN配置')
    routing_info = models.TextField('路由信息', blank=True)
    
    history = HistoricalRecords()

    class Meta:
        verbose_name = '网络设备'
        verbose_name_plural = verbose_name
        default_permissions = ('view', 'add', 'change', 'delete')
        permissions = [
            ('export_networkdevice', '导出网络设备信息'),
            ('import_networkdevice', '导入网络设备信息'),
        ]

    def __str__(self):
        return self.name

class StorageDevice(Device):
    """存储设备模型"""
    storage_type = models.CharField('存储类型', max_length=50)  # 如SAN、NAS等
    total_capacity = models.DecimalField('总容量(TB)', max_digits=10, decimal_places=2)
    used_capacity = models.DecimalField('已用容量(TB)', max_digits=10, decimal_places=2)
    raid_type = models.CharField('RAID类型', max_length=50)
    raid_config = models.TextField('RAID配置')
    controller_info = models.TextField('控制器信息')
    
    history = HistoricalRecords()

    class Meta:
        verbose_name = '存储设备'
        verbose_name_plural = verbose_name
        default_permissions = ('view', 'add', 'change', 'delete')
        permissions = [
            ('export_storagedevice', '导出存储设备信息'),
            ('import_storagedevice', '导入存储设备信息'),
        ]

    def __str__(self):
        return self.name

class SecurityDevice(Device):
    """安全设备模型"""
    device_type = models.CharField('设备类型', max_length=50)  # 如防火墙、IDS等
    software_version = models.CharField('软件版本', max_length=50)
    rule_version = models.CharField('规则库版本', max_length=50)
    policy_info = models.TextField('策略配置')
    log_info = models.TextField('日志配置')
    monitor_info = models.TextField('监控配置')
    
    history = HistoricalRecords()

    class Meta:
        verbose_name = '安全设备'
        verbose_name_plural = verbose_name
        default_permissions = ('view', 'add', 'change', 'delete')
        permissions = [
            ('export_securitydevice', '导出安全设备信息'),
            ('import_securitydevice', '导入安全设备信息'),
        ]

    def __str__(self):
        return self.name 