from import_export import resources, fields
from assets.models import (
    DataCenter, Server, NetworkDevice, StorageDevice, SecurityDevice
)

class BaseDeviceResource(resources.ModelResource):
    """设备基础资源类"""
    data_center = fields.Field(
        column_name='数据中心',
        attribute='data_center',
        widget=resources.widgets.ForeignKeyWidget(DataCenter, 'name')
    )
    status = fields.Field(
        column_name='状态',
        attribute='status',
        widget=resources.widgets.CharWidget()
    )

    def get_export_headers(self, *args, **kwargs):
        """获取导出表头"""
        headers = []
        for field in self.get_fields():
            if hasattr(field, 'column_name'):
                headers.append(field.column_name)
            else:
                headers.append(field.attribute)
        return headers

    def get_fields(self):
        """获取所有字段"""
        fields = super().get_fields()
        # 添加中文表头
        for field in fields:
            if not hasattr(field, 'column_name'):
                try:
                    field.column_name = self._meta.model._meta.get_field(field.attribute).verbose_name
                except:
                    field.column_name = field.attribute
        return fields

    def export_field(self, field, obj):
        """导出字段值"""
        value = super().export_field(field, obj)
        if field.attribute == 'status':
            # 获取状态的显示值
            choices = dict(self._meta.model._meta.get_field('status').choices)
            return choices.get(value, value)
        return value

class ServerResource(BaseDeviceResource):
    """服务器资源类"""
    name = fields.Field(column_name='名称', attribute='name')
    hostname = fields.Field(column_name='主机名', attribute='hostname')
    model = fields.Field(column_name='型号', attribute='model')
    sn = fields.Field(column_name='序列号', attribute='sn')
    manufacturer = fields.Field(column_name='制造商', attribute='manufacturer')
    ip_address = fields.Field(column_name='IP地址', attribute='ip_address')
    mac_address = fields.Field(column_name='MAC地址', attribute='mac_address')
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
        fields = ('name', 'hostname', 'model', 'sn', 'manufacturer', 'status', 
                 'data_center', 'ip_address', 'mac_address', 'cpu_model', 
                 'cpu_count', 'cpu_cores', 'memory_size', 'disk_info', 
                 'os_type', 'os_version', 'business_system')
        export_order = fields

class NetworkDeviceResource(BaseDeviceResource):
    """网络设备资源类"""
    name = fields.Field(column_name='名称', attribute='name')
    model = fields.Field(column_name='型号', attribute='model')
    sn = fields.Field(column_name='序列号', attribute='sn')
    manufacturer = fields.Field(column_name='制造商', attribute='manufacturer')
    ip_address = fields.Field(column_name='IP地址', attribute='ip_address')
    mac_address = fields.Field(column_name='MAC地址', attribute='mac_address')
    device_type = fields.Field(column_name='设备类型', attribute='device_type')
    port_count = fields.Field(column_name='端口数量', attribute='port_count')
    management_ip = fields.Field(column_name='管理IP', attribute='management_ip')
    vlan_info = fields.Field(column_name='VLAN配置', attribute='vlan_info')

    class Meta:
        model = NetworkDevice
        fields = ('name', 'model', 'sn', 'manufacturer', 'status', 'data_center',
                 'ip_address', 'mac_address', 'device_type', 'port_count',
                 'management_ip', 'vlan_info')
        export_order = fields

class StorageDeviceResource(BaseDeviceResource):
    """存储设备资源类"""
    name = fields.Field(column_name='名称', attribute='name')
    model = fields.Field(column_name='型号', attribute='model')
    sn = fields.Field(column_name='序列号', attribute='sn')
    manufacturer = fields.Field(column_name='制造商', attribute='manufacturer')
    ip_address = fields.Field(column_name='IP地址', attribute='ip_address')
    mac_address = fields.Field(column_name='MAC地址', attribute='mac_address')
    storage_type = fields.Field(column_name='存储类型', attribute='storage_type')
    total_capacity = fields.Field(column_name='总容量(TB)', attribute='total_capacity')
    used_capacity = fields.Field(column_name='已用容量(TB)', attribute='used_capacity')
    raid_type = fields.Field(column_name='RAID类型', attribute='raid_type')

    class Meta:
        model = StorageDevice
        fields = ('name', 'model', 'sn', 'manufacturer', 'status', 'data_center',
                 'ip_address', 'mac_address', 'storage_type', 'total_capacity',
                 'used_capacity', 'raid_type')
        export_order = fields

class SecurityDeviceResource(BaseDeviceResource):
    """安全设备资源类"""
    name = fields.Field(column_name='名称', attribute='name')
    model = fields.Field(column_name='型号', attribute='model')
    sn = fields.Field(column_name='序列号', attribute='sn')
    manufacturer = fields.Field(column_name='制造商', attribute='manufacturer')
    ip_address = fields.Field(column_name='IP地址', attribute='ip_address')
    mac_address = fields.Field(column_name='MAC地址', attribute='mac_address')
    device_type = fields.Field(column_name='设备类型', attribute='device_type')
    software_version = fields.Field(column_name='软件版本', attribute='software_version')
    rule_version = fields.Field(column_name='规则库版本', attribute='rule_version')

    class Meta:
        model = SecurityDevice
        fields = ('name', 'model', 'sn', 'manufacturer', 'status', 'data_center',
                 'ip_address', 'mac_address', 'device_type', 'software_version',
                 'rule_version')
        export_order = fields 