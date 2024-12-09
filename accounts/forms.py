from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import User
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.db.models import Q
from assets.models import DataCenter

class UserCreateForm(forms.ModelForm):
    """用户创建表单"""
    password1 = forms.CharField(
        label='密码',
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        help_text='密码长度至少8位，且不能太简单'
    )
    password2 = forms.CharField(
        label='确认密码',
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        help_text='请再次输入密码进行确认'
    )

    class Meta:
        model = User
        fields = ('username', 'email', 'phone', 'department', 'position', 
                 'user_type', 'data_centers', 'is_active')
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'department': forms.TextInput(attrs={'class': 'form-control'}),
            'position': forms.TextInput(attrs={'class': 'form-control'}),
            'user_type': forms.Select(attrs={'class': 'form-control'}),
            'data_centers': forms.SelectMultiple(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user and not user.is_admin:
            # 非管理员用户不能创建管理员账号
            self.fields['user_type'].choices = [('user', '普通用户')]
            # 非管理员只能分配自己有权限的数据中心
            self.fields['data_centers'].queryset = user.data_centers.all()
            # 隐藏一些字段
            self.fields['user_type'].widget = forms.HiddenInput()
            self.fields['is_active'].widget = forms.HiddenInput()

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("两次输入的密码不匹配")
        return password2

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        
        # 设置用户权限
        if user.user_type == 'admin':
            user.is_staff = True
            user.is_superuser = True
        else:
            user.is_staff = False
            user.is_superuser = False
        
        if commit:
            user.save()
            self.save_m2m()  # 保存多对多关系
        return user

class UserUpdateForm(UserChangeForm):
    password = None  # 移除密码字段
    
    class Meta:
        model = User
        fields = ('username', 'email', 'phone', 'department', 'position', 'user_type', 'is_active')
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'department': forms.TextInput(attrs={'class': 'form-control'}),
            'position': forms.TextInput(attrs={'class': 'form-control'}),
            'user_type': forms.Select(attrs={'class': 'form-control'}),
        }

class PasswordChangeForm(forms.Form):
    old_password = forms.CharField(widget=forms.PasswordInput, label='原密码')
    new_password1 = forms.CharField(widget=forms.PasswordInput, label='新密码')
    new_password2 = forms.CharField(widget=forms.PasswordInput, label='确认新密码')

    def clean(self):
        cleaned_data = super().clean()
        new_password1 = cleaned_data.get('new_password1')
        new_password2 = cleaned_data.get('new_password2')
        
        if new_password1 and new_password2 and new_password1 != new_password2:
            raise forms.ValidationError('两次输入的密码不一致') 

class UserPermissionForm(forms.Form):
    """用户权限表单"""
    data_centers = forms.ModelMultipleChoiceField(
        queryset=DataCenter.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label='可访问的数据中心'
    )

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        if user:
            self.fields['data_centers'].initial = user.data_centers.all()

        # 动态创建权限字段
        self.permission_fields = {}
        
        # 按模块分组的权限
        permission_groups = {
            'server': {
                'name': '服务器',
                'permissions': ['view', 'add', 'change', 'delete', 'export', 'import']
            },
            'networkdevice': {
                'name': '网络设备',
                'permissions': ['view', 'add', 'change', 'delete', 'export', 'import']
            },
            'storagedevice': {
                'name': '存储设备',
                'permissions': ['view', 'add', 'change', 'delete', 'export', 'import']
            },
            'securitydevice': {
                'name': '安全设备',
                'permissions': ['view', 'add', 'change', 'delete', 'export', 'import']
            }
        }

        # 权限操作的显示名称
        action_names = {
            'view': '查看',
            'add': '添加',
            'change': '修改',
            'delete': '删除',
            'export': '导出',
            'import': '导入'
        }

        # 为每个模块创建权限字段
        for model_name, group_info in permission_groups.items():
            for action in group_info['permissions']:
                field_name = f'{model_name}_{action}'
                label = f"{action_names[action]}{group_info['name']}"
                
                # 创建权限字段
                self.fields[field_name] = forms.BooleanField(
                    label=label,
                    required=False,
                    # 检查用户是否有该权限
                    initial=user.has_perm(f'assets.{action}_{model_name}') if user else False
                )
                
                # 记录字段信息用于模板渲染
                if model_name not in self.permission_fields:
                    self.permission_fields[model_name] = {
                        'name': group_info['name'],
                        'permissions': []
                    }
                self.permission_fields[model_name]['permissions'].append({
                    'field_name': field_name,
                    'label': label
                })

    def save(self, user):
        """保存用户权限"""
        # 更新数据中心权限
        user.data_centers.set(self.cleaned_data['data_centers'])
        
        # 更新操作权限
        new_permissions = []
        content_types = ContentType.objects.filter(app_label='assets')
        
        # 权限映射关系
        permission_mapping = {
            'server': 'server',
            'networkdevice': 'networkdevice',
            'storagedevice': 'storagedevice',
            'securitydevice': 'securitydevice',
        }
        
        # 导入导出权限特殊处理
        special_permissions = {
            'export': 'export_{}',
            'import': 'import_{}'
        }
        
        for field_name, value in self.cleaned_data.items():
            if field_name != 'data_centers' and value:
                try:
                    model_name, action = field_name.split('_')
                    if model_name in permission_mapping:
                        content_type = content_types.get(model=permission_mapping[model_name])
                        
                        # 处理特殊权限（导入导出）
                        if action in special_permissions:
                            codename = special_permissions[action].format(model_name)
                        else:
                            codename = f'{action}_{model_name}'
                        
                        perm = Permission.objects.get(
                            codename=codename,
                            content_type=content_type
                        )
                        new_permissions.append(perm)
                except (ContentType.DoesNotExist, Permission.DoesNotExist, ValueError):
                    print(f"Permission not found: {field_name}")  # 添加调试信息
                    continue
        
        # 设置新的权限
        user.user_permissions.set(new_permissions)

class UserEditForm(forms.ModelForm):
    """用户编辑表单"""
    class Meta:
        model = User
        fields = ('username', 'email', 'phone', 'department', 'position', 
                 'user_type', 'data_centers', 'is_active')
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'department': forms.TextInput(attrs={'class': 'form-control'}),
            'position': forms.TextInput(attrs={'class': 'form-control'}),
            'user_type': forms.Select(attrs={'class': 'form-control'}),
            'data_centers': forms.SelectMultiple(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)  # 当前登录的用户
        super().__init__(*args, **kwargs)
        
        if user and not user.is_admin:
            # 非管理员用户不能修改用户类型
            self.fields['user_type'].widget = forms.HiddenInput()
            self.fields['is_active'].widget = forms.HiddenInput()
            # 非管理员只能分配自己有���限的数据中心
            self.fields['data_centers'].queryset = user.data_centers.all()

    def save(self, commit=True):
        user = super().save(commit=False)
        
        # 根据用户类型设置权限
        if user.user_type == 'admin':
            user.is_staff = True
            user.is_superuser = True
        else:
            user.is_staff = False
            user.is_superuser = False
            
        if commit:
            user.save()
            self.save_m2m()  # 保存多对多关系（数据中心）
        return user