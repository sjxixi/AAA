from django.views.generic import DeleteView
from django.http import JsonResponse
from django.urls import reverse_lazy
from .models import Server
from .forms import ServerForm
from django.shortcuts import render, redirect
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