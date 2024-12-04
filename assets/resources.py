from import_export import resources, fields
from .models import DataCenter

class DataCenterResource(resources.ModelResource):
    name = fields.Field(column_name='名称', attribute='name')
    location = fields.Field(column_name='位置', attribute='location')
    contact_name = fields.Field(column_name='联系人', attribute='contact_name')
    contact_phone = fields.Field(column_name='联系电话', attribute='contact_phone')
    area = fields.Field(column_name='面积(平方米)', attribute='area')
    power_capacity = fields.Field(column_name='电力容量(KW)', attribute='power_capacity')
    cooling_capacity = fields.Field(column_name='制冷能力(KW)', attribute='cooling_capacity')

    class Meta:
        model = DataCenter
        fields = ('name', 'location', 'contact_name', 'contact_phone', 
                 'area', 'power_capacity', 'cooling_capacity')
        export_order = fields 