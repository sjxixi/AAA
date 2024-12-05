from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.admin.models import LogEntry, DELETION
from django.contrib.contenttypes.models import ContentType
from django.db.models import Count
from ..models import DataCenter, Server, NetworkDevice, StorageDevice, SecurityDevice
from ..forms import DataCenterForm
from ..filters import DataCenterFilter
from ..resources import DataCenterResource
from ..resources.devices import (
    ServerResource, NetworkDeviceResource,
    StorageDeviceResource, SecurityDeviceResource
)
from tablib import Dataset
import datetime
import json


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
    """数据中心史记录视图"""
    datacenter = get_object_or_404(DataCenter, pk=pk)
    history = datacenter.history.all().order_by('-history_date')

    # 处理历史记录
    history_list = list(history)
    for i in range(len(history_list) - 1):
        current = history_list[i]
        previous = history_list[i + 1]
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


# 导入相关视图
@login_required
@permission_required('assets.add_device')
def import_data(request):
    if request.method == 'POST' and request.FILES.get('file'):
        try:
            model_type = request.POST.get('model_type')
            model_map = {
                'Server': Server,
                'NetworkDevice': NetworkDevice,
                'StorageDevice': StorageDevice,
                'SecurityDevice': SecurityDevice,
                'DataCenter': DataCenter
            }

            model = model_map.get(model_type)
            if not model:
                messages.error(request, '无效的设备类型')
                return redirect(request.META.get('HTTP_REFERER', '/'))

            # 获取对应的Resource类
            resource_map = {
                'Server': ServerResource,
                'NetworkDevice': NetworkDeviceResource,
                'StorageDevice': StorageDeviceResource,
                'SecurityDevice': SecurityDeviceResource,
                'DataCenter': DataCenterResource
            }

            resource_class = resource_map.get(model_type)
            if not resource_class:
                messages.error(request, '无效的资源类型')
                return redirect(request.META.get('HTTP_REFERER', '/'))

            # 读取文件内容
            file_content = request.FILES['file'].read()
            if not file_content:
                messages.error(request, '文件内容为空')
                return redirect(request.META.get('HTTP_REFERER', '/'))

            resource = resource_class()
            dataset = Dataset()

            # 尝试加载不同格式
            try:
                imported_data = dataset.load(file_content, format='xlsx')
            except:
                try:
                    imported_data = dataset.load(file_content, format='xls')
                except Exception as e:
                    messages.error(request, f'不支持的文件格式: {str(e)}')
                    return redirect(request.META.get('HTTP_REFERER', '/'))

            if len(dataset) == 0:
                messages.error(request, '文件中没有数据')
                return redirect(request.META.get('HTTP_REFERER', '/'))

            # 必填字段定义
            required_fields = {
                'Server': ['name', 'sn', 'manufacturer', 'data_center', 'ip_address', 'mac_address', 'hostname'],
                'NetworkDevice': ['name', 'sn', 'manufacturer', 'data_center', 'ip_address', 'mac_address',
                                  'device_type'],
                'StorageDevice': ['name', 'sn', 'manufacturer', 'data_center', 'ip_address', 'mac_address',
                                  'storage_type'],
                'SecurityDevice': ['name', 'sn', 'manufacturer', 'data_center', 'ip_address', 'mac_address',
                                   'security_type'],
                'DataCenter': ['name', 'location', 'contact', 'phone']
            }

            # 获取当前设备类型的必填字段
            required = required_fields.get(model_type, [])

            # 检查必填字段是否存在
            missing_fields = []
            for field in required:
                field_obj = resource.fields.get(field)
                if field_obj and hasattr(field_obj, 'column_name'):
                    if field_obj.column_name not in dataset.headers:
                        missing_fields.append(field_obj.column_name)
                elif field not in dataset.headers:
                    missing_fields.append(field)

            if missing_fields:
                messages.error(request, f'缺少必填字段: {", ".join(missing_fields)}')
                return redirect(request.META.get('HTTP_REFERER', '/'))

            # 先进行测试导入
            result = resource.import_data(dataset, dry_run=True)

            if not result.has_errors():
                # 如果测试通过，执行实际导入
                result = resource.import_data(dataset, dry_run=False)
                messages.success(request, f'成功导入 {result.total_rows} 条数据')
            else:
                # 收集所有错误信息
                error_messages = []

                # 处理行级错误
                if hasattr(result, 'row_errors'):
                    for row_number, errors in result.row_errors():
                        for error in errors:
                            error_messages.append(f'第 {row_number} 行: {error.error}')

                # 处理验证错误
                if hasattr(result, 'validation_errors'):
                    for error in result.validation_errors:
                        error_messages.append(str(error))

                # 处理无效行
                if hasattr(result, 'invalid_rows'):
                    for row in result.invalid_rows:
                        for error in row.errors:
                            error_messages.append(f'第 {row.number} 行: {error.error}')

                if error_messages:
                    messages.error(request, '导入失败:\n' + '\n'.join(error_messages))
                else:
                    messages.error(request, '导入失败，请检查以下问题：\n'
                                            '1. 必填字段是否都已填写\n'
                                            '2. 字段格式是否正确\n'
                                            '3. 唯一字段是否重复\n'
                                            '4. 日期格式是否为YYYY-MM-DD\n'
                                            '5. 数据中心名称是否存在')

        except Exception as e:
            messages.error(request, f'导入失败: {str(e)}')

    return redirect(request.META.get('HTTP_REFERER', '/'))


@login_required
def download_template(request):
    model_type = request.GET.get('type')
    model_map = {
        'Server': Server,
        'NetworkDevice': NetworkDevice,
        'StorageDevice': StorageDevice,
        'SecurityDevice': SecurityDevice,
        'DataCenter': DataCenter
    }

    model = model_map.get(model_type)
    if not model:
        return HttpResponse('无效的设备类型', status=400)

    # 获取对应的Resource类
    resource_map = {
        'Server': ServerResource,
        'NetworkDevice': NetworkDeviceResource,
        'StorageDevice': StorageDeviceResource,
        'SecurityDevice': SecurityDeviceResource,
        'DataCenter': DataCenterResource
    }

    # 示例数据
    example_data = {
        'Server': {
            'name': '示例服务器',
            'model': 'Dell R740',
            'sn': 'DELL12345678',
            'manufacturer': 'Dell',
            'purchase_date': '2024-01-01',
            'warranty_date': '2027-01-01',
            'status': '运行中',
            'data_center': '北京数据中心',
            'rack_position': 'A01-01',
            'ip_address': '192.168.1.100',
            'mac_address': '00:11:22:33:44:55',
            'description': '这是一个示例服务器',
            'hostname': 'server-bj-01',
            'cpu_model': 'Intel Xeon Gold 6248R',
            'cpu_count': '2',
            'cpu_cores': '24',
            'memory_size': '256',
            'disk_info': '2TB SSD x 4',
            'os_type': 'CentOS',
            'os_version': '7.9',
            'business_system': '示例系统'
        },
        'NetworkDevice': {
            'name': '示例交换机',
            'model': 'Cisco Nexus 9300',
            'sn': 'CISCO12345678',
            'manufacturer': 'Cisco',
            'purchase_date': '2024-01-01',
            'warranty_date': '2027-01-01',
            'status': '运行中',
            'data_center': '北京数据中心',
            'rack_position': 'A01-02',
            'ip_address': '192.168.1.101',
            'mac_address': '00:11:22:33:44:66',
            'description': '这是一个示例交换机',
            'device_type': '核心交换机',
            'port_count': '48',
            'port_info': '40GE x 48',
            'management_ip': '192.168.1.102',
            'vlan_info': 'VLAN 1-100',
            'routing_info': 'OSPF, BGP'
        },
        'StorageDevice': {
            'name': '示例存储',
            'model': 'EMC Unity 480F',
            'sn': 'EMC12345678',
            'manufacturer': 'EMC',
            'purchase_date': '2024-01-01',
            'warranty_date': '2027-01-01',
            'status': '运行中',
            'data_center': '北京数据中心',
            'rack_position': 'A01-03',
            'ip_address': '192.168.1.103',
            'mac_address': '00:11:22:33:44:77',
            'description': '这是一个示例存储',
            'storage_type': 'All Flash',
            'capacity': '100',
            'raid_type': 'RAID 5',
            'disk_count': '24',
            'disk_info': '3.84TB SSD x 24'
        },
        'SecurityDevice': {
            'name': '示例防火墙',
            'model': 'Palo Alto PA-5250',
            'sn': 'PALO12345678',
            'manufacturer': 'Palo Alto',
            'purchase_date': '2024-01-01',
            'warranty_date': '2027-01-01',
            'status': '运行中',
            'data_center': '北京数据中心',
            'rack_position': 'A01-04',
            'ip_address': '192.168.1.104',
            'mac_address': '00:11:22:33:44:88',
            'description': '这是一个示例防火墙',
            'security_type': 'NGFW',
            'throughput': '20Gbps',
            'policy_count': '1000',
            'firmware_version': '10.1.0'
        },
        'DataCenter': {
            'name': '示例数据中心',
            'location': '北京市海淀区',
            'contact': '张三',
            'phone': '13800138000',
            'address': '北京市海淀区示例路123号',
            'description': '这是一个示例数据中心'
        }
    }

    resource_class = resource_map.get(model_type)
    if not resource_class:
        return HttpResponse('无效的资源类型', status=400)

    resource = resource_class()
    dataset = Dataset()

    # 获取表头和字段映射
    headers = []
    fields = []
    for field in resource.get_fields():
        if hasattr(field, 'column_name'):
            headers.append(field.column_name)
            fields.append(field.attribute)
        else:
            headers.append(field.attribute)
            fields.append(field.attribute)

    dataset.headers = headers

    # 添加示例数据
    example = example_data.get(model_type, {})
    if example:
        # 根据字段名获取对应的示例值
        row = []
        for field in fields:
            row.append(example.get(field, ''))
        dataset.append(row)

        # 添加一个空行，用于用户填写
        dataset.append([''] * len(headers))

    response = HttpResponse(
        dataset.export('xlsx'),
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = f'attachment; filename="{model._meta.verbose_name}_template.xlsx"'
    return response


@require_POST
@permission_required('assets.delete_device')
def batch_delete(request):
    try:
        data = json.loads(request.body)
        ids = data.get('ids', [])
        device_type = data.get('type', '')  # 添加设备类型参数

        # 根据设备类型选择模型
        model_map = {
            'Server': Server,
            'NetworkDevice': NetworkDevice,
            'StorageDevice': StorageDevice,
            'SecurityDevice': SecurityDevice,
            'DataCenter': DataCenter
        }

        model = model_map.get(device_type)
        if not model:
            return JsonResponse({
                'success': False,
                'message': f'无效的设备类型: {device_type}，可用类型: {list(model_map.keys())}'
            })

        # 记录操作日志
        for item_id in ids:
            item = get_object_or_404(model, id=item_id)
            LogEntry.objects.create(
                user=request.user,
                content_type=ContentType.objects.get_for_model(item),
                object_id=item.id,
                object_repr=str(item),
                action_flag=DELETION,
                change_message=f'批量删除操作'
            )

        # 执行删除
        deleted_count = model.objects.filter(id__in=ids).delete()[0]

        return JsonResponse({
            'success': True,
            'message': f'成功删除 {deleted_count} 项'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'删除失败: {str(e)}'
        })