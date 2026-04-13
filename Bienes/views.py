from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .utils import get_empleados_por_area_usuario, get_user_role
from django.http import JsonResponse
from django.contrib import messages
from django.urls import reverse
from .models import *
from .forms import *

def bienes(request):

    return render(request, 'bienes/bienes.html')

def lista_bienes(request):

    entity = Bienes.objects.all()
    data = [
        {
            'bm': c.bm,
            'descripcion': c.description,
            'partes': c.part,
            'condicion': c.condition,
            'id': c.id,
            } for c in entity
        ]
    return JsonResponse({'data':data}, safe=False)

@login_required
def add_bien(request, id):

    empleados = get_empleados_por_area_usuario(request.user)
    bien_fisico = get_object_or_404(Bienes, id=id)
    responsable = encargado_bienes.objects.filter(id_worker=request.user).first()
    
    is_juridico = False

    if responsable and responsable.area.name == "Juridico":
        is_juridico = True

    if request.user.is_superuser:
        empleados = Empleado.objects.all()
    else:
        responsable = encargado_bienes.objects.filter(id_worker=request.user).first()
        if responsable:
            empleados = Empleado.objects.filter(area=responsable.area)  # Solo su área
        else:
            empleados = Empleado.objects.none()
    
    if request.method == 'POST':
        print(f"Datos POST recibidos: {request.POST}")

        form = addBien_form(request.POST)

        print(f"Formulario es válido: {form.is_valid()}")
        if not form.is_valid():
            print(f"Errores del formulario: {form.errors}")
            
        condition_bien = request.POST.get('condition') 
            
        print("="*50)
        print("Datos POST recibidos:", request.POST)
        print("Condición de bien recibida:", condition_bien)
        print("="*50)
            
        if form.is_valid():
            print("Formulario válido, procesando...")
            
            if bien_fisico.part and '/' in bien_fisico.part:
                try:
                    actual, total = map(int, bien_fisico.part.split('/'))

                    if condition_bien == 'Enajenado' or condition_bien == 'Comodato':

                        bien_fisico.part = f"{total}/{total}"
                        bien_fisico.condition = 'Completo'
                        bien_fisico.save()
                        print(f"Bien físico marcado como Completo por condición {condition_bien}")
                    
                    elif actual < total:
                        actual += 1
                        nuevo_part = f"{actual}/{total}"
                        
                        if actual == total:
                            bien_fisico.condition = 'Completo'
                            print("Bien físico marcado como Completo")
                        else:
                            bien_fisico.condition = 'Incompleto'
                            print("Bien físico marcado como Incompleto")
                        
                        bien_fisico.part = nuevo_part
                        bien_fisico.save()
                        print(f"Part actualizado: {nuevo_part}")
                        
                except ValueError as e:
                    print(f"Error al procesar part: {e}")
            
            try:
                form.instance.bm_worker = bien_fisico.bm
                form.instance.id_bien = bien_fisico

                if not request.user.is_superuser and responsable:
                    form.instance.area = responsable.area
                    print(f"Asignando área automática: {responsable.area}")
                
                if condition_bien:
                    form.instance.condition = condition_bien
                    print(f"Asignando condición: {condition_bien} a la instancia")
                
                asignacion = form.save()
                messages.success(request, "Bien guardado correctamente")
                
                print(f"Asignación guardada exitosamente con ID: {asignacion.id}")
                print(f"Condición guardada: {asignacion.condition}")
                print(f"Condición en BD: {Bienes_persona.objects.get(id=asignacion.id).condition}")
                print(f"Área guardada: {asignacion.area}")
                
                return redirect('bienes')
                
            except Exception as e:
                print(f"Error al guardar asignación: {e}")
                # Aquí deberías retornar algo o manejar el error
                return render(request, 'bienes/add_bien_det.html', {
                    'form': form,
                    'bien': bien_fisico,
                    'form_errors': form.errors,
                    'empleados': empleados,
                    'error': str(e)
                })
        else:
            # Formulario no válido
            context = {
                'form': form,
                'bien': bien_fisico, 
                'form_errors': form.errors,
                'responsable': responsable,
                'empleados': empleados,
                'is_juridico': is_juridico,
                'is_admin': request.user.is_superuser,
            }
            return render(request, 'bienes/add_bien_det.html', context)
    
    else:
        # Método GET (carga inicial)

        initial_data = {}
        if not request.user.is_superuser and responsable:
            initial_data['area'] = responsable.area

        form = addBien_form()
        context = {
            'form': form,
            'bien': bien_fisico, 
            'responsable': responsable,
            'is_admin': request.user.is_superuser,
            'is_juridico': is_juridico,
            'empleados': empleados,
        }
        return render(request, 'bienes/add_bien_det.html', context)

def bienes_detallado(request, id):

    bienes_fisico = get_object_or_404(Bienes, id=id)
    bienes_asignados = Bienes_persona.objects.filter(id_bien=id)

    context = {
        'bien': bienes_fisico,
        'ajax_url': reverse('lista_bienes_det') 
    }
   
    return render(request, 'bienes/bienes_det.html', context)

def lista_bienes_det(request):
    print("=== DEBUG ===")
    print("GET params:", request.GET)
    
    bien_id = request.GET.get('bien_id')
    print("bien_id recibido:", bien_id)
    
    if not bien_id:
        return JsonResponse({'error': 'Se requiere bien_id'}, status=400)
    
    try:
        # Filtra los registros
        entity = Bienes_persona.objects.filter(id_bien=bien_id)
        print("Registros encontrados:", entity.count())
        
        data = []
        for c in entity:
            print(f"Procesando: {c.id} - {c.description}")
            data.append({
                'descripcion': c.description or '',
                'area': str(c.area.name) if c.area else '',  # Ajusta según tu modelo
                'funcionario': str(c.id_worker.names) if c.id_worker else '',  # Ajusta según tu modelo
                'condicion': c.condition.capitalize() if c.condition else '',
                'observacion': c.observation or '',
                'id': c.id,
            })
        
        print("Data a enviar:", data)
        return JsonResponse({'data': data}, safe=False)
        
    except Exception as e:
        print("ERROR:", str(e))
        import traceback
        traceback.print_exc()
        return JsonResponse({'error': str(e)}, status=500)

def editar_asignacion(request, id):
    asignacion = get_object_or_404(Bienes_persona, id=id)
    
    if request.method == 'POST':
        form = addBien_form(request.POST, instance=asignacion)
        
        if form.is_valid():
            form.save()
            messages.success(request, "Asignación actualizada correctamente")
            return redirect('bienes')
        else:
            messages.error(request, "Error al actualizar la asignación")
    else:
        form = addBien_form(instance=asignacion)
    
    context = {
        'form': form,
        'asignacion': asignacion,
    }
    
    return render(request, 'bienes/edit_bien_det.html', context)
    
def borrar_asignacion(request, id):
    try:
        # Busca la asignación específica por su ID
        asignacion = get_object_or_404(Bienes_persona, id=id)
        
        # Obtén el bien físico relacionado
        bien_fisico = asignacion.id_bien  # O asignacion.id_bien según tu modelo
        
        # Guarda el part actual para debug
        print(f"Part antes de eliminar: {bien_fisico.part}")
        
        # Elimina la asignación
        asignacion.delete()
        
        # Actualiza el contador en bienes físicos
        if bien_fisico.part and '/' in bien_fisico.part:
            try:
                actual, total = map(int, bien_fisico.part.split('/'))
                
                # Solo resta si hay asignaciones actuales (actual > 0)
                if actual > 0:
                    actual -= 1
                    nuevo_part = f"{actual}/{total}"
                    bien_fisico.part = nuevo_part
                    
                    # Actualiza la condición basada en el nuevo valor
                    if actual == total:
                        bien_fisico.condition = 'Completo'
                    else:
                        bien_fisico.condition = 'Incompleto'
                    
                    # Si no hay más asignaciones, la condición podría ser 'Completo' pero no hay partes asignadas
                    if actual == 0:
                        bien_fisico.condition = 'Completo'
                    
                    bien_fisico.save()
                    print(f"Part actualizado: {nuevo_part}, Condition: {bien_fisico.condition}")
                    
                    messages.success(request, f"Asignación eliminada correctamente. Part actual: {actual}/{total}")
                else:
                    messages.warning(request, "No había asignaciones para descontar")
                    
            except ValueError as e:
                print(f"Error al procesar part: {e}")
                messages.error(request, "Error al actualizar el contador")
        else:
            # Si no tiene formato part, solo elimina la asignación
            messages.success(request, "Asignación eliminada correctamente")
        
        return redirect('bienes')
        
    except Exception as e:
        print(f"Error en borrar_asignacion: {e}")
        messages.error(request, f"Error al eliminar la asignación: {str(e)}")
        return redirect('bienes')

@login_required
def listado_bienes_det(request):
    usuario_actual = request.user
    rol = get_user_role(usuario_actual)
    if rol == 'admin':

        entity = Bienes_persona.objects.all()
        data = [
        {
                'bm': c.bm_worker,
                'descripcion': c.description,
                'area': str(c.area.name) if c.area else '',
                'funcionario': str(c.id_worker.names) if c.id_worker else '',
                'condicion': c.condition.capitalize() if c.condition else '',
                'observacion': c.observation or '',
                'id': c.id,
                } for c in entity
            ]
        return JsonResponse({'data':data}, safe=False)
    
    elif rol[0] == 'encargado_bienes':
        area = rol[1]
        
        entity = Bienes_persona.objects.filter(area=area)
        data = [
        {
                'bm': c.bm_worker,
                'descripcion': c.description,
                'area': str(c.area.name) if c.area else '',
                'funcionario': str(c.id_worker.names) if c.id_worker else '',
                'condicion': c.condition.capitalize() if c.condition else '',
                'observacion': c.observation or '',
                'id': c.id,
                } for c in entity
            ]
        return JsonResponse({'data':data}, safe=False)
    
    else:

        entity = Bienes_persona.objects.filter(id_worker__user=usuario_actual)
        data = [
        {
                'bm': c.bm_worker,
                'descripcion': c.description,
                'area': str(c.area.name) if c.area else '',
                'funcionario': str(c.id_worker.names) if c.id_worker else '',
                'condicion': c.condition.capitalize() if c.condition else '',
                'observacion': c.observation or '',
                'id': c.id,
                } for c in entity
            ]
        return JsonResponse({'data':data}, safe=False)

def bienes_det(request):
    return render(request, 'bienes/lista_bien_det.html')

def bienes_pd(request):
    return render(request, 'bienes/bienes_pd.html')

def lista_bienes_pd(request):

    usuario_actual = request.user
    rol = get_user_role(usuario_actual)

    if rol == 'admin':

        entity = otros_bienes_pd.objects.filter(status=True)
        data = [
            {
                'bm': c.bm,
                'descripcion': c.description,
                'area': str(c.area.name) if c.area else '',
                'funcionario': str(c.id_worker.names) if c.id_worker else '',
                'condicion': c.condition,
                'observacion': c.observation or '',
                'id': c.id,
                } for c in entity
            ]
        return JsonResponse({'data':data}, safe=False)
    
    elif rol[0] == 'encargado_bienes':
        area = rol[1]
        
        entity = otros_bienes_pd.objects.filter(area=area, status=True)
        data = [
            {
                'bm': c.bm,
                'descripcion': c.description,
                'area': str(c.area.name) if c.area else '',
                'funcionario': str(c.id_worker.names) if c.id_worker else '',
                'condicion': c.condition,
                'observacion': c.observation or '',
                'id': c.id,
                } for c in entity
            ]
        return JsonResponse({'data':data}, safe=False)
    
    else:

        entity = otros_bienes_pd.objects.filter(id_worker__user=usuario_actual, status=True)
        data = [
            {
                'bm': c.bm,
                'descripcion': c.description,
                'area': str(c.area.name) if c.area else '',
                'funcionario': str(c.id_worker.names) if c.id_worker else '',
                'observacion': c.observation or '',
                'condicion': c.condition,
                'id': c.id,
                } for c in entity
            ]
        return JsonResponse({'data':data}, safe=False)
    
def add_bien_pd(request):

    responsable = encargado_bienes.objects.filter(id_worker=request.user).first()

    if request.user.is_superuser:
        empleados = Empleado.objects.all()
    else:
        responsable = encargado_bienes.objects.filter(id_worker=request.user).first()
        if responsable:
            empleados = Empleado.objects.filter(area=responsable.area)  # Solo su área
        else:
            empleados = Empleado.objects.none()

    if request.method == 'POST':
        form = OtroBienPd_form(request.POST)
        condition_bien = request.POST.get('condition') 

        if form.is_valid():

            if not request.user.is_superuser and responsable:
                    form.instance.area = responsable.area
                    print(f"Asignando área automática: {responsable.area}")
            form.instance.condition = condition_bien
            form.save()
            messages.success(request, "Bien guardado correctamente")
            return redirect('bienes_pd')
        else:
            messages.error(request, "Error al guardar el bien")

    context = {
        'responsable': responsable,
        'form': OtroBienPd_form(),
        'is_admin': request.user.is_superuser,
        'empleados': empleados,
    }

    return render(request, 'bienes/add_bien_pd.html', context)

def delete_bien_pd(request, id):
    try:
        bien = get_object_or_404(otros_bienes_pd, id=id)
        bien.delete()
        messages.success(request, "Bien eliminado correctamente")
    except Exception as e:
        print(f"Error al eliminar el bien: {e}")
        messages.error(request, f"Error al eliminar el bien: {str(e)}")
    return redirect('bienes_pd')

def bienes_ci(request):
    return render(request, 'bienes/bienes_ci.html')

def lista_bienes_ci(request):

    usuario_actual = request.user
    rol = get_user_role(usuario_actual)

    if rol == 'admin':

        entity = otros_bienes_ci.objects.filter(status=True)
        data = [
            {
                'bm': c.bm,
                'descripcion': c.description,
                'area': str(c.area.name) if c.area else '',
                'funcionario': str(c.id_worker.names) if c.id_worker else '',
                'condicion': c.condition,
                'observacion': c.observation or '',
                'id': c.id,
                } for c in entity
            ]
        return JsonResponse({'data':data}, safe=False)
    
    elif rol[0] == 'encargado_bienes':
        area = rol[1]
        
        entity = otros_bienes_ci.objects.filter(area=area, status=True)
        data = [
            {
                'bm': c.bm,
                'descripcion': c.description,
                'area': str(c.area.name) if c.area else '',
                'funcionario': str(c.id_worker.names) if c.id_worker else '',
                'condicion': c.condition,
                'observacion': c.observation or '',
                'id': c.id,
                } for c in entity
            ]
        return JsonResponse({'data':data}, safe=False)
    
    else:

        entity = otros_bienes_ci.objects.filter(id_worker__user=usuario_actual, status=True)
        data = [
            {
                'bm': c.bm,
                'descripcion': c.description,
                'area': str(c.area.name) if c.area else '',
                'funcionario': str(c.id_worker.names) if c.id_worker else '',
                'observacion': c.observation or '',
                'condicion': c.condition,
                'id': c.id,
                } for c in entity
            ]
        return JsonResponse({'data':data}, safe=False)
    
def add_bien_ci(request):

    responsable = encargado_bienes.objects.filter(id_worker=request.user).first()

    if request.user.is_superuser:
        empleados = Empleado.objects.all()
    else:
        responsable = encargado_bienes.objects.filter(id_worker=request.user).first()
        if responsable:
            empleados = Empleado.objects.filter(area=responsable.area)  # Solo su área
        else:
            empleados = Empleado.objects.none()

    if request.method == 'POST':
        form = OtroBienCi_form(request.POST)
        condition_bien = request.POST.get('condition') 

        if form.is_valid():

            if not request.user.is_superuser and responsable:
                    form.instance.area = responsable.area
                    print(f"Asignando área automática: {responsable.area}")
            form.instance.condition = condition_bien
            form.save()
            messages.success(request, "Bien guardado correctamente")
            return redirect('bienes_ci')
        else:
            messages.error(request, "Error al guardar el bien")

    context = {
        'responsable': responsable,
        'form': OtroBienCi_form(),
        'is_admin': request.user.is_superuser,
        'empleados': empleados,
    }

    return render(request, 'bienes/add_bien_ci.html', context)

def delete_bien_ci(request, id):
    try:
        bien = get_object_or_404(otros_bienes_ci, id=id)
        bien.delete()
        messages.success(request, "Bien eliminado correctamente")
    except Exception as e:
        print(f"Error al eliminar el bien: {e}")
        messages.error(request, f"Error al eliminar el bien: {str(e)}")
    return redirect('bienes_ci')


