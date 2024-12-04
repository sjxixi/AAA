import django_filters
from .models import DataCenter

class DataCenterFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(lookup_expr='icontains', label='名称')
    location = django_filters.CharFilter(lookup_expr='icontains', label='位置')
    contact_name = django_filters.CharFilter(lookup_expr='icontains', label='联系人')
    area_min = django_filters.NumberFilter(field_name='area', lookup_expr='gte', label='最小面积')
    area_max = django_filters.NumberFilter(field_name='area', lookup_expr='lte', label='最大面积')

    class Meta:
        model = DataCenter
        fields = ['name', 'location', 'contact_name'] 