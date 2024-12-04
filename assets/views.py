from django.views.generic import DeleteView
from django.http import JsonResponse
from django.urls import reverse_lazy
from .models import Server

class ServerDeleteView(DeleteView):
    model = Server
    success_url = reverse_lazy('assets:server_list')
    
    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.delete()
        return JsonResponse({'status': 'success'}) 