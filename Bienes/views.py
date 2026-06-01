from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from django.http import JsonResponse, FileResponse, HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from .utils import get_empleados_por_area_usuario, get_user_role
from django.contrib.auth.decorators import login_required
from django.views.generic.base import TemplateView
from reportlab.lib.utils import ImageReader
from reportlab.lib.colors import HexColor
from reportlab.platypus import Paragraph
from reportlab.lib.pagesizes import A4, legal, landscape
from reportlab.lib.units import cm, mm
from reportlab.pdfgen import canvas
from django.contrib import messages
from datetime import date, datetime
from reportlab.lib import colors
from django.urls import reverse
from openpyxl import workbook
from turtle import pd
import xlwt
from .models import *
from .forms import *
import io
import os

def bienes(request):

    return render(request, 'bienes/bienes.html')

def lista_bienes(request):

    entity = Bienes.objects.filter(activo=True)  # Solo bienes activos
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

#------------- Formatos PDF -------------#

def etiquetas_bm_pdf(request):
    responsable = encargado_bienes.objects.filter(id_worker=request.user).first()
    
    if not responsable:
        buffer = io.BytesIO()
        p = canvas.Canvas(buffer, pagesize=A4)
        p.drawString(100, 750, "No se encontraron bienes asignados")
        p.showPage()
        p.save()
        buffer.seek(0)
        return FileResponse(buffer, as_attachment=True, filename='error.pdf')
    
    area = responsable.area.name if responsable.area else "Área Desconocida"
    bienes_asignados = Bienes_persona.objects.filter(area=responsable.area)
    
    # Diccionario de colores por área
    colores_areas = {
        "Gerencia de Administración": colors.HexColor('#FF930F'),
        "Gerencia de Fiscalizacion": colors.HexColor('#EBE412'),
        "Gerencia de Publicidad": colors.HexColor('#01420D'),
        "División de Informática": colors.HexColor('#7D807D'),
        "Div. Calidad de Gest": colors.HexColor('#2B5EED'),
        "Gerencia de Licores": colors.HexColor('#FF0000'),
        "Gerencia General": colors.HexColor('#FFFFFF'),
        "Gerencia de Inmuebles": colors.HexColor('#FF00E5'),
        "Gerencia Juridica": colors.HexColor('#7F14A6'),
        "GADT": colors.HexColor('#06D6D6'),
        "Gerencia de Recaudación": colors.HexColor('#09FF00'),
        "Departamento de Apostilla": colors.HexColor('#55855C'),
        "Gerencia de Prensa": colors.HexColor('#6A7507'),
        "Deposito": colors.HexColor('#5C0902'),
    }
    
    color_area = colores_areas.get(area, colors.HexColor('#CCCCCC'))
    
    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=A4)
    
    # Configuración de la página
    ancho_pagina, alto_pagina = A4
    margen_izquierdo = 1 * cm
    margen_superior = alto_pagina - 1.5 * cm
    margen_derecho = ancho_pagina - 1 * cm
    
    ancho_etiqueta = (margen_derecho - margen_izquierdo) / 3 - 0.3 * cm
    alto_etiqueta = 2.5 * cm  # Reducí la altura porque hay menos información
    separacion_horizontal = 0.3 * cm
    separacion_vertical = 0.4 * cm
    
    contador = 0
    pagina_actual = 1
    logo = ImageReader('static/image/semat_logo_bn.png')
    
    
    def dibujar_etiqueta(p, x, y, bien, color_fondo, area_nombre):
        p.saveState()
        
        # Dibujar rectángulo de fondo
        p.setFillColor(color_fondo)
        p.setStrokeColor(colors.black)
        p.setLineWidth(0.5)
        p.rect(x, y, ancho_etiqueta, alto_etiqueta, fill=1, stroke=1)
        
        # Calcular contraste para el texto
        brillo = (color_fondo.red * 0.299 + color_fondo.green * 0.587 + color_fondo.blue * 0.114)
        if brillo > 0.7:
            color_texto = colors.black
        else:
            color_texto = colors.white
        
        p.setFillColor(color_texto)
        
        # Área (solo el nombre del área del encargado)
        p.setFont("Helvetica-Bold", 10)
        p.drawString(x + 4, y + alto_etiqueta - 10, f"{area_nombre.upper()}")
        
        # Línea separadora
        p.setStrokeColor(color_texto)
        p.line(x + 5, y + alto_etiqueta - 15, x + ancho_etiqueta - 5, y + alto_etiqueta - 15)
        
        # Número del bien (BM)
        p.setFont("Helvetica-Bold", 8)
        p.drawString(x + 5, y + alto_etiqueta - 68, f"BM: {bien.bm_worker}")
        
        # Responsable del bien (nombre del empleado de la tabla Empleado)
        p.setFont("Helvetica-Bold", 8)
        nombre_empleado = bien.id_worker.names if bien.id_worker else "No asignado"
        p.drawString(x + 5, y + 47, f"{nombre_empleado}")

        p.setFillAlpha(0.5)
        p.drawImage(logo, x + ancho_etiqueta - 160, y + 12, width=150, height=40, mask='auto')
        
        p.restoreState()
    
    x_actual = margen_izquierdo
    y_actual = margen_superior - alto_etiqueta
    
    for idx, bien in enumerate(bienes_asignados):
        columna = contador % 3
        fila = (contador // 3) % 6
        
        if columna == 0:
            x_actual = margen_izquierdo
        elif columna == 1:
            x_actual = margen_izquierdo + ancho_etiqueta + separacion_horizontal
        else:
            x_actual = margen_izquierdo + (ancho_etiqueta + separacion_horizontal) * 2
        
        y_actual = margen_superior - alto_etiqueta - (fila * (alto_etiqueta + separacion_vertical))
        
        dibujar_etiqueta(p, x_actual, y_actual, bien, color_area, area)
        
        contador += 1
        
        if contador % 18 == 0 and idx < len(bienes_asignados) - 1:
            p.setFont("Helvetica", 8)
            p.setFillColor(colors.grey)
            p.drawString(ancho_pagina - 50, 20, f"Página {pagina_actual}")
            pagina_actual += 1
            p.showPage()
            contador = 0
            p.setFillColor(color_area)
    
    # Agregar número de página en la última página
    p.setFont("Helvetica", 8)
    p.setFillColor(colors.grey)
    p.drawString(ancho_pagina - 50, 20, f"Página {pagina_actual}")
    
    from datetime import datetime
    fecha_actual = datetime.now().strftime("%d/%m/%Y %H:%M")
    p.setFont("Helvetica", 7)
    p.drawString(margen_izquierdo, 20, f"Generado: {fecha_actual} | Área: {area}")
    
    p.showPage()
    p.save()
    
    buffer.seek(0)
    return FileResponse(buffer, as_attachment=True, filename=f'etiquetas_{area}_{fecha_actual.replace("/", "-").replace(" ", "_").replace(":", "-")}.pdf')

def etiquetas_ci_pdf(request):
    responsable = encargado_bienes.objects.filter(id_worker=request.user).first()
    
    if not responsable:
        buffer = io.BytesIO()
        p = canvas.Canvas(buffer, pagesize=A4)
        p.drawString(100, 750, "No se encontraron bienes asignados")
        p.showPage()
        p.save()
        buffer.seek(0)
        return FileResponse(buffer, as_attachment=True, filename='error.pdf')
    
    area = responsable.area.name if responsable.area else "Área Desconocida"
    bienes_asignados = otros_bienes_ci.objects.filter(area=responsable.area)
    
    # Diccionario de colores por área
    colores_areas = {
        "Gerencia de Administración": colors.HexColor('#FF930F'),
        "Gerencia de Fiscalizacion": colors.HexColor('#EBE412'),
        "Gerencia de Publicidad": colors.HexColor('#01420D'),
        "División de Informática": colors.HexColor('#7D807D'),
        "Div. Calidad de Gest": colors.HexColor('#2B5EED'),
        "Gerencia de Licores": colors.HexColor('#FF0000'),
        "Gerencia General": colors.HexColor('#FFFFFF'),
        "Gerencia de Inmuebles": colors.HexColor('#FF00E5'),
        "Gerencia Juridica": colors.HexColor('#7F14A6'),
        "GADT": colors.HexColor('#06D6D6'),
        "Gerencia de Recaudación": colors.HexColor('#09FF00'),
        "Departamento de Apostilla": colors.HexColor('#55855C'),
        "Gerencia de Prensa": colors.HexColor('#6A7507'),
        "Deposito": colors.HexColor('#5C0902'),
    }
    
    color_area = colores_areas.get(area, colors.HexColor('#CCCCCC'))
    
    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=A4)
    
    # Configuración de la página
    ancho_pagina, alto_pagina = A4
    margen_izquierdo = 1 * cm
    margen_superior = alto_pagina - 1.5 * cm
    margen_derecho = ancho_pagina - 1 * cm
    
    ancho_etiqueta = (margen_derecho - margen_izquierdo) / 3 - 0.3 * cm
    alto_etiqueta = 2.5 * cm  # Reducí la altura porque hay menos información
    separacion_horizontal = 0.3 * cm
    separacion_vertical = 0.4 * cm
    
    contador = 0
    pagina_actual = 1
    logo = ImageReader('static/image/semat_logo_bn.png')
    
    def dibujar_etiqueta(p, x, y, bien, color_fondo, area_nombre):
        p.saveState()
        
        # Dibujar rectángulo de fondo
        p.setFillColor(color_fondo)
        p.setStrokeColor(colors.black)
        p.setLineWidth(0.5)
        p.rect(x, y, ancho_etiqueta, alto_etiqueta, fill=1, stroke=1)
        
        # Calcular contraste para el texto
        brillo = (color_fondo.red * 0.299 + color_fondo.green * 0.587 + color_fondo.blue * 0.114)
        if brillo > 0.7:
            color_texto = colors.black
        else:
            color_texto = colors.white
        
        p.setFillColor(color_texto)
        
        # Área (solo el nombre del área del encargado)
        p.setFont("Helvetica-Bold", 10)
        p.drawString(x + 4, y + alto_etiqueta - 10, f"{area_nombre.upper()}")
        
        # Línea separadora
        p.setStrokeColor(color_texto)
        p.line(x + 5, y + alto_etiqueta - 15, x + ancho_etiqueta - 5, y + alto_etiqueta - 15)
        
        # Número del bien (BM)
        p.setFont("Helvetica-Bold", 8)
        p.drawString(x + 5, y + alto_etiqueta - 68, f"{bien.bm}")
        
        # Responsable del bien (nombre del empleado de la tabla Empleado)
        p.setFont("Helvetica-Bold", 8)
        nombre_empleado = bien.id_worker.names if bien.id_worker else "No asignado"
        p.drawString(x + 5, y + 47, f"{nombre_empleado}")

        p.setFillAlpha(0.5)
        p.drawImage(logo, x + ancho_etiqueta - 160, y + 12, width=150, height=40, mask='auto')
        
        p.restoreState()
    
    x_actual = margen_izquierdo
    y_actual = margen_superior - alto_etiqueta
    
    for idx, bien in enumerate(bienes_asignados):
        columna = contador % 3
        fila = (contador // 3) % 6
        
        if columna == 0:
            x_actual = margen_izquierdo
        elif columna == 1:
            x_actual = margen_izquierdo + ancho_etiqueta + separacion_horizontal
        else:
            x_actual = margen_izquierdo + (ancho_etiqueta + separacion_horizontal) * 2
        
        y_actual = margen_superior - alto_etiqueta - (fila * (alto_etiqueta + separacion_vertical))
        
        dibujar_etiqueta(p, x_actual, y_actual, bien, color_area, area)
        
        contador += 1
        
        if contador % 18 == 0 and idx < len(bienes_asignados) - 1:
            p.setFont("Helvetica", 8)
            p.setFillColor(colors.grey)
            p.drawString(ancho_pagina - 50, 20, f"Página {pagina_actual}")
            pagina_actual += 1
            p.showPage()
            contador = 0
            p.setFillColor(color_area)
    
    # Agregar número de página en la última página
    p.setFont("Helvetica", 8)
    p.setFillColor(colors.grey)
    p.drawString(ancho_pagina - 50, 20, f"Página {pagina_actual}")
    
    from datetime import datetime
    fecha_actual = datetime.now().strftime("%d/%m/%Y %H:%M")
    p.setFont("Helvetica", 7)
    p.drawString(margen_izquierdo, 20, f"Generado: {fecha_actual} | Área: {area}")
    
    p.showPage()
    p.save()
    
    buffer.seek(0)
    return FileResponse(buffer, as_attachment=True, filename=f'etiquetas_{area}_{fecha_actual.replace("/", "-").replace(" ", "_").replace(":", "-")}.pdf')

def etiquetas_pd_pdf(request):
    responsable = encargado_bienes.objects.filter(id_worker=request.user).first()
    
    if not responsable:
        buffer = io.BytesIO()
        p = canvas.Canvas(buffer, pagesize=A4)
        p.drawString(100, 750, "No se encontraron bienes asignados")
        p.showPage()
        p.save()
        buffer.seek(0)
        return FileResponse(buffer, as_attachment=True, filename='error.pdf')
    
    area = responsable.area.name if responsable.area else "Área Desconocida"
    bienes_asignados = otros_bienes_pd.objects.filter(area=responsable.area)
    
    # Diccionario de colores por área
    colores_areas = {
        "Gerencia de Administración": colors.HexColor('#FF930F'),
        "Gerencia de Fiscalizacion": colors.HexColor('#EBE412'),
        "Gerencia de Publicidad": colors.HexColor('#01420D'),
        "División de Informática": colors.HexColor('#7D807D'),
        "Div. Calidad de Gest": colors.HexColor('#2B5EED'),
        "Gerencia de Licores": colors.HexColor('#FF0000'),
        "Gerencia General": colors.HexColor('#FFFFFF'),
        "Gerencia de Inmuebles": colors.HexColor('#FF00E5'),
        "Gerencia Juridica": colors.HexColor('#7F14A6'),
        "GADT": colors.HexColor('#06D6D6'),
        "Gerencia de Recaudación": colors.HexColor('#09FF00'),
        "Departamento de Apostilla": colors.HexColor('#55855C'),
        "Gerencia de Prensa": colors.HexColor('#6A7507'),
        "Deposito": colors.HexColor('#5C0902'),
    }
    
    color_area = colores_areas.get(area, colors.HexColor('#CCCCCC'))
    
    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=A4)
    
    # Configuración de la página
    ancho_pagina, alto_pagina = A4
    margen_izquierdo = 1 * cm
    margen_superior = alto_pagina - 1.5 * cm
    margen_derecho = ancho_pagina - 1 * cm
    
    ancho_etiqueta = (margen_derecho - margen_izquierdo) / 3 - 0.3 * cm
    alto_etiqueta = 2.5 * cm  # Reducí la altura porque hay menos información
    separacion_horizontal = 0.3 * cm
    separacion_vertical = 0.4 * cm
    
    contador = 0
    pagina_actual = 1
    logo = ImageReader('static/image/semat_logo_bn.png')
    
    def dibujar_etiqueta(p, x, y, bien, color_fondo, area_nombre):
        p.saveState()
        
        # Dibujar rectángulo de fondo
        p.setFillColor(color_fondo)
        p.setStrokeColor(colors.black)
        p.setLineWidth(0.5)
        p.rect(x, y, ancho_etiqueta, alto_etiqueta, fill=1, stroke=1)
        
        # Calcular contraste para el texto
        brillo = (color_fondo.red * 0.299 + color_fondo.green * 0.587 + color_fondo.blue * 0.114)
        if brillo > 0.7:
            color_texto = colors.black
        else:
            color_texto = colors.white
        
        p.setFillColor(color_texto)
        
        # Área (solo el nombre del área del encargado)
        p.setFont("Helvetica-Bold", 10)
        p.drawString(x + 4, y + alto_etiqueta - 10, f"{area_nombre.upper()}")
        
        # Línea separadora
        p.setStrokeColor(color_texto)
        p.line(x + 5, y + alto_etiqueta - 15, x + ancho_etiqueta - 5, y + alto_etiqueta - 15)
        
        # Número del bien (BM)
        p.setFont("Helvetica-Bold", 8)
        p.drawString(x + 5, y + alto_etiqueta - 68, f"{bien.bm}")
        
        # Responsable del bien (nombre del empleado de la tabla Empleado)
        p.setFont("Helvetica-Bold", 8)
        nombre_empleado = bien.id_worker.names if bien.id_worker else "No asignado"
        p.drawString(x + 5, y + 47, f"{nombre_empleado}")

        p.setFillAlpha(0.5)
        p.drawImage(logo, x + ancho_etiqueta - 160, y + 12, width=150, height=40, mask='auto')
        
        p.restoreState()
    
    x_actual = margen_izquierdo
    y_actual = margen_superior - alto_etiqueta
    
    for idx, bien in enumerate(bienes_asignados):
        columna = contador % 3
        fila = (contador // 3) % 6
        
        if columna == 0:
            x_actual = margen_izquierdo
        elif columna == 1:
            x_actual = margen_izquierdo + ancho_etiqueta + separacion_horizontal
        else:
            x_actual = margen_izquierdo + (ancho_etiqueta + separacion_horizontal) * 2
        
        y_actual = margen_superior - alto_etiqueta - (fila * (alto_etiqueta + separacion_vertical))
        
        dibujar_etiqueta(p, x_actual, y_actual, bien, color_area, area)
        
        contador += 1
        
        if contador % 18 == 0 and idx < len(bienes_asignados) - 1:
            p.setFont("Helvetica", 8)
            p.setFillColor(colors.grey)
            p.drawString(ancho_pagina - 50, 20, f"Página {pagina_actual}")
            pagina_actual += 1
            p.showPage()
            contador = 0
            p.setFillColor(color_area)
    
    # Agregar número de página en la última página
    p.setFont("Helvetica", 8)
    p.setFillColor(colors.grey)
    p.drawString(ancho_pagina - 50, 20, f"Página {pagina_actual}")
    
    from datetime import datetime
    fecha_actual = datetime.now().strftime("%d/%m/%Y %H:%M")
    p.setFont("Helvetica", 7)
    p.drawString(margen_izquierdo, 20, f"Generado: {fecha_actual} | Área: {area}")
    
    p.showPage()
    p.save()
    
    buffer.seek(0)
    return FileResponse(buffer, as_attachment=True, filename=f'etiquetas_{area}_{fecha_actual.replace("/", "-").replace(" ", "_").replace(":", "-")}.pdf')

def rpu_pdf(request):

    my_Style = getSampleStyleSheet()
    my_Style=ParagraphStyle('My Para style',
        fontName='Times-Roman',
        fontSize=12,
        borderWidth=0,
        leading=15,
        alignment = 1,
        stikeGap = 1,
        strikeOffset = 0.25,
        endDots = None,
        borderPadding= 0,
    )

    my_Style2 = getSampleStyleSheet()
    my_Style2=ParagraphStyle('My Para style 2',
        fontName='Times-Roman',
        fontSize=12,
        firstLineIndent = 30,
        rightIndent = 15,
        borderWidth=0,
        leading=17,
        alignment= 4
    )
    
    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=A4)

    logo = ImageReader('static/image/semat_logo.png')
    hoy = date.today()

    hora_actual = datetime.now().strftime("%I:%M:%p")

    # ------------------- ENCABEZADO ------------------- #
    azul_claro = HexColor('#2F86E9FF')

    p.setFillColor(azul_claro)  
    p.rect(35, 700, 530, 100, fill=1)
    p.rect(35, 700, 180, 100, fill=1)
    p.rect(215, 750, 350, 50, fill=1)
    p.drawImage(logo, 40, 710, 170, 82, mask='auto')

    titulo = "<b>BIENES PÚBLICOS </b>"
    subtitulo = "<b>RESPONSABILIDAD DE BIENES </b>"

    pti = Paragraph(titulo, my_Style)
    pti.wrap(410, 350)
    pti.drawOn(p, 180, 770)

    psub = Paragraph(subtitulo, my_Style)
    psub.wrap(410, 350)
    psub.drawOn(p, 180, 720)

    #-------------------- CONTENIDO ------------------- #
    titulo_2 = "<b><u>ACTA DE BIENES</u></b>"

    prf1 = "Siendo las "+ hora_actual +" del día "+ hoy.strftime('%d') +" de "+ hoy.strftime('%B') +" del año "+ hoy.strftime('%Y') +", yo <b>Argenis Cordero</b> portador de la cédula de identidad Nº <b>V-10.779.050</b>, en condición de responsable de bienes declaro; que recibo los Bienes Muebles especificados en inventario de bienes mueble en (BM-1), para ser utilizado en el desempeño de la unidad de trabajo del área de <b>Informática</b>"

    prf2 = "<bullet>&bull;</bullet><b>Primera:</b> He leído, y entendido que, si se demuestra mi negligencia o impericia en el manejo de los Bienes, así como la omisión o retardo en las notificaciones antes mencionadas, podrá generar responsabilidades disciplinarias, administrativas, penales o civiles de acuerdo a las normativas y leyes."

    prf3 = "<bullet>&bull;</bullet><b>Segunda:</b> En el caso de ocasionarse un Hurto o Robo, deberá formular la denuncia ante el cuerpo de Investigaciones Científicas Penales y Criminalísticas (CICPC) y notificar a La unidad de Bienes Municipales, iniciando los procedimientos a que haya lugar."

    

    pti2 = Paragraph(titulo_2, my_Style)
    pti2.wrap(530, 530) 
    pti2.drawOn(p, 35, 640)

    prf = Paragraph(prf1, my_Style2)
    prf.wrap(530, 530)
    prf.drawOn(p, 40, 550)

    prf_2 = Paragraph(prf2, my_Style2)
    prf_2.wrap(475, 470)
    prf_2.drawOn(p, 90, 465)

    prf_3 = Paragraph(prf3, my_Style2)
    prf_3.wrap(475, 470)
    prf_3.drawOn(p, 90, 400)

    p.rect(35, 335, 530, 40, fill=1)
    p.rect(120, 335, 445, 40, fill=1)
    p.rect(205, 335, 360, 40, fill=1)
    p.rect(450, 335, 115, 40, fill=1)

    p.setFont("Times-Roman", 9)
    p.setFillColor(colors.black)  
    p.drawString(40, 350, "CÓDIGO DEL BIEN")
    p.drawString(125, 350, "SERIAL DEL BIEN")
    p.drawString(285, 350, "DESCRIPCIÓN DEL BIEN")
    p.drawString(465, 350, "CONDICIÓN DEL BIEN")

    # Aquí deberías agregar la lógica para listar los bienes y dibujarlos en el PDF
    # Por ejemplo, podrías iterar sobre los bienes asignados a un empleado y dib

    p.showPage()
    p.save()

    #----------- 2DA PÁGINA -----------#

    p.setFillColor(azul_claro)  
    p.rect(35, 700, 530, 100, fill=1)
    p.rect(35, 700, 180, 100, fill=1)
    p.rect(215, 750, 350, 50, fill=1)
    p.drawImage(logo, 40, 710, 170, 82, mask='auto')

    titulo = "<b>BIENES PÚBLICOS </b>"
    subtitulo = "<b>RESPONSABILIDAD DE BIENES </b>"

    pti = Paragraph(titulo, my_Style)
    pti.wrap(410, 350)
    pti.drawOn(p, 180, 770)

    psub = Paragraph(subtitulo, my_Style)
    psub.wrap(410, 350)
    psub.drawOn(p, 180, 720)




    p.showPage()
    p.save()
    
    buffer.seek(0)
    return FileResponse(buffer, as_attachment=True, filename=f'rpu.pdf')



def bm2_pdf(request):
    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=landscape(legal))


    p.setFont("Times-Bold", 12)
    
    p.rect(30, 550, 950, 20)
    p.rect(30, 30, 950, 520)
    p.drawString(35, 555, "RELACION DEL MOVIMIENTO DE BIENES MUEBLES")
    p.drawString(500, 555, "FORMULARIO BM-2")
    p.drawString(800, 555, "HOJA  Nº.    1")
    p.drawString(35, 535, "1. ESTADO: LARA")
    p.drawString(35, 520, "2. DISTRITO:")
    p.drawString(35, 505, "3. MUNICIPIO: IRIBARREN")
    p.drawString(35, 490, "4. DIRECCION O LUGAR: CALLE 25 ENTRE CARRERAS 17 Y 18.")
    p.drawString(35, 475, "5. DEPENDENCIA O UNIDAD PRIMARIA: ")
    p.drawString(35, 460, "6. SERVICIO:")
    p.drawString(35, 445, "7. UNIDAD DE TRABAJO O DEPENDENCIA:")
    p.drawString(35, 430, "8. PERIODO DE LA CUENTA (MES Y AÑO)")

    p.setFont("Times-Roman", 12)

    p.drawString(650, 520, "Formulario Nro. ")

    p.setFont("Times-Bold", 12)
    p.rect(30, 400, 950, 20)
    p.drawString(115, 405, "EN EL MES DE LA CUENTA HA OCURRIDO EL SIGUIENTE MOVIMIENTO EN LOS BIENES A CARGO DE ESTA DEPENDENCIA.")

    p.rect(30, 360, 950, 40)
    p.rect(30, 385, 150, 15)
    p.rect(30, 30, 50, 355)
    p.rect(80, 30, 50, 355)
    p.rect(130, 30, 50, 355)

    p.setFont("Times-Bold", 10)
    p.drawString(60, 390, "CLASIFICACION")
    p.setFont("Times-Bold", 8)
    p.drawString(40, 370, "GRUPO")
    p.drawString(82, 370, "SUBGRUPO")
    p.drawString(136, 370, "SECCION")

    p.rect(180, 30, 60, 370)
    p.rect(240, 30, 60, 370)
    p.rect(300, 30, 60, 370)

    p.drawString(185, 385, "CONCEPTO")
    p.drawString(200, 375, "DE")
    p.drawString(182, 365, "MOVIMIENTO")

    p.drawString(247, 375, "CANTIDAD")

    p.drawString(314, 385, "NUMERO")
    p.drawString(325, 375, "DE")
    p.drawString(310, 365, "IDENTIFIC.")
    

    p.rect(880, 375, 100, 25)
    p.rect(780, 375, 100, 25)
    p.rect(780, 360, 200, 15)

    p.rect(880, 30, 100, 330)
    p.rect(780, 30, 100, 330)

    p.setFont("Times-Bold", 8)
    p.drawString(790, 390, "INCORPORACIONES")
    p.drawString(830, 380, "Bs.")
    p.drawString(882, 390, "DESINCORPORACIONES")
    p.drawString(930, 380, "Bs.")

    p.drawString(820, 365, "CIFRAS CONVENCIONALES")
    
    p.setFont("Times-Bold", 9)
    p.drawString(380, 385, "NOMBRE Y DESCRIPCION DE LOS BIENES REFERENCIA DE LOS COMPROBANTES")
    p.drawString(475, 370, "Y DE LOS PRECIOS UNITARIOS")


    p.setFont("Times-Roman", 8)

    p.line(375, 95, 500, 95)
    p.line(630, 95, 755, 95)

    p.drawString(375, 85, "JEFE DE LA UNIDAD DE TRABAJO")
    p.drawString(640, 85, "ENCARGADO DE  BIENES")
    p.drawString(375, 75, "ING. RONALD GIMENEZ")
    p.drawString(640, 75, "LCDO. BRAIAN SUAREZ")
    p.drawString(375, 65, "C.I. V-10.779.050")
    p.drawString(640, 65, "C.I. V-10.779.051")


    p.setFont("Times-Roman", 10)
    p.drawString(690, 35, "Total General………")


    p.showPage()
    p.save()

    buffer.seek(0)
    return FileResponse(buffer, as_attachment=True, filename=f'bm2.pdf')

def transf_pdf(request):

    my_Style = getSampleStyleSheet()
    my_Style=ParagraphStyle('My Para style',
        fontName='Times-Roman',
        fontSize=12,
        borderWidth=0,
        leading=15,
        alignment = 1,
        stikeGap = 1,
        strikeOffset = 0.25,
        endDots = None,
        borderPadding= 0,
    )

    my_Style2 = getSampleStyleSheet()
    my_Style2=ParagraphStyle('My Para style2',
        fontName='Times-Roman',
        fontSize=18,
        borderWidth=0,
        leading=15,
        alignment = 1,
        stikeGap = 1,
        strikeOffset = 0.25,
        endDots = None,
        borderPadding= 0,
    )

    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=landscape(legal))

    logo = ImageReader('static/image/semat_logo.png')
    logo2 = ImageReader('static/image/semat_logo_bn.png')

    p.drawImage(logo, 80, 500, 170, 82, mask='auto')
    p.drawImage(logo2, 730, 500, 170, 82, mask='auto')

    membrete = '<b>REPÚBLICA BOLIVARIANA DE VENEZUELA <br/> ALCALDÍA DEL MUNICIPIO IRIBARREN <br/> DIRECCIÓN DE ADMINISTRACIÒN Y FINANZAS <br/> COORDINACION DE BIENES MUNICIPALES </b>'

    titulo = "<b>PLANILLA DE TRANSFERENCIA INTERNA DE BIENES</b>"

    p.rect(30, 30, 950, 400)
    p.rect(30, 410, 950, 20)
    p.rect(830, 410, 150, 20)
    p.rect(30, 410, 400, 20)

    #-------------------------------------

    p.rect(30, 370, 950, 40)
    p.rect(30, 370, 400, 40)
    p.rect(430, 370, 400, 40)

    p.rect(30, 390, 300, 20)
    p.rect(330, 370, 100, 40)


    #--------------------------------------

    p.rect(30, 30, 600, 100)
    p.rect(630, 30, 350, 100)
    p.rect(630, 110, 350, 20)
    p.rect(30, 30, 300, 50)
    p.rect(330, 80, 300, 50)

    #-------------------------------------- 

    p.rect(30, 130, 75, 260)
    p.rect(105, 130, 75, 260)
    p.rect(180, 130, 75, 260)
    p.rect(330, 130, 100, 240)

    p.rect(830, 110, 150, 260)
    
    

    p.setFont("Times-Bold", 10)

    p.drawString(35, 420, "(1) DE:")
    p.drawString(435, 420, "(2) PARA:")
    p.drawString(835, 420, "(3) FECHA:")



    p.drawString(160, 395, "CODIGO")
    p.drawString(560, 385, "DESCRIPCION DE LOS BIENES")
    p.drawString(845, 385, "MONTO EN BOLIVARES")
    p.drawString(347, 395, "CODIGO DE")
    p.drawString(340, 385, "IDENTIFICACION")
    

    pti2 = Paragraph(membrete, my_Style)
    pti2.wrap(950, 530) 
    pti2.drawOn(p, 35, 500)

    pti = Paragraph(titulo, my_Style2)
    pti.wrap(950, 530)
    pti.drawOn(p, 35, 460)

    
    p.showPage()
    p.save()

    buffer.seek(0)
    return FileResponse(buffer, as_attachment=True, filename=f'transferencia.pdf')

# --------------- reportes Excel --------------- # 


def reporte_bxa_excel(request):

    responsable = encargado_bienes.objects.filter(id_worker=request.user).first()

    if request.user.is_superuser:
        area = Departamento.objects.all()
    else:
        responsable = encargado_bienes.objects.filter(id_worker=request.user).first()
        if responsable:
            area = Departamento.objects.filter(id = responsable.area)  # Solo su área
       

    context = {
        'responsable': responsable,
        'is_admin': request.user.is_superuser,
        'area': area,
    }

    return render(request, 'reportes/bienes_area.html', context)

class export_bxa_excel(TemplateView):
    
    def get(self, request, *args, **kwargs):
        # CORREGIDO: Obtener los parámetros correctamente
        area_id = request.GET.get('area')  # 'area' no 'area_id'
        tipo = request.GET.get('bienes')   # 'bienes' está bien
        
        # Validar que se recibieron los parámetros
        if not area_id or not tipo:
            return HttpResponse("Faltan parámetros requeridos", status=400)
        
        area = get_object_or_404(Departamento, id=area_id)
        
        # Crear respuesta
        nombre_archivo = f"Lista-bienes-{tipo}-{area.name}.xls"
        response = HttpResponse(content_type='application/ms-excel')
        response['Content-Disposition'] = f'attachment; filename="{nombre_archivo}"'
        
        # Usar xlwt consistentemente (no mezcles con openpyxl)
        wb = xlwt.Workbook(encoding='utf-8')
        ws = wb.add_sheet('Bienes por área')
        
        # Estilos
        header_style = xlwt.XFStyle()
        header_style.font.bold = True
        header_style.pattern.pattern = xlwt.Pattern.SOLID_PATTERN
        header_style.pattern.pattern_fore_colour = 22  # Gris claro
        
        cell_style = xlwt.XFStyle()
        
        # Escribir encabezados
        headers = ['BM', 'Descripción', 'Área', 'Funcionario', 'Condición', 'Observación']
        for col, header in enumerate(headers):
            ws.write(0, col, header, header_style)
        
        # Obtener datos según tipo
        if tipo == 'bm':
            from .models import Bienes_persona  # Ajusta el import
            bienes = Bienes_persona.objects.filter(area=area)
            
        elif tipo == 'ci':
            from .models import otros_bienes_ci  # Ajusta el import
            bienes = otros_bienes_ci.objects.filter(area=area)
            
        elif tipo == 'pd':
            from .models import otros_bienes_pd  # Ajusta el import
            bienes = otros_bienes_pd.objects.filter(area=area)
            
        else:
            return HttpResponse("Tipo de bien no válido", status=400)
        
        # Escribir datos
        row_num = 1
        for bien in bienes:
            ws.write(row_num, 0, getattr(bien, 'bm', getattr(bien, 'bm_worker', '')), cell_style)
            ws.write(row_num, 1, bien.description or '', cell_style)
            ws.write(row_num, 2, bien.area.name if hasattr(bien, 'area') and bien.area else '', cell_style)
            ws.write(row_num, 3, bien.id_worker.names if hasattr(bien, 'id_worker') and bien.id_worker else '', cell_style)
            ws.write(row_num, 4, bien.condition.capitalize() if bien.condition else '', cell_style)
            ws.write(row_num, 5, bien.observation or '', cell_style)
            row_num += 1
        
        # Ajustar ancho de columnas
        for col in range(len(headers)):
            ws.col(col).width = 5000
        
        # Guardar y retornar
        wb.save(response)
        return response

def reporte_bienes_excel(request):

    return render(request, 'reportes/bienes.html')

class export_bienes_excel(TemplateView):

    def get(self, request, *args, **kwargs):
        condicion = request.GET.get('condicion')
        status = request.GET.get('status')

        
        if not condicion or not status:
            return HttpResponse("Faltan parámetros requeridos", status=400)
        
        nombre_archivo = f"Lista-bienes-{condicion}-{status}.xls"
        response = HttpResponse(content_type='application/ms-excel')
        response['Content-Disposition'] = f'attachment; filename="{nombre_archivo}"'
        
        wb = xlwt.Workbook(encoding='utf-8')
        ws = wb.add_sheet('Bienes')
        
        header_style = xlwt.XFStyle()
        header_style.font.bold = True
        header_style.pattern.pattern = xlwt.Pattern.SOLID_PATTERN
        header_style.pattern.pattern_fore_colour = 22
        
        cell_style = xlwt.XFStyle()
        
        headers = ['BM', 'Descripción', 'Status', 'Condición']
        for col, header in enumerate(headers):
            ws.write(0, col, header, header_style)
        
        if condicion == 'Bueno' and status == 'Completo':
            
            bienes = Bienes.objects.filter(condition='Completo', status='Bueno', activo=True)

        elif condicion == 'Dañado' and status == 'Completo':
            
            bienes = Bienes.objects.filter(condition='Completo', status='Dañado', activo=True)

        elif condicion == 'Bueno' and status == 'Incompleto':
            
            bienes = Bienes.objects.filter(condition='Incompleto', status='Bueno', activo=True)

        elif condicion == 'Dañado' and status == 'Incompleto':
            
            bienes = Bienes.objects.filter(condition='Incompleto', status='Dañado', activo=True)

        elif condicion == 'all' and status == 'Incompleto':

            bienes = Bienes.objects.filter(condition='Incompleto', activo=True)

        elif condicion == 'all' and status == 'Completo':

            bienes = Bienes.objects.filter(condition='Completo', activo=True)

        elif condicion == 'Bueno' and status == 'all':

            bienes = Bienes.objects.filter(status='Bueno', activo=True)

        elif condicion == 'Dañado' and status == 'all':

            bienes = Bienes.objects.filter(status='Dañado', activo=True)

        elif condicion == 'all' and status == 'all':

            bienes = Bienes.objects.filter(activo=True)
            
        else:
            return HttpResponse("Error", status=400)
        
        row_num = 1
        for bien in bienes:
            ws.write(row_num, 0, getattr(bien, 'bm', getattr(bien, 'bm_worker', '')), cell_style)
            ws.write(row_num, 1, bien.description or '', cell_style)
            ws.write(row_num, 2, bien.status.capitalize() if bien.status else '', cell_style)
            ws.write(row_num, 3, bien.condition.capitalize() if bien.condition else '', cell_style)
            row_num += 1
        
        for col in range(len(headers)):
            ws.col(col).width = 5000

        wb.save(response)
        return response



def prueba(request):

    return render (request, 'act_econ/tax.html')
