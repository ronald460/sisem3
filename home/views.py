from django.shortcuts import render
from django.http import JsonResponse
from .models import *

# Create your views here.



def reportes(request):
    return render(request, 'reportes.html')

def listado_reportes(request):
    
    entity = Reporte.objects.filter(activo=True).order_by('-created_at')
    data = [
            {
                'nombre': c.name,
                'url': c.url,
                'id': c.id,
                } for c in entity
            ]
    return JsonResponse({'data':data}, safe=False)