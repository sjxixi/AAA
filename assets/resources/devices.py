from import_export import resources, fields
from assets.models import (
    Server, NetworkDevice, StorageDevice, SecurityDevice
)
from .base import BaseDeviceResource

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
        fields = BaseDeviceResource.Meta.fields + (
            'hostname', 'cpu_model', 'cpu_count', 'cpu_cores', 'memory_size',
            'disk_info', 'os_type', 'os_version', 'business_system'
        )

class NetworkDeviceResource(BaseDeviceResource):
    """网络设备资源类"""
    device_type = fields.Field(column_name='设备类型', attribute='device_type')
    port_count = fields.Field(column_name='端口数量', attribute='port_count')
    port_info = fields.Field(column_name='端口信息', attribute='port_info')
    management_ip = fields.Field(column_name='管理IP', attribute='management_ip')
    vlan_info = fields.Field(column_name='VLAN信息', attribute='vlan_info')
    routing_info = fields.Field(column_name='路由信息', attribute='routing_info')

    class Meta:
        model = NetworkDevice
        skip_unchanged = True
        report_skipped = False
        import_id_fields = ('sn',)
        fields = BaseDeviceResource.Meta.fields + (
            'device_type', 'port_count', 'port_info', 'management_ip',
            'vlan_info', 'routing_info'
        )

class StorageDeviceResource(BaseDeviceResource):
    """存储设备资源类"""
    storage_type = fields.Field(column_name='存储类型', attribute='storage_type')
    capacity = fields.Field(column_name='容量(TB)', attribute='capacity')
    raid_type = fields.Field(column_name='RAID类型', attribute='raid_type')
    disk_count = fields.Field(column_name='硬盘数量', attribute='disk_count')
    disk_info = fields.Field(column_name='硬盘信息', attribute='disk_info')

    class Meta:
        model = StorageDevice
        skip_unchanged = True
        report_skipped = False
        import_id_fields = ('sn',)
        fields = BaseDeviceResource.Meta.fields + (
            'storage_type', 'capacity', 'raid_type', 'disk_count', 'disk_info'
        )

class SecurityDeviceResource(BaseDeviceResource):
    """安全设备资源类"""
    security_type = fields.Field(column_name='安全类型', attribute='security_type')
    throughput = fields.Field(column_name='吞吐量', attribute='throughput')
    policy_count = fields.Field(column_name='策略数量', attribute='policy_count')
    firmware_version = fields.Field(column_name='固件版本', attribute='firmware_version')

    class Meta:
        model = SecurityDevice
        skip_unchanged = True
        report_skipped = False
        import_id_fields = ('sn',)
        fields = BaseDeviceResource.Meta.fields + (
            'security_type', 'throughput', 'policy_count', 'firmware_version'
        ) 