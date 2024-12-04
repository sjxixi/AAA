from django import forms
from .models import DataCenter

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