from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse
from django.db.models import Count
from ..models import DataCenter, Server, NetworkDevice, StorageDevice, SecurityDevice
from ..forms import DataCenterForm
from ..filters import DataCenterFilter
from ..resources import DataCenterResource
import datetime

@login_required
def dashboard(request):
    """仪表盘视图"""
    # 获取所有数据中心
    datacenters = DataCenter.objects.all()
    
    # 为每个数据中心添加设备统计
    for dc in datacenters:
        dc.server_count = dc.server_set.count()
        dc.network_count = dc.networkdevice_set.count()
        dc.storage_count = dc.storagedevice_set.count()
        dc.security_count = dc.securitydevice_set.count()
    
    context = {
        'datacenter_count': DataCenter.objects.count(),
        'server_count': Server.objects.count(),
        'network_count': NetworkDevice.objects.count(),
        'storage_count': StorageDevice.objects.count(),
        'security_count': SecurityDevice.objects.count(),
        'datacenters': datacenters
    }
    return render(request, 'assets/dashboard.html', context)

@login_required
def datacenter_list(request):
    """数据中心列表视图"""
    filter = DataCenterFilter(request.GET, queryset=DataCenter.objects.all())
    
    # 处理导出请求
    if 'export' in request.GET:
        resource = DataCenterResource()
        dataset = resource.export(filter.qs)
        response = HttpResponse(
            dataset.export('xlsx'),
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = f'attachment; filename="datacenters_{datetime.date.today()}.xlsx"'
        return response
    
    context = {
        'filter': filter,
        'datacenters': filter.qs
    }
    return render(request, 'assets/datacenter_list.html', context)

@login_required
def datacenter_detail(request, pk):
    """数据中心详情视图"""
    datacenter = get_object_or_404(DataCenter, pk=pk)
    return render(request, 'assets/datacenter_detail.html', {'datacenter': datacenter})

@login_required
def datacenter_create(request):
    """创建数据中心视图"""
    if request.method == 'POST':
        form = DataCenterForm(request.POST)
        if form.is_valid():
            datacenter = form.save()
            messages.success(request, f'数据中心 {datacenter.name} 创建成功')
            return redirect('assets:datacenter_detail', pk=datacenter.pk)
    else:
        form = DataCenterForm()
    return render(request, 'assets/datacenter_form.html', {'form': form, 'title': '创建数据中心'})

@login_required
def datacenter_edit(request, pk):
    """编辑数据中心视图"""
    datacenter = get_object_or_404(DataCenter, pk=pk)
    if request.method == 'POST':
        form = DataCenterForm(request.POST, instance=datacenter)
        if form.is_valid():
            datacenter = form.save()
            messages.success(request, f'数据中心 {datacenter.name} 更新成功')
            return redirect('assets:datacenter_detail', pk=datacenter.pk)
    else:
        form = DataCenterForm(instance=datacenter)
    return render(request, 'assets/datacenter_form.html', 
                 {'form': form, 'datacenter': datacenter, 'title': '编辑数据中心'})

@login_required
def datacenter_delete(request, pk):
    """删除数据中心视图"""
    datacenter = get_object_or_404(DataCenter, pk=pk)
    if request.method == 'POST':
        try:
            datacenter.delete()
            messages.success(request, f'数据中心 {datacenter.name} 已成功删除')
        except Exception as e:
            messages.error(request, f'删除失败：{str(e)}')
    return redirect('assets:datacenter_list')

@login_required
def datacenter_history(request, pk):
    """数据中心历史记录视图"""
    datacenter = get_object_or_404(DataCenter, pk=pk)
    history = datacenter.history.all().order_by('-history_date')
    
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
                verbose_name = datacenter._meta.get_field(field_name).verbose_name
            except:
                verbose_name = field_name
            current.changes.append({
                'field': verbose_name,
                'old': change.old,
                'new': change.new
            })
    
    return render(request, 'assets/datacenter_history.html', {
        'datacenter': datacenter,
        'history': history_list
    }) 