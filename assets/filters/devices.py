import django_filters
from django.conf import settings
from assets.models import Server, NetworkDevice, StorageDevice, SecurityDevice, DataCenter

class BaseDeviceFilter(django_filters.FilterSet):
    """设备基础过滤器"""
    name = django_filters.CharFilter(lookup_expr='icontains', label='名称')
    ip_address = django_filters.CharFilter(lookup_expr='icontains', label='IP地址')
    status = django_filters.ChoiceFilter(
        choices=[(k, v) for k, v in settings.DEVICE_STATUS.items()], 
        label='状态'
    )
    data_center = django_filters.ModelChoiceFilter(
        queryset=DataCenter.objects.all(),
        label='数据中心'
    )

class ServerFilter(django_filters.FilterSet):
    """服务器过滤器"""
    name = django_filters.CharFilter(lookup_expr='icontains', label='名称')
    hostname = django_filters.CharFilter(lookup_expr='icontains', label='主机名')
    ip_address = django_filters.CharFilter(lookup_expr='icontains', label='IP地址')
    os_type = django_filters.CharFilter(lookup_expr='icontains', label='操作系统')
    business_system = django_filters.CharFilter(lookup_expr='icontains', label='业务系统')
    status = django_filters.ChoiceFilter(
        choices=[(k, v) for k, v in settings.DEVICE_STATUS.items()], 
        label='状态'
    )
    data_center = django_filters.ModelChoiceFilter(
        queryset=DataCenter.objects.all(),
        label='数据中心'
    )

    class Meta:
        model = Server
        fields = ['name', 'hostname', 'ip_address', 'os_type', 'business_system', 
                 'status', 'data_center']

class NetworkDeviceFilter(BaseDeviceFilter):
    """网络设备过滤器"""
    device_type = django_filters.CharFilter(lookup_expr='icontains', label='设备类型')
    manufacturer = django_filters.CharFilter(lookup_expr='icontains', label='制造商')

    class Meta:
        model = NetworkDevice
        fields = ['name', 'sn', 'ip_address', 'status', 'data_center', 
                 'device_type', 'manufacturer']

class StorageDeviceFilter(BaseDeviceFilter):
    """存储设备过滤器"""
    storage_type = django_filters.CharFilter(lookup_expr='icontains', label='存储类型')
    raid_type = django_filters.CharFilter(lookup_expr='icontains', label='RAID类型')

    class Meta:
        model = StorageDevice
        fields = ['name', 'sn', 'ip_address', 'status', 'data_center', 
                 'storage_type', 'raid_type']

class SecurityDeviceFilter(BaseDeviceFilter):
    """安全设备过滤器"""
    device_type = django_filters.CharFilter(lookup_expr='icontains', label='设备类型')
    software_version = django_filters.CharFilter(lookup_expr='icontains', label='软件版本')

    class Meta:
        model = SecurityDevice
        fields = ['name', 'sn', 'ip_address', 'status', 'data_center', 
                 'device_type', 'software_version'] 