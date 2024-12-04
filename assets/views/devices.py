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

class BaseDeviceView(View):
    """设备视图基类"""
    template_name_list = None
    template_name_detail = None
    template_name_form = None
    model = None
    form_class = None
    filter_class = None
    resource_class = None

    @method_decorator(login_required)
    def get(self, request, pk=None):
        """处理GET请求"""
        if pk is None:
            if 'create' in request.path:
                return self.create_view(request)
            return self.list_view(request)
        if 'edit' in request.path:
            return self.edit_view(request, pk)
        if 'history' in request.path:
            return self.history_view(request, pk)
        return self.detail_view(request, pk)

    @method_decorator(login_required)
    def post(self, request, pk=None):
        """处理POST请求"""
        if pk is None:
            return self.create_view(request)
        if 'delete' in request.path:
            return self.delete_view(request, pk)
        return self.edit_view(request, pk)

    def dispatch(self, request, *args, **kwargs):
        """处理请求分发"""
        if request.method.lower() in self.http_method_names:
            handler = getattr(self, request.method.lower(), self.http_method_not_allowed)
        else:
            handler = self.http_method_not_allowed
        return handler(request, *args, **kwargs)

    def list_view(self, request):
        """列表视图"""
        # 添加默认排序
        queryset = self.model.objects.all().order_by('id')
        filter = self.filter_class(request.GET, queryset=queryset)
        
        # 处理导出请求
        if 'export' in request.GET:
            resource = self.resource_class()
            dataset = resource.export(filter.qs)
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
        
        # 获取设备类型的中文名称
        device_types = {
            'Server': '服务器',
            'NetworkDevice': '网络设备',
            'StorageDevice': '存储设备',
            'SecurityDevice': '安全设备'
        }
        model_name = device_types.get(self.model.__name__, '')
        
        # 获取URL前缀
        url_prefixes = {
            'Server': 'server',
            'NetworkDevice': 'network',
            'StorageDevice': 'storage',
            'SecurityDevice': 'security'
        }
        url_prefix = url_prefixes.get(self.model.__name__, '')
        
        context = {
            'filter': filter,
            'page_obj': page_obj,
            'model_name': model_name,  # 使用中文名称
            'view_create': f'assets:{url_prefix}_create',
            'view_detail': f'assets:{url_prefix}_detail',
            'view_edit': f'assets:{url_prefix}_edit',
            'view_delete': f'assets:{url_prefix}_delete',
            'view_history': f'assets:{url_prefix}_history',
            'colspan': len(self.model._meta.fields) + 1  # +1 for actions column
        }
        return render(request, self.template_name_list, context)

    def detail_view(self, request, pk):
        """详情视图"""
        device = get_object_or_404(self.model, pk=pk)
        return render(request, self.template_name_detail, {'device': device})

    def create_view(self, request):
        """创建视图"""
        # 获取URL前缀
        url_prefixes = {
            'Server': 'server',
            'NetworkDevice': 'network',
            'StorageDevice': 'storage',
            'SecurityDevice': 'security'
        }
        url_prefix = url_prefixes.get(self.model.__name__, '')
        
        if request.method == 'POST':
            form = self.form_class(request.POST)
            if form.is_valid():
                device = form.save()
                messages.success(request, f'{self.model._meta.verbose_name} {device.name} 创建成功')
                return redirect(f'assets:{url_prefix}_detail', pk=device.pk)
        else:
            form = self.form_class()
        
        context = {
            'form': form,
            'title': f'创建{self.model._meta.verbose_name}',
            'view_list': f'assets:{url_prefix}_list'
        }
        return render(request, self.template_name_form, context)

    def edit_view(self, request, pk):
        """编辑视图"""
        # 获取URL前缀
        url_prefixes = {
            'Server': 'server',
            'NetworkDevice': 'network',
            'StorageDevice': 'storage',
            'SecurityDevice': 'security'
        }
        url_prefix = url_prefixes.get(self.model.__name__, '')
        
        device = get_object_or_404(self.model, pk=pk)
        if request.method == 'POST':
            form = self.form_class(request.POST, instance=device)
            if form.is_valid():
                device = form.save()
                messages.success(request, f'{self.model._meta.verbose_name} {device.name} 更新成功')
                return redirect(f'assets:{url_prefix}_detail', pk=device.pk)
        else:
            form = self.form_class(instance=device)
        
        context = {
            'form': form,
            'device': device,
            'title': f'编辑{self.model._meta.verbose_name}',
            'view_list': f'assets:{url_prefix}_list'
        }
        return render(request, self.template_name_form, context)

    def delete_view(self, request, pk):
        """删除视图"""
        if request.method == 'POST':
            try:
                device = get_object_or_404(self.model, pk=pk)
                device_name = device.name
                device.delete()
                messages.success(request, f'{self.model._meta.verbose_name} {device_name} 已成功删除')
            except Exception as e:
                messages.error(request, f'删除失败：{str(e)}')
        
        # 获取URL前缀
        url_prefixes = {
            'Server': 'server',
            'NetworkDevice': 'network',
            'StorageDevice': 'storage',
            'SecurityDevice': 'security'
        }
        url_prefix = url_prefixes.get(self.model.__name__, '')
        return redirect(f'assets:{url_prefix}_list')

    def history_view(self, request, pk):
        """历史记录视图"""
        # 获取URL前缀
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

class ServerView(BaseDeviceView):
    template_name_list = 'assets/server_list.html'
    template_name_detail = 'assets/server_detail.html'
    template_name_form = 'assets/device_form.html'
    model = Server
    form_class = ServerForm
    filter_class = ServerFilter
    resource_class = ServerResource

class NetworkDeviceView(BaseDeviceView):
    template_name_list = 'assets/network_list.html'
    template_name_detail = 'assets/network_detail.html'
    template_name_form = 'assets/device_form.html'
    model = NetworkDevice
    form_class = NetworkDeviceForm
    filter_class = NetworkDeviceFilter
    resource_class = NetworkDeviceResource

class StorageDeviceView(BaseDeviceView):
    template_name_list = 'assets/storage_list.html'
    template_name_detail = 'assets/storage_detail.html'
    template_name_form = 'assets/device_form.html'
    model = StorageDevice
    form_class = StorageDeviceForm
    filter_class = StorageDeviceFilter
    resource_class = StorageDeviceResource

class SecurityDeviceView(BaseDeviceView):
    template_name_list = 'assets/security_list.html'
    template_name_detail = 'assets/security_detail.html'
    template_name_form = 'assets/device_form.html'
    model = SecurityDevice
    form_class = SecurityDeviceForm
    filter_class = SecurityDeviceFilter
    resource_class = SecurityDeviceResource 