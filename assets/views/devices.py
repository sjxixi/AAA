from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from django.core.paginator import Paginator
from django.conf import settings
from django.utils.decorators import method_decorator
from django.views import View
from assets.models import Server, NetworkDevice, StorageDevice, SecurityDevice
from assets.forms.devices import (
    ServerForm, NetworkDeviceForm, StorageDeviceForm, SecurityDeviceForm
)
from assets.filters.devices import (
    ServerFilter, NetworkDeviceFilter, StorageDeviceFilter, SecurityDeviceFilter
)
from assets.resources.devices import (
    ServerResource, NetworkDeviceResource, StorageDeviceResource, SecurityDeviceResource
)
import datetime
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import permission_required
import json
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.views.generic import DeleteView
from django.urls import reverse_lazy

class BaseDeviceView(LoginRequiredMixin, View):
    """设备视图基类"""
    template_name_list = None
    template_name_detail = None
    template_name_form = None
    model = None
    form_class = None
    filter_class = None
    resource_class = None

    def dispatch(self, request, *args, **kwargs):
        """处理请求分发"""
        print("=== 请求分发调试信息 ===")
        print(f"请求路径: {request.path}")
        print(f"URL名称: {request.resolver_match.url_name}")
        print(f"请求方法: {request.method}")
        print(f"参数: {kwargs}")
        
        if not request.user.is_authenticated:
            return self.handle_no_permission()

        # 检查数据中心权限
        pk = kwargs.get('pk')
        if pk:
            device = get_object_or_404(self.model, pk=pk)
            if not request.user.has_datacenter_perm(device.data_center.id):
                messages.error(request, '您没有该数据中心的操作权限')
                return redirect('assets:dashboard')

        # 根据URL名称决定显示哪个视图
        url_name = request.resolver_match.url_name
        
        # 处理编辑视图
        if url_name and url_name.endswith('_edit'):
            return self.edit_view(request, pk)
        
        # 处理其他视图
        if pk:
            if url_name.endswith('_history'):
                return self.history_view(request, pk)
            elif url_name.endswith('_delete'):
                return self.delete_view(request, pk)
            else:
                return self.detail_view(request, pk)
        else:
            if url_name.endswith('_create'):
                return self.create_view(request)
            return self.list_view(request)

    def get_url_prefix(self):
        """获取URL前缀"""
        url_prefixes = {
            'Server': 'server',
            'NetworkDevice': 'network',
            'StorageDevice': 'storage',
            'SecurityDevice': 'security'
        }
        return url_prefixes.get(self.model.__name__, '')

    def get_queryset(self):
        """获取用户有权限的设备列表"""
        queryset = self.model.objects.all()
        if not self.request.user.is_admin:
            # 非管理员只能看到有权限的数据中的设备
            queryset = queryset.filter(
                data_center__in=self.request.user.data_centers.all()
            )
        return queryset.order_by('id')

    def list_view(self, request):
        """列表视图"""
        queryset = self.get_queryset()
        for device in queryset:
            print(f"Device: {device.name}, Status: {device.status}")  # 调试信息
        filter = self.filter_class(request.GET, queryset=queryset)
        
        # 处理导出请求
        if 'export' in request.GET:
            resource = self.resource_class()
            # 检查是否有选中的ID
            selected_ids = request.GET.get('ids', '')
            if selected_ids:
                # 如果有选中的ID，只导出选中的数据
                ids = [int(id) for id in selected_ids.split(',')]
                queryset = filter.qs.filter(id__in=ids)
            else:
                # 否则导出过滤后的所有数据
                queryset = filter.qs
            
            dataset = resource.export(queryset)
            response = HttpResponse(
                dataset.export('xlsx'),
                content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )
            response['Content-Disposition'] = f'attachment; filename="{self.model._meta.verbose_name}_{datetime.date.today()}.xlsx"'
            return response

        # 分页
        paginator = Paginator(filter.qs, settings.PAGINATION_PAGE_SIZE)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        
        # 获取模型名称
        model_name = self.model._meta.model_name
        
        context = {
            'filter': filter,
            'page_obj': page_obj,
            'verbose_name': self.model._meta.verbose_name,
            'model_type': self.model.__name__,
            'model_name': model_name,
            'view_create': f'assets:{self.get_url_prefix()}_create',
            'view_detail': f'assets:{self.get_url_prefix()}_detail',
            'view_edit': f'assets:{self.get_url_prefix()}_edit',
            'view_delete': f'assets:{self.get_url_prefix()}_delete',
            'view_history': f'assets:{self.get_url_prefix()}_history',
            'view_list': f'assets:{self.get_url_prefix()}_list',
            'view_batch_delete': 'assets:batch_delete',
            'user': request.user,
            'perms': {
                'add': request.user.has_perm(f'assets.add_{model_name}'),
                'change': request.user.has_perm(f'assets.change_{model_name}'),
                'delete': request.user.has_perm(f'assets.delete_{model_name}'),
                'view': request.user.has_perm(f'assets.view_{model_name}'),
                'export': request.user.has_perm(f'assets.export_{model_name}'),
                'import': request.user.has_perm(f'assets.import_{model_name}'),
            }
        }
        return render(request, self.template_name_list, context)

    def detail_view(self, request, pk):
        """详���视图"""
        device = get_object_or_404(self.get_queryset(), pk=pk)
        return render(request, self.template_name_detail, {'device': device})

    def create_view(self, request):
        """创建视图"""
        if not request.user.has_perm(f'assets.add_{self.model._meta.model_name}'):
            messages.error(request, f'您没有添加{self.model._meta.verbose_name}的权限')
            return redirect(f'assets:{self.get_url_prefix()}_list')

        if request.method == 'POST':
            form = self.form_class(request.POST)
            if form.is_valid():
                # 检查用户是否有权操作选择的数据中心
                data_center = form.cleaned_data.get('data_center')
                if not request.user.is_admin and not request.user.data_centers.filter(id=data_center.id).exists():
                    messages.error(request, '您没有权限在该数据中心创建设备')
                    return self.form_invalid(form)

                device = form.save()
                messages.success(request, f'{self.model._meta.verbose_name} {device.name} 创建成功')
                return redirect(f'assets:{self.get_url_prefix()}_detail', pk=device.pk)
        else:
            form = self.form_class()
            # 限制数据中心选择
            if not request.user.is_admin:
                form.fields['data_center'].queryset = request.user.data_centers.all()

        context = {
            'form': form,
            'title': f'创建{self.model._meta.verbose_name}'
        }
        return render(request, self.template_name_form, context)

    def edit_view(self, request, pk):
        """编辑视图"""
        print("=== 编辑视图调试信息 ===")
        print(f"请求方法: {request.method}")
        print(f"设备ID: {pk}")
        
        device = get_object_or_404(self.get_queryset(), pk=pk)
        
        # 检查编辑权限
        model_name = self.model._meta.model_name
        perm = f'assets.change_{model_name}'
        
        print(f"用户: {request.user.username}")
        print(f"是否管理员: {request.user.is_admin}")
        print(f"权限: {perm}")
        
        if not request.user.has_perm(perm, device):
            messages.error(request, f'您没有修改{self.model._meta.verbose_name}的权限')
            return redirect(f'assets:{self.get_url_prefix()}_detail', pk=pk)
        
        if request.method == 'POST':
            form = self.form_class(request.POST, instance=device)
            if form.is_valid():
                # 检查用户是否有权限操作选择的数据中心
                data_center = form.cleaned_data.get('data_center')
                if not request.user.is_admin and not request.user.data_centers.filter(id=data_center.id).exists():
                    messages.error(request, '您没有权限将设备移动到该数据中心')
                    return self.form_invalid(form)

                device = form.save()
                messages.success(request, f'{self.model._meta.verbose_name} {device.name} 更新成功')
                return redirect(f'assets:{self.get_url_prefix()}_detail', pk=device.pk)
        else:
            form = self.form_class(instance=device)
            # 限制数据中心选择
            if not request.user.is_admin:
                form.fields['data_center'].queryset = request.user.data_centers.all()

        context = {
            'form': form,
            'device': device,
            'title': f'编辑{self.model._meta.verbose_name}',
            'can_edit': True,
            'model_type': self.get_url_prefix()
        }
        print(f"渲染模板: {self.template_name_form}")
        return render(request, self.template_name_form, context)

    def delete_view(self, request, pk):
        """删除视图"""
        device = get_object_or_404(self.get_queryset(), pk=pk)
        if request.method == 'POST':
            try:
                device_name = device.name
                device.delete()
                messages.success(request, f'{self.model._meta.verbose_name} {device_name} 已成功删除')
            except Exception as e:
                messages.error(request, f'删除失败：{str(e)}')
        return redirect(f'assets:{self.get_url_prefix()}_list')

    def history_view(self, request, pk):
        """历史记录视图"""
        # 获URL前缀
        url_prefixes = {
            'Server': 'server',
            'NetworkDevice': 'network',
            'StorageDevice': 'storage',
            'SecurityDevice': 'security'
        }
        url_prefix = url_prefixes.get(self.model.__name__, '')
        
        device = get_object_or_404(self.model, pk=pk)
        history = device.history.all().order_by('-history_date')
        
        # 处理历史记录
        history_list = list(history)
        for i in range(len(history_list)-1):
            current = history_list[i]
            previous = history_list[i+1]
            delta = current.diff_against(previous)
            current.changes = []
            for change in delta.changes:
                field_name = change.field
                try:
                    verbose_name = device._meta.get_field(field_name).verbose_name
                except:
                    verbose_name = field_name
                current.changes.append({
                    'field': verbose_name,
                    'old': change.old,
                    'new': change.new
                })
        
        context = {
            'device': device,
            'history': history_list,
            'view_list': f'assets:{url_prefix}_list'
        }
        return render(request, 'assets/device_history.html', context)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['model_type'] = self.model.__name__
        return context

    def has_datacenter_permission(self, datacenter_id):
        """检查用户是否有据中心权限"""
        return self.request.user.has_datacenter_perm(datacenter_id)

class ServerView(BaseDeviceView):
    template_name_list = 'assets/server_list.html'
    def dispatch(self, request, *args, **kwargs):
        """权限检查"""
        if not request.user.is_authenticated:
            return self.handle_no_permission()
            
        # 检查数据中心权限
        if 'pk' in kwargs:
            device = get_object_or_404(self.model, pk=kwargs['pk'])
            if not request.user.has_datacenter_perm(device.data_center.id):
                messages.error(request, '您没有该数据中心的操作权限')
                return redirect('assets:dashboard')
                
        return super().dispatch(request, *args, **kwargs)

class ServerView(BaseDeviceView):
    template_name_list = 'assets/server_list.html'
    template_name_detail = 'assets/server_detail.html'
    template_name_form = 'assets/device_form.html'
    model = Server
    form_class = ServerForm
    filter_class = ServerFilter
    resource_class = ServerResource

    def get(self, request, pk=None):
        if pk is None:
            queryset = self.get_queryset()
            filter = self.filter_class(request.GET, queryset=queryset)
            paginator = Paginator(filter.qs, settings.PAGINATION_PAGE_SIZE)
            page_number = request.GET.get('page')
            page_obj = paginator.get_page(page_number)
            
            context = {
                'filter': filter,
                'page_obj': page_obj,
                'model_name': self.model._meta.verbose_name,
                'model_type': self.model.__name__,
                'view_create': 'assets:server_create',
                'view_detail': 'assets:server_detail',
                'view_edit': 'assets:server_edit',
                'view_delete': 'assets:server_delete',
                'view_history': 'assets:server_history',
                'view_list': 'assets:server_list',
                'perms': {
                    'add': request.user.has_perm('assets.add_server'),
                    'change': request.user.has_perm('assets.change_server'),
                    'delete': request.user.has_perm('assets.delete_server'),
                    'view': request.user.has_perm('assets.view_server'),
                    'export': request.user.has_perm('assets.export_server'),
                    'import': request.user.has_perm('assets.import_server'),
                }
            }
            return render(request, self.template_name_list, context)
        else:
            device = get_object_or_404(self.get_queryset(), pk=pk)
            return render(request, self.template_name_detail, {'device': device})

    def post(self, request, pk=None):
        """处理POST请求"""
        if pk is None:
            # 创建
            if not request.user.has_perm('assets.add_server'):
                return JsonResponse({'status': 'error', 'message': '没有添加权限'})
            return self.create_view(request)
        else:
            # 检查是否是删除操作
            if 'delete' in request.path:
                return self.delete_view(request, pk)
            # 否则是更新操作
            if not request.user.has_perm('assets.change_server'):
                return JsonResponse({'status': 'error', 'message': '没有修改权限'})
            return self.edit_view(request, pk)

    def delete_view(self, request, pk):
        """删除视图"""
        if not request.user.has_perm('assets.delete_server'):
            messages.error(request, '您没有删除权限')
            return redirect('assets:server_list')

        device = get_object_or_404(self.get_queryset(), pk=pk)
        try:
            device_name = device.name
            device.delete()
            messages.success(request, f'{self.model._meta.verbose_name} {device_name} 已成功删除')
        except Exception as e:
            messages.error(request, f'删除失败：{str(e)}')
        
        return redirect('assets:server_list')

class NetworkDeviceView(BaseDeviceView):
    template_name_list = 'assets/network_list.html'
    template_name_detail = 'assets/network_detail.html'
    template_name_form = 'assets/device_form.html'
    model = NetworkDevice
    form_class = NetworkDeviceForm
    filter_class = NetworkDeviceFilter
    resource_class = NetworkDeviceResource

    def get(self, request, pk=None):
        if pk is None:
            queryset = self.get_queryset()
            filter = self.filter_class(request.GET, queryset=queryset)
            paginator = Paginator(filter.qs, settings.PAGINATION_PAGE_SIZE)
            page_number = request.GET.get('page')
            page_obj = paginator.get_page(page_number)
            
            context = {
                'filter': filter,
                'page_obj': page_obj,
                'model_name': self.model._meta.verbose_name,
                'model_type': self.model.__name__,
                'view_create': 'assets:network_create',
                'view_detail': 'assets:network_detail',
                'view_edit': 'assets:network_edit',
                'view_delete': 'assets:network_delete',
                'view_history': 'assets:network_history',
                'view_list': 'assets:network_list',
                'perms': {
                    'add': request.user.has_perm('assets.add_networkdevice'),
                    'change': request.user.has_perm('assets.change_networkdevice'),
                    'delete': request.user.has_perm('assets.delete_networkdevice'),
                    'view': request.user.has_perm('assets.view_networkdevice'),
                    'export': request.user.has_perm('assets.export_networkdevice'),
                    'import': request.user.has_perm('assets.import_networkdevice'),
                }
            }
            return render(request, self.template_name_list, context)
        else:
            device = get_object_or_404(self.get_queryset(), pk=pk)
            return render(request, self.template_name_detail, {'device': device})

    def post(self, request, pk=None):
        """处理POST请求"""
        if pk is None:
            # 创建
            if not request.user.has_perm('assets.add_networkdevice'):
                return JsonResponse({'status': 'error', 'message': '没有添加权限'})
            return self.create_view(request)
        else:
            # 检查是否是删除操作
            if 'delete' in request.path:
                return self.delete_view(request, pk)
            # 否则是更新操作
            if not request.user.has_perm('assets.change_networkdevice'):
                return JsonResponse({'status': 'error', 'message': '没有修改权限'})
            return self.edit_view(request, pk)

    def delete_view(self, request, pk):
        """删除视图"""
        if not request.user.has_perm('assets.delete_networkdevice'):
            messages.error(request, '您没有删除权限')
            return redirect('assets:network_list')

        device = get_object_or_404(self.get_queryset(), pk=pk)
        try:
            device_name = device.name
            device.delete()
            messages.success(request, f'{self.model._meta.verbose_name} {device_name} 已成功删除')
        except Exception as e:
            messages.error(request, f'删除失败：{str(e)}')
        
        return redirect('assets:network_list')

class StorageDeviceView(BaseDeviceView):
    template_name_list = 'assets/storage_list.html'
    template_name_detail = 'assets/storage_detail.html'
    template_name_form = 'assets/device_form.html'
    model = StorageDevice
    form_class = StorageDeviceForm
    filter_class = StorageDeviceFilter
    resource_class = StorageDeviceResource

    def get(self, request, pk=None):
        if pk is None:
            queryset = self.get_queryset()
            filter = self.filter_class(request.GET, queryset=queryset)
            paginator = Paginator(filter.qs, settings.PAGINATION_PAGE_SIZE)
            page_number = request.GET.get('page')
            page_obj = paginator.get_page(page_number)
            
            context = {
                'filter': filter,
                'page_obj': page_obj,
                'model_name': self.model._meta.verbose_name,
                'model_type': self.model.__name__,
                'view_create': 'assets:storage_create',
                'view_detail': 'assets:storage_detail',
                'view_edit': 'assets:storage_edit',
                'view_delete': 'assets:storage_delete',
                'view_history': 'assets:storage_history',
                'view_list': 'assets:storage_list',
                'perms': {
                    'add': request.user.has_perm('assets.add_storagedevice'),
                    'change': request.user.has_perm('assets.change_storagedevice'),
                    'delete': request.user.has_perm('assets.delete_storagedevice'),
                    'view': request.user.has_perm('assets.view_storagedevice'),
                    'export': request.user.has_perm('assets.export_storagedevice'),
                    'import': request.user.has_perm('assets.import_storagedevice'),
                }
            }
            return render(request, self.template_name_list, context)
        else:
            device = get_object_or_404(self.get_queryset(), pk=pk)
            return render(request, self.template_name_detail, {'device': device})

    def post(self, request, pk=None):
        """处理POST请求"""
        if pk is None:
            if not request.user.has_perm('assets.add_storagedevice'):
                return JsonResponse({'status': 'error', 'message': '没有添加权限'})
            return self.create_view(request)
        else:
            if 'delete' in request.path:
                return self.delete_view(request, pk)
            if not request.user.has_perm('assets.change_storagedevice'):
                return JsonResponse({'status': 'error', 'message': '没有修改权限'})
            return self.edit_view(request, pk)

class SecurityDeviceView(BaseDeviceView):
    template_name_list = 'assets/security_list.html'
    template_name_detail = 'assets/security_detail.html'
    template_name_form = 'assets/device_form.html'
    model = SecurityDevice
    form_class = SecurityDeviceForm
    filter_class = SecurityDeviceFilter
    resource_class = SecurityDeviceResource

    def get(self, request, pk=None):
        if pk is None:
            queryset = self.get_queryset()
            filter = self.filter_class(request.GET, queryset=queryset)
            paginator = Paginator(filter.qs, settings.PAGINATION_PAGE_SIZE)
            page_number = request.GET.get('page')
            page_obj = paginator.get_page(page_number)
            
            context = {
                'filter': filter,
                'page_obj': page_obj,
                'model_name': self.model._meta.verbose_name,
                'model_type': self.model.__name__,
                'view_create': 'assets:security_create',
                'view_detail': 'assets:security_detail',
                'view_edit': 'assets:security_edit',
                'view_delete': 'assets:security_delete',
                'view_history': 'assets:security_history',
                'view_list': 'assets:security_list',
                'perms': {
                    'add': request.user.has_perm('assets.add_securitydevice'),
                    'change': request.user.has_perm('assets.change_securitydevice'),
                    'delete': request.user.has_perm('assets.delete_securitydevice'),
                    'view': request.user.has_perm('assets.view_securitydevice'),
                    'export': request.user.has_perm('assets.export_securitydevice'),
                    'import': request.user.has_perm('assets.import_securitydevice'),
                }
            }
            return render(request, self.template_name_list, context)
        else:
            device = get_object_or_404(self.get_queryset(), pk=pk)
            return render(request, self.template_name_detail, {'device': device})

    def post(self, request, pk=None):
        """处理POST请求"""
        if pk is None:
            if not request.user.has_perm('assets.add_securitydevice'):
                return JsonResponse({'status': 'error', 'message': '没有添加权限'})
            return self.create_view(request)
        else:
            if 'delete' in request.path:
                return self.delete_view(request, pk)
            if not request.user.has_perm('assets.change_securitydevice'):
                return JsonResponse({'status': 'error', 'message': '没有修改权限'})
            return self.edit_view(request, pk)

@require_POST
@permission_required('assets.delete_device')
def batch_delete(request):
    try:
        data = json.loads(request.body)
        ids = data.get('ids', [])
        
        # 记录操作日志
        for device_id in ids:
            device = get_object_or_404(Device, id=device_id)
            LogEntry.objects.create(
                user=request.user,
                content_type=ContentType.objects.get_for_model(device),
                object_id=device.id,
                object_repr=str(device),
                action_flag=DELETION,
                change_message=f'批删除操作'
            )
        
        # 执行删除
        Device.objects.filter(id__in=ids).delete()
        
        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}) 

def server_create(request):
    """创建服务器视图"""
    if request.method == 'POST':
        form = ServerForm(request.POST)
        if form.is_valid():
            data_center = form.cleaned_data.get('data_center')
            if not request.user.is_admin and not request.user.data_centers.filter(id=data_center.id).exists():
                messages.error(request, '您没有权限在该数据中心创建设备')
                return render(request, 'assets/device_form.html', {
                    'form': form,
                    'title': '添加服务器',
                    'model_type': 'server'
                })

            device = form.save()
            messages.success(request, f'服务器 {device.name} 创建成功')
            return redirect('assets:server_list')
    else:
        form = ServerForm()
        if not request.user.is_admin:
            form.fields['data_center'].queryset = request.user.data_centers.all()

    return render(request, 'assets/device_form.html', {
        'form': form,
        'title': '添加服务器',
        'model_type': 'server'
    })

def network_create(request):
    """创建网络设备视图"""
    if request.method == 'POST':
        form = NetworkDeviceForm(request.POST)
        if form.is_valid():
            data_center = form.cleaned_data.get('data_center')
            if not request.user.is_admin and not request.user.data_centers.filter(id=data_center.id).exists():
                messages.error(request, '您没有权限在该数据中心创建设备')
                return render(request, 'assets/device_form.html', {
                    'form': form,
                    'title': '添加网络设备',
                    'model_type': 'network'
                })

            device = form.save()
            messages.success(request, f'网络设备 {device.name} 创建成功')
            return redirect('assets:network_list')
    else:
        form = NetworkDeviceForm()
        if not request.user.is_admin:
            form.fields['data_center'].queryset = request.user.data_centers.all()

    return render(request, 'assets/device_form.html', {
        'form': form,
        'title': '添加网络设备',
        'model_type': 'network'
    })

def storage_create(request):
    """创建存储设备视图"""
    if request.method == 'POST':
        form = StorageDeviceForm(request.POST)
        if form.is_valid():
            data_center = form.cleaned_data.get('data_center')
            if not request.user.is_admin and not request.user.data_centers.filter(id=data_center.id).exists():
                messages.error(request, '您没有权限在该数据中心创建设备')
                return render(request, 'assets/device_form.html', {
                    'form': form,
                    'title': '添加存储设备',
                    'model_type': 'storage'
                })

            device = form.save()
            messages.success(request, f'存储设备 {device.name} 创建成功')
            return redirect('assets:storage_list')
    else:
        form = StorageDeviceForm()
        if not request.user.is_admin:
            form.fields['data_center'].queryset = request.user.data_centers.all()

    return render(request, 'assets/device_form.html', {
        'form': form,
        'title': '添加存储设备',
        'model_type': 'storage'
    })

def security_create(request):
    """创建安全设备视图"""
    if request.method == 'POST':
        form = SecurityDeviceForm(request.POST)
        if form.is_valid():
            data_center = form.cleaned_data.get('data_center')
            if not request.user.is_admin and not request.user.data_centers.filter(id=data_center.id).exists():
                messages.error(request, '您没有权限在该数据中心创建设备')
                return render(request, 'assets/device_form.html', {
                    'form': form,
                    'title': '添加安全设备',
                    'model_type': 'security'
                })

            device = form.save()
            messages.success(request, f'安全设备 {device.name} 创建成功')
            return redirect('assets:security_list')
    else:
        form = SecurityDeviceForm()
        if not request.user.is_admin:
            form.fields['data_center'].queryset = request.user.data_centers.all()

    return render(request, 'assets/device_form.html', {
        'form': form,
        'title': '添加安全设备',
        'model_type': 'security'
    })

# 更新 __all__ 列表，添加新的视图函数
__all__ = [
    'ServerView', 
    'NetworkDeviceView', 
    'StorageDeviceView', 
    'SecurityDeviceView',
    'server_create',
    'network_create',
    'storage_create',
    'security_create'
] 