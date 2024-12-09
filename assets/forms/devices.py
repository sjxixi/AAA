from django import forms
from assets.models import Server, NetworkDevice, StorageDevice, SecurityDevice

class BaseDeviceForm(forms.ModelForm):
    """设备基础表单"""
    class Meta:
        abstract = True
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'model': forms.TextInput(attrs={'class': 'form-control'}),
            'sn': forms.TextInput(attrs={'class': 'form-control'}),
            'manufacturer': forms.TextInput(attrs={'class': 'form-control'}),
            'purchase_date': forms.DateInput(
                attrs={
                    'class': 'form-control',
                    'type': 'date',
                }
            ),
            'warranty_date': forms.DateInput(
                attrs={
                    'class': 'form-control',
                    'type': 'date',
                }
            ),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'data_center': forms.Select(attrs={'class': 'form-control'}),
            'rack_position': forms.TextInput(attrs={'class': 'form-control'}),
            'ip_address': forms.TextInput(attrs={'class': 'form-control'}),
            'mac_address': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # 移除状态字段的默认值
        self.fields['status'].empty_label = None  # 不显示空选项
        self.fields['status'].initial = None  # 清除初始值

class ServerForm(BaseDeviceForm):
    """服务器表单"""
    class Meta(BaseDeviceForm.Meta):
        model = Server
        fields = [
            'name', 'hostname', 'ip_address', 'mac_address',
            'os_type', 'os_version', 'cpu_model', 'cpu_count',
            'cpu_cores', 'memory_size', 'disk_info', 'business_system',
            'status', 'data_center', 'rack_position', 'manufacturer',
            'model', 'sn', 'purchase_date', 'warranty_date', 'description'
        ]
        widgets = {
            **BaseDeviceForm.Meta.widgets,  # 继承基类的 widgets
            'hostname': forms.TextInput(attrs={'class': 'form-control'}),
            'os_type': forms.TextInput(attrs={'class': 'form-control'}),
            'os_version': forms.TextInput(attrs={'class': 'form-control'}),
            'cpu_model': forms.TextInput(attrs={'class': 'form-control'}),
            'cpu_count': forms.NumberInput(attrs={'class': 'form-control'}),
            'cpu_cores': forms.NumberInput(attrs={'class': 'form-control'}),
            'memory_size': forms.NumberInput(attrs={'class': 'form-control'}),
            'disk_info': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'business_system': forms.TextInput(attrs={'class': 'form-control'}),
        }

class NetworkDeviceForm(BaseDeviceForm):
    """网络设备表单"""
    class Meta(BaseDeviceForm.Meta):
        model = NetworkDevice
        fields = '__all__'
        widgets = {
            **BaseDeviceForm.Meta.widgets,
            'device_type': forms.TextInput(attrs={'class': 'form-control'}),
            'port_count': forms.NumberInput(attrs={'class': 'form-control'}),
            'port_info': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'management_ip': forms.TextInput(attrs={'class': 'form-control'}),
            'vlan_info': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'routing_info': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

class StorageDeviceForm(BaseDeviceForm):
    """存储设备表单"""
    class Meta(BaseDeviceForm.Meta):
        model = StorageDevice
        fields = '__all__'
        widgets = {
            **BaseDeviceForm.Meta.widgets,
            'storage_type': forms.TextInput(attrs={'class': 'form-control'}),
            'total_capacity': forms.NumberInput(attrs={'class': 'form-control'}),
            'used_capacity': forms.NumberInput(attrs={'class': 'form-control'}),
            'raid_type': forms.TextInput(attrs={'class': 'form-control'}),
            'raid_config': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'controller_info': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

class SecurityDeviceForm(BaseDeviceForm):
    """安全设备表单"""
    class Meta(BaseDeviceForm.Meta):
        model = SecurityDevice
        fields = '__all__'
        widgets = {
            **BaseDeviceForm.Meta.widgets,
            'device_type': forms.TextInput(attrs={'class': 'form-control'}),
            'software_version': forms.TextInput(attrs={'class': 'form-control'}),
            'rule_version': forms.TextInput(attrs={'class': 'form-control'}),
            'policy_info': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'log_info': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'monitor_info': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        } 