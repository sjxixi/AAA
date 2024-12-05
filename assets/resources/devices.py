from import_export import resources, fields
from assets.models import Server, NetworkDevice, StorageDevice, SecurityDevice, DataCenter
from .base import BaseDeviceResource
from django.db import transaction
from import_export.widgets import ForeignKeyWidget

class ServerResource(BaseDeviceResource):
    """服务器资源类"""
    hostname = fields.Field(column_name='主机名', attribute='hostname')
    cpu_model = fields.Field(column_name='CPU型号', attribute='cpu_model')
    cpu_count = fields.Field(column_name='CPU数量', attribute='cpu_count')
    cpu_cores = fields.Field(column_name='CPU核心数', attribute='cpu_cores')
    memory_size = fields.Field(column_name='内存大小(GB)', attribute='memory_size')
    disk_info = fields.Field(column_name='硬盘信息', attribute='disk_info')
    os_type = fields.Field(column_name='操作系统类型', attribute='os_type')
    os_version = fields.Field(column_name='操作系统版本', attribute='os_version')
    business_system = fields.Field(column_name='业务系统', attribute='business_system')

    class Meta:
        model = Server
        skip_unchanged = True
        report_skipped = False
        import_id_fields = ('sn',)
        fields = BaseDeviceResource.Meta.fields + [
            'hostname', 
            'cpu_model', 
            'cpu_count', 
            'cpu_cores', 
            'memory_size',
            'disk_info', 
            'os_type', 
            'os_version', 
            'business_system'
        ]
        use_transactions = False  # 禁用事务

    def before_import_row(self, row, **kwargs):
        try:
            with transaction.atomic():
                # 确保主机名是唯一的
                if '主机名' in row and not row.get('主机名'):
                    row['主机名'] = f"host-{row.get('序列号', 'unknown')}"
                return super().before_import_row(row, **kwargs)
        except Exception as e:
            return False

class NetworkDeviceResource(BaseDeviceResource):
    """网络设备资源类"""
    device_type = fields.Field(column_name='设备类型', attribute='device_type')
    port_count = fields.Field(column_name='端口数量', attribute='port_count')
    port_info = fields.Field(column_name='端口信息', attribute='port_info')
    management_ip = fields.Field(column_name='管理IP', attribute='management_ip')
    vlan_info = fields.Field(column_name='VLAN配置', attribute='vlan_info')
    routing_info = fields.Field(column_name='路由信息', attribute='routing_info')

    def before_import_row(self, row, **kwargs):
        """在导入每行之前进行数据处理"""
        # 先调用父类的处理
        row = super().before_import_row(row, **kwargs)

        # 网络设备特有的必填字段验证
        if not row.get('设备类型'):
            raise Exception('设备类型不能为空')
        if not row.get('端口数量'):
            raise Exception('端口数量不能为空')
        if not row.get('管理IP'):
            raise Exception('管理IP不能为空')

        # 处理默认值
        if not row.get('端口信息'):
            row['端口信息'] = ''
        if not row.get('VLAN配置'):
            row['VLAN配置'] = ''
        if not row.get('路由信息'):
            row['路由信息'] = ''

        return row

    class Meta:
        model = NetworkDevice
        skip_unchanged = True
        report_skipped = False
        import_id_fields = ('sn',)
        fields = BaseDeviceResource.Meta.fields + [
            'device_type',
            'port_count',
            'port_info',
            'management_ip',
            'vlan_info',
            'routing_info'
        ]
        export_order = fields

class StorageDeviceResource(BaseDeviceResource):
    """存储设备资源类"""
    storage_type = fields.Field(column_name='存储类型', attribute='storage_type')
    total_capacity = fields.Field(column_name='总容量(TB)', attribute='total_capacity')
    used_capacity = fields.Field(column_name='已用容量(TB)', attribute='used_capacity')
    raid_type = fields.Field(column_name='RAID类型', attribute='raid_type')
    raid_config = fields.Field(column_name='RAID配置', attribute='raid_config')
    controller_info = fields.Field(column_name='控制器信息', attribute='controller_info')
    data_center = fields.Field(
        column_name='所属数据中心',
        attribute='data_center',
        widget=ForeignKeyWidget(DataCenter, 'name')
    )

    def before_import_row(self, row, **kwargs):
        """在导入每行之前进行数据处理"""
        # 先调用父类的处理
        row = super().before_import_row(row, **kwargs)

        # 处理存储类型
        if '所属数据中心' in row and row['所属数据中心']:
            if not row['所属数据中心'].endswith('-01'):
                row['所属数据中心'] = f"{row['所属数据中心']}-01"

        # 处理存储类型
        if 'Flash' in str(row.get('存储类型', '')):
            row['存储类型'] = 'All Flash'
        
        # 处理容量
        capacity_str = str(row.get('总容量(TB)', '0')).lower()
        if 't' in capacity_str:
            capacity = float(capacity_str.replace('t', ''))
        else:
            capacity = float(capacity_str)
        row['总容量(TB)'] = capacity
        
        # 默认已用容量为总容量的10%
        row['已用容量(TB)'] = capacity * 0.1

        # 处理RAID信息
        raid_type = str(row.get('RAID类型', 'RAID 10'))
        if not raid_type.startswith('RAID'):
            raid_type = f"RAID {raid_type}"
        row['RAID类型'] = raid_type
        
        # 设置RAID配置
        row['RAID配置'] = f"主配置: {raid_type}, 备配置: {row.get('RAID配置', raid_type)}"
        
        # 设置控制器信息
        row['控制器信息'] = f"存储控制器: {row.get('控制器信息', 'EMC Unity')}"

        return row

    def import_row(self, row, instance_loader, **kwargs):
        """处理每行数据的导入"""
        try:
            # 获取或创建数据中心
            data_center_name = row.get('所属数据中心')
            if data_center_name:
                data_center, created = DataCenter.objects.get_or_create(
                    name=data_center_name,
                    defaults={
                        'location': '默认位置',
                        'contact_name': '默认联系人',
                        'contact_phone': '默认电话',
                        'area': 100,
                        'power_capacity': 10,
                        'cooling_capacity': 10
                    }
                )
            
            return super().import_row(row, instance_loader, **kwargs)
        except Exception as e:
            raise Exception(f'导入行时出错: {str(e)}')

    class Meta:
        model = StorageDevice
        skip_unchanged = True
        report_skipped = False
        import_id_fields = ('sn',)
        fields = BaseDeviceResource.Meta.fields + [
            'storage_type',
            'total_capacity',
            'used_capacity',
            'raid_type',
            'raid_config',
            'controller_info'
        ]
        export_order = fields

class SecurityDeviceResource(BaseDeviceResource):
    """安全设备资源类"""
    security_type = fields.Field(column_name='设备类型', attribute='device_type')
    software_version = fields.Field(column_name='软件版本', attribute='software_version')
    rule_version = fields.Field(column_name='规则版本', attribute='rule_version')
    policy_info = fields.Field(column_name='策略配置', attribute='policy_info')
    log_info = fields.Field(column_name='日志配置', attribute='log_info')
    monitor_info = fields.Field(column_name='监控配置', attribute='monitor_info')

    def before_import_row(self, row, **kwargs):
        """在导入每行之前进行数据处理"""
        # 先调用父类的处理
        row = super().before_import_row(row, **kwargs)

        # 安全设备特有的必填字段验证
        if not row.get('设备类型'):
            raise Exception('设备类型不能为空')
        if not row.get('软件版本'):
            raise Exception('软件版本不能为空')
        if not row.get('规则版本'):
            raise Exception('规则版本不能为空')

        # 处理默认值
        if not row.get('策略配置'):
            row['策略配置'] = ''
        if not row.get('日志配置'):
            row['日志配置'] = ''
        if not row.get('监控配置'):
            row['监控配置'] = ''

        return row

    class Meta:
        model = SecurityDevice
        skip_unchanged = True
        report_skipped = False
        import_id_fields = ('sn',)
        fields = BaseDeviceResource.Meta.fields + [
            'security_type',
            'software_version',
            'rule_version',
            'policy_info',
            'log_info',
            'monitor_info'
        ]
        export_order = fields 