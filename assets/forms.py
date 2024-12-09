from django import forms
from .models import DataCenter, Server
from django.forms import DateInput

class DataCenterForm(forms.ModelForm):
    class Meta:
        model = DataCenter
        fields = ['name', 'location', 'contact_name', 'contact_phone', 
                 'area', 'power_capacity', 'cooling_capacity']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'location': forms.TextInput(attrs={'class': 'form-control'}),
            'contact_name': forms.TextInput(attrs={'class': 'form-control'}),
            'contact_phone': forms.TextInput(attrs={'class': 'form-control'}),
            'area': forms.NumberInput(attrs={'class': 'form-control'}),
            'power_capacity': forms.NumberInput(attrs={'class': 'form-control'}),
            'cooling_capacity': forms.NumberInput(attrs={'class': 'form-control'}),
        }

class ServerForm(forms.ModelForm):
    class Meta:
        model = Server
        fields = '__all__'
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'hostname': forms.TextInput(attrs={'class': 'form-control'}),
            'ip_address': forms.TextInput(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={
                'class': 'form-control'
            }),
            'data_center': forms.Select(attrs={'class': 'form-control'}),
            'manufacturer': forms.TextInput(attrs={'class': 'form-control'}),
            'model': forms.TextInput(attrs={'class': 'form-control'}),
            'sn': forms.TextInput(attrs={'class': 'form-control'}),
            'purchase_date': DateInput(attrs={
                'class': 'form-control',
                'type': 'text',  # 使用text类型让flatpickr接管
                'placeholder': '选择采购日期'
            }),
            'warranty_expire': DateInput(attrs={
                'class': 'form-control', 
                'type': 'text',  # 使用text类型让flatpickr接管
                'placeholder': '选择保修到期日期'
            }),
            'rack_position': forms.TextInput(attrs={'class': 'form-control'}),
            'os_type': forms.TextInput(attrs={'class': 'form-control'}),
            'os_version': forms.TextInput(attrs={'class': 'form-control'}),
            'cpu_model': forms.TextInput(attrs={'class': 'form-control'}),
            'cpu_count': forms.NumberInput(attrs={'class': 'form-control'}),
            'memory_size': forms.NumberInput(attrs={'class': 'form-control'}),
            'disk_size': forms.NumberInput(attrs={'class': 'form-control'}),
            'business_system': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3
            }),
        } 