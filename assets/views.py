from django.views.generic import DeleteView
from django.http import JsonResponse
from django.urls import reverse_lazy
from .models import Server, DataCenter, NetworkDevice, StorageDevice, SecurityDevice
from .forms import ServerForm
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages

class ServerDeleteView(DeleteView):
    model = Server
    success_url = reverse_lazy('assets:server_list')
    
    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.delete()
        return JsonResponse({'status': 'success'}) 

def server_create(request):
    if request.method == 'POST':
        form = ServerForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, '服务器添加成功！')
            return redirect('assets:server_list')
    else:
        form = ServerForm()
    
    return render(request, 'assets/server_form.html', {
        'form': form,
        'title': '添加服务器'
    }) 

def datacenter_detail(request, pk):
    datacenter = get_object_or_404(DataCenter, pk=pk)
    context = {
        'datacenter': datacenter,
        'servers': Server.objects.filter(data_center=datacenter),
        'network_devices': NetworkDevice.objects.filter(data_center=datacenter),
        'storage_devices': StorageDevice.objects.filter(data_center=datacenter),
        'security_devices': SecurityDevice.objects.filter(data_center=datacenter),
    }
    return render(request, 'assets/datacenter_detail.html', context) 