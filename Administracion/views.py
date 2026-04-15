from django.views.decorators.cache import never_cache
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from Bienes.models import Bienes, encargado_bienes
from Bienes.utils import get_user_role
from django.http import JsonResponse
from django.contrib import messages
from django.core.cache import cache
from datetime import date
from .models import *
from .forms import *
import requests


def obtener_tasas_api():
    cache_key = 'tasas_cambio_completas'
    tasas = cache.get(cache_key)
    
    if not tasas:
        try:
            # Usar Frankfurter API (gratuita y confiable)
            url = 'https://api.frankfurter.app/latest?from=USD&to=VES'
            response = requests.get(url, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                dolar = data['rates']['VES']
                
                # Obtener euro desde USD
                url_eur = 'https://api.frankfurter.app/latest?from=EUR&to=USD,VES'
                response_eur = requests.get(url_eur, timeout=5)
                
                if response_eur.status_code == 200:
                    data_eur = response_eur.json()
                    euro_usd = data_eur['rates']['USD']
                    euro_ves = data_eur['rates']['VES']
                    
                    tasas = {
                        'dolar': f"{dolar:.2f}",
                        'euro': f"{euro_ves:.2f}",
                        'euro_usd': f"{euro_usd:.2f}",
                    }
                    
                    # Cache por 1 hora
                    cache.set(cache_key, tasas, 3600)
                else:
                    tasas = {
                        'dolar': f"{dolar:.2f}",
                        'euro': "No disponible",
                    }
            else:
                tasas = obtener_tasas_fallback()
                
        except Exception as e:
            print(f"Error en API: {e}")
            tasas = obtener_tasas_fallback()
    
    return tasas

def obtener_tasas_fallback():
    """API de respaldo"""
    try:
        # Usar ExchangeRate-API
        url = 'https://api.exchangerate-api.com/v4/latest/USD'
        response = requests.get(url, timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            dolar_ves = data['rates'].get('VES', 'N/A')
            
            # Obtener EUR
            url_eur = 'https://api.exchangerate-api.com/v4/latest/EUR'
            response_eur = requests.get(url_eur, timeout=5)
            
            if response_eur.status_code == 200:
                data_eur = response_eur.json()
                euro_ves = data_eur['rates'].get('VES', 'N/A')
                
                return {
                    'dolar': str(dolar_ves),
                    'euro': str(euro_ves),
                }
    except:
        pass
    
    return {
        'dolar': "No disponible",
        'euro': "No disponible",
    }

def Home(request):
    empleados = Empleado.objects.all().count()
    bienes = Bienes.objects.all().count()

    user = request.user

    tasas = obtener_tasas_api()
    
    context = {
        'empleados': empleados,
        'bienes': bienes,
        'euro': tasas.get('euro', 'No disponible'),
        'dolar': tasas.get('dolar', 'No disponible'),
        'user': user,
    }
    return render(request, 'home.html', context)

def Funcionarios(request):

    return render(request,"administracion/funcionarios.html")

@never_cache
@login_required
def lista_funcionarios(request):

    usuario_actual = request.user
    rol = get_user_role(usuario_actual)

    if rol == 'admin':

        entity = Empleado.objects.all()
        data = [
            {
                'cedula': c.document,
                'nombre': c.names, 
                'telefono': c.phone,
                'status': c.condition.capitalize(),
                'cargo': c.position,
                'area': c.area.name,
                'id': c.id,
                } for c in entity
            ]
        return JsonResponse({'data':data}, safe=False)
    
    elif rol[0] == 'encargado_bienes':
        area = rol[1]
        
        entity = Empleado.objects.filter(area=area)
        data = [
            {
                'cedula': c.document,
                'nombre': c.names, 
                'telefono': c.phone,
                'status': c.condition.capitalize(),
                'cargo': c.position,
                'area': c.area.name,
                'id': c.id,
                } for c in entity
            ]
        return JsonResponse({'data':data}, safe=False)
    
    else:

        entity = Empleado.objects.filter(user = usuario_actual)
        data = [
            {
                'cedula': c.document,
                'nombre': c.names, 
                'telefono': c.phone,
                'status': c.condition.capitalize(),
                'cargo': c.position,
                'area': c.area.name,
                'id': c.id,
                } for c in entity
            ]
        return JsonResponse({'data':data}, safe=False)

@never_cache
@login_required
def crear_funcionario(request):
    usuario_actual = request.user
    responsable = encargado_bienes.objects.filter(id_worker=usuario_actual).first()
    
    if request.method == 'POST':
        # Si no es admin, forzar el valor del área en POST data
        if not request.user.is_superuser and responsable:
            # Crear una copia mutable de POST
            post_data = request.POST.copy()
            post_data['area'] = responsable.area
            formulario = EmpleadoForm(post_data)
        else:
            formulario = EmpleadoForm(request.POST)
        
        if formulario.is_valid():
            empleado = formulario.save(commit=False)
            empleado.save()
            messages.success(request, 'Empleado registrado exitosamente')
            return redirect('funcionarios')
        else:
            context = {
                'form': formulario,
                'is_admin': request.user.is_superuser,
                'responsable': responsable,
            }
            return render(request, 'administracion/new_func.html', context)
    
    else:
        context = {
            'form': EmpleadoForm(),
            'is_admin': request.user.is_superuser,
            'responsable': responsable,
        }
        return render(request, 'administracion/new_func.html', context)
    
def profile(request, id):
    hoy = date.today()


    employee = get_object_or_404(Empleado, id=id)
    fecha_nacimiento = employee.birthday
    edad = hoy.year - fecha_nacimiento.year - ((hoy.month, hoy.day) < (fecha_nacimiento.month, fecha_nacimiento.day))

    context = {
        'employee': employee,
        'edad': edad,
    }
    
    return render(request, 'profile.html', context)

def editar_funcionario(request, id):
    empleado = get_object_or_404(Empleado, id=id)
    usuario_actual = request.user
    responsable = encargado_bienes.objects.filter(id_worker=usuario_actual).first()
    
    if request.method == 'POST':
        formulario = EmpleadoForm(request.POST, instance=empleado)

        if not request.user.is_superuser and responsable:
            # Crear una copia mutable de POST
            post_data = request.POST.copy()
            post_data['area'] = responsable.area
            formulario = EmpleadoForm(post_data)
        else:
            formulario = EmpleadoForm(request.POST)

        if formulario.is_valid():
            formulario.save()
            messages.success(request, 'Empleado actualizado exitosamente')
            return redirect('funcionarios')
    else:
        formulario = EmpleadoForm(instance=empleado)
    
    context = {
        'form': formulario,
        'empleado': empleado,
        'is_admin': request.user.is_superuser,
        'responsable': responsable,
    }
    return render(request, 'administracion/edit_func.html', context)

def eliminar_funcionario(request, id):

    empleado = Empleado.objects.get(id=id)
    empleado.delete()
    messages.success(request, 'Empleado eliminado exitosamente')
    return redirect('funcionarios')

