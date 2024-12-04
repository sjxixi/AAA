from django.contrib import admin
from .models import DataCenter
from simple_history.admin import SimpleHistoryAdmin

@admin.register(DataCenter)
class DataCenterAdmin(SimpleHistoryAdmin):
    list_display = ('name', 'location', 'contact_name', 'contact_phone', 
                   'area', 'power_capacity', 'cooling_capacity')
    search_fields = ('name', 'location', 'contact_name')
    history_list_display = ['status'] 