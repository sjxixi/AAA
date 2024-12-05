from import_export import resources, fields
from import_export.widgets import ForeignKeyWidget, DateWidget
from import_export.results import RowResult, Result
from import_export.instance_loaders import ModelInstanceLoader
from assets.models import DataCenter, Server, NetworkDevice
from django.db import IntegrityError, transaction
from django.contrib import messages
import hashlib
import ipaddress

class BaseDeviceResource(resources.ModelResource):
    """基础设备导入导出资源类"""
    
    # 定义字段映射
    name = fields.Field(column_name='名称', attribute='name')
    model = fields.Field(column_name='型号', attribute='model')
    sn = fields.Field(column_name='序列号', attribute='sn')
    manufacturer = fields.Field(column_name='制造商', attribute='manufacturer')
    purchase_date = fields.Field(column_name='采购日期', attribute='purchase_date')
    warranty_date = fields.Field(column_name='保修期限', attribute='warranty_date')
    status = fields.Field(column_name='状态', attribute='status')
    rack_position = fields.Field(column_name='机架位置', attribute='rack_position')
    ip_address = fields.Field(column_name='IP地址', attribute='ip_address')
    mac_address = fields.Field(column_name='MAC地址', attribute='mac_address')
    description = fields.Field(column_name='描述', attribute='description')
    data_center = fields.Field(
        column_name='所属数据中心',
        attribute='data_center',
        widget=ForeignKeyWidget(DataCenter, 'name')
    )

    def skip_row(self, instance, original, row, import_validation_errors=None):
        """决定是否跳过该行"""
        return False

    def before_import_row(self, row, **kwargs):
        """在导入每行之前进行数据处理"""
        # 确保所有必填字段都存在
        if not row.get('名称'):
            raise Exception('名称不能为空')
        if not row.get('序列号'):
            raise Exception('序列号不能为空')
        if not row.get('制造商'):
            raise Exception('制造商不能为空')
        if not row.get('IP地址'):
            raise Exception('IP地址不能为空')
        if not row.get('MAC地址'):
            raise Exception('MAC地址不能为空')
        if not row.get('所属数据中心'):
            raise Exception('数据中心不能为空')

        # 处理状态字段
        if '状态' in row:
            row['状态'] = self._convert_status(row['状态'])
        else:
            row['状态'] = 'running'

        # 处理默认值
        if not row.get('型号'):
            row['型号'] = 'Unknown'
        if not row.get('采购日期'):
            row['采购日期'] = '2024-01-01'
        if not row.get('保修期限'):
            row['保修期限'] = '2027-01-01'
        if not row.get('机架位置'):
            row['机架位置'] = 'A01'

        return row

    def _convert_status(self, status):
        """转换状态值"""
        if not status:
            return 'running'
        
        status = str(status).strip().lower()
        if '运行' in status:
            return 'running'
        elif '停止' in status:
            return 'stopped'
        elif '维护' in status:
            return 'maintenance'
        elif '故障' in status:
            return 'fault'
        return 'running'

    class Meta:
        abstract = True
        skip_unchanged = False
        report_skipped = False
        fields = [
            'name',
            'model',
            'sn',
            'manufacturer',
            'purchase_date',
            'warranty_date',
            'status',
            'rack_position',
            'ip_address',
            'mac_address',
            'data_center',
            'description',
        ]
        use_bulk = False
        use_transactions = True

class NetworkDeviceResource(resources.ModelResource):
    """网络设备导入导出资源类"""
    
    class Meta:
        model = NetworkDevice
        skip_unchanged = False
        report_skipped = False
        import_id_fields = ['ip_address']  # 只使用 IP 地址作为唯一标识
        # 明确指定导入和导出的字段
        export_order = (
            'name',
            'model',
            'sn',
            'manufacturer',
            'purchase_date',
            'warranty_date',
            'status',
            'rack_position',
            'ip_address',
            'mac_address',
            'description',
            'data_center',
            'device_type',
            'port_count',
            'port_info',
            'management_ip',
            'vlan_info',
            'routing_info',
        )
        fields = export_order
        exclude = (
            'id',
            'created_time',
            'updated_time',
            'history',
        )

    # 定义字段映射
    name = fields.Field(column_name='名称', attribute='name')
    model = fields.Field(column_name='型号', attribute='model')
    sn = fields.Field(column_name='序列号', attribute='sn')
    manufacturer = fields.Field(column_name='制造商', attribute='manufacturer')
    purchase_date = fields.Field(column_name='采购日期', attribute='purchase_date')
    warranty_date = fields.Field(column_name='保修期限', attribute='warranty_date')
    status = fields.Field(column_name='状态', attribute='status')
    rack_position = fields.Field(column_name='机架位置', attribute='rack_position')
    ip_address = fields.Field(column_name='IP地址', attribute='ip_address')
    mac_address = fields.Field(column_name='MAC地址', attribute='mac_address')
    description = fields.Field(column_name='描述', attribute='description')
    data_center = fields.Field(
        column_name='所属数据中心',
        attribute='data_center',
        widget=ForeignKeyWidget(DataCenter, 'name')
    )
    device_type = fields.Field(column_name='设备类型', attribute='device_type')
    port_count = fields.Field(column_name='端口数量', attribute='port_count')
    port_info = fields.Field(column_name='端口信息', attribute='port_info')
    management_ip = fields.Field(column_name='管理IP', attribute='management_ip')
    vlan_info = fields.Field(column_name='VLAN配置', attribute='vlan_info')
    routing_info = fields.Field(column_name='路由信息', attribute='routing_info')

    def get_export_headers(self):
        """自定义导出表头"""
        return [
            '名称',
            '型号',
            '序列号',
            '制造商',
            '采购日期',
            '保修期限',
            '状态',
            '机架位置',
            'IP地址',
            'MAC地址',
            '描述',
            '所属数据中心',
            '设备类型',
            '端口数量',
            '端口信息',
            '管理IP',
            'VLAN配置',
            '路由信息'
        ]

    def before_import_row(self, row, **kwargs):
        """在导入每行之前进行数据处理"""
        # 确保所有必填字段都存在
        if not row.get('名称'):
            raise Exception('名称不能为空')
        if not row.get('序列号'):
            raise Exception('序列号不能为空')
        if not row.get('制造商'):
            raise Exception('制造商不能为空')
        if not row.get('IP地址'):
            raise Exception('IP地址不能为空')
        if not row.get('MAC地址'):
            raise Exception('MAC地址不能为空')
        if not row.get('所属数据中心'):
            raise Exception('数据中心不能为空')
        if not row.get('设备类型'):
            raise Exception('设备类型不能为空')
        if not row.get('端口数量'):
            raise Exception('端口数量不能为空')

        # 处理状态字段
        if '状态' in row:
            row['状态'] = self._convert_status(row['状态'])
        else:
            row['状态'] = 'running'

        # 处理默认值
        if not row.get('型号'):
            row['型号'] = 'Cisco'
        if not row.get('采购日期'):
            row['采购日期'] = '2024-01-01'
        if not row.get('保修期限'):
            row['保修期限'] = '2027-01-01'
        if not row.get('机架位置'):
            row['机架位置'] = 'A01'

        return row

    def _convert_status(self, status):
        """转换状态值"""
        if not status:
            return 'running'
        
        status = str(status).strip().lower()
        if '运行' in status:
            return 'running'
        elif '停止' in status:
            return 'stopped'
        elif '维护' in status:
            return 'maintenance'
        elif '故障' in status:
            return 'fault'
        return 'running'