from django.utils.translation import gettext
from django.shortcuts import redirect, render, get_object_or_404
from django.http import JsonResponse, FileResponse
from .models import *
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
import io
from googletrans import Translator 
from Administracion.models import Empleado
from django.contrib import messages
from .forms import *
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from reportlab.platypus import Paragraph
from reportlab.lib.utils import ImageReader
from reportlab.lib.pagesizes import A4, landscape

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


def act_confid(request):
    return render(request, 'home/list_act_conf.html')


def listado_act_confid(request):
    entity = act_confidentiality.objects.all().order_by('-created_at')
    data = [
            {
                'id': c.id,
                'employee': c.employee.names,
                'date': c.date,
                'observations': c.observations,
                } for c in entity
            ]
    return JsonResponse({'data':data}, safe=False)


def act_confid_create(request):

    busq_docuemt = request.GET.get("cedula", None)
    
    try:

        document_emp = Empleado.objects.get(document = busq_docuemt)

    except Empleado.DoesNotExist:

        document_emp = None

    datos = {
        'form': act_confidentiality_form()
    }

    datos_emp = Empleado.objects.filter(document = request.GET.get('cedula')).last()

    if request.method == "POST":

        formulario = act_confidentiality_form(request.POST)
        

        if formulario.is_valid():

            formulario.instance.employee = datos_emp

            
            formulario.save()

            messages.success(request, 'Se ha guardado correctamente')
            return redirect('act_confid')
        
        else:
            datos['form'] = formulario
    
    return render(request, "home/act_confidentiality.html", {'info': document_emp, 'form':act_confidentiality_form()})

def delete_actconf(request, id):

    try:
        acta = get_object_or_404(act_confidentiality, id=id)
        acta.delete()
        messages.success(request, "Acta eliminada correctamente")
    except Exception as e:
        print(f"Error al eliminar el Acta: {e}")
        messages.error(request, f"Error al eliminar el Acta: {str(e)}")
    return redirect('act_confid')

def ActconfiPdf(request, id):

    act = act_confidentiality.objects.get(id=id)

    empleado = act.employee
    datos_empleado = Empleado.objects.get(id=empleado.id)

    nombre = datos_empleado.names
    cedula = datos_empleado.document
    cargo = datos_empleado.position

    date = act.date.strftime("%d/%m/%Y")

    system = act.system


    dia = act.date.strftime("%d")
    mes = act.date.strftime("%B")
    año = act.date.strftime("%Y")

    translator = Translator()

    system_name = ''

    fm = gettext(mes)

    if system == 'sigep-r':

        system_name = 'SIGESP (RENTAS)'

    elif system == 'sigep-a':

        system_name = 'SIGESP (ADMINISTRATIVO)'

    elif system == 'sigat':

        system_name = 'SIGAT'

    elif system == 'sisem':

        system_name = 'SISEM'

    

    

    my_Style = getSampleStyleSheet()
    my_Style=ParagraphStyle('My Para style',
        fontName='Times-Roman',
        firstLineIndent = 30,
        fontSize=12,
        rightIndent = 15,
        borderWidth=0,
        leading=18,
        alignment= 4,
        spaceAfter= 0,
        spaceBefore=0,
        justifyLastLine= 0,
        underlineGap= 0,
        spaceShrinkage= 0.05,
        underlineOffset= -0.125,
        stikeGap = 1,
        strikeOffset = 0.25,
        endDots = None,
        borderPadding= 0,
    )

    my_Style2=ParagraphStyle('My Para style 2',
        fontName='Times-Roman',
        fontSize=12,
        rightIndent = 15,
        borderWidth=0,
        leading=15,
        alignment = 1,
        spaceAfter= 0,
        spaceBefore=0,
        justifyLastLine= 0,
        underlineGap= 0,
        spaceShrinkage= 0.05,
        underlineOffset= -0.125,
        stikeGap = 1,
        strikeOffset = 0.25,
        endDots = None,
        borderPadding= 0,
    )

    my_Style3=ParagraphStyle('My Para style 3',
        fontName='Times-Roman',
        fontSize=10,
        rightIndent = 15,
        borderWidth=0,
        leading=15,
        alignment= 4,
        spaceAfter= 0,
        spaceBefore=0,
        justifyLastLine= 0,
        underlineGap= 0,
        spaceShrinkage= 0.05,
        underlineOffset= -0.125,
        stikeGap = 1,
        strikeOffset = 0.25,
        endDots = None,
        borderPadding= 0,
    )
    
    my_Style4 = getSampleStyleSheet()
    my_Style4=ParagraphStyle('My Para style 4',
        fontName='Times-Roman',
        firstLineIndent = 0,
        fontSize=12,
        rightIndent = 0,
        borderWidth=0,
        leading=18,
        alignment= 4,
        spaceAfter= 0,
        spaceBefore=0,
        justifyLastLine= 0,
        underlineGap= 0,
        spaceShrinkage= 0.05,
        underlineOffset= -0.125,
        stikeGap = 1,
        strikeOffset = 0.25,
        endDots = None,
        borderPadding= 0,
    )

    my_Style5 = getSampleStyleSheet()
    my_Style5=ParagraphStyle('My Para style5',
        fontName='Times-Roman',
        fontSize=12,
        rightIndent = 15,
        borderWidth=0,
        leading=15,
        alignment = 1,
        stikeGap = 1,
        strikeOffset = 0.25,
        endDots = None,
        borderPadding= 0,
    )

    my_Style6 = getSampleStyleSheet()
    my_Style6=ParagraphStyle('My Para style6',
        fontName='Times-Roman',
        fontSize=10,
        rightIndent = 15,
        borderWidth=0,
        leading=15,
        alignment = 1,
        stikeGap = 1,
        strikeOffset = 0.25,
        endDots = None,
        borderPadding= 0,
    )

    buffer = io.BytesIO()

    log = ImageReader('static/image/alcaldia_logo.png')
    logo = ImageReader('static/image/semat_logo.png')

    p = canvas.Canvas(buffer, pagesize=A4)
    p.setFont("Times-Bold", 12)

    p.drawImage(log, 35, 755, 110, 62)
    p.drawImage(logo, 6.2*inch, 755, 110, 62)

    membrete = '<b>República Bolivariana de Venezuela<br/>Estado Lara<br/>Alcaldía Bolivariana del Municipio Iribarren<br/>Servicio  Municipal de Administración Tributaria</b>'

    titulo = '<b>ACTA DE CONFIDENCIALIDAD, NO DIVULGACIÓN Y USO RESPONSABLE DE SISTEMAS DE RECAUDACIÓN TRIBUTARIA</b>'

    prf1 = 'En la ciudad de <b>Barquisimeto</b>, a los <b>'+ str(dia) +'</b> días del mes de <b>'+ fm +'</b> del '+ str(año) +', ante el <b>Servicio Municipal de Administracion Tributaria (SEMAT)</b>, representado en este acto por <b>Ing. Rudy Orellana de Lanza</b>, comparece el ciudadano <b>'+ nombre + '</b>, titular de la Cédula de Identidad N° <b>' + cedula + '</b>, quien desempeña el cargo de <b>' + cargo + '</b>, a los fines de suscribir el presente compromiso de confidencialidad bajo las siguientes cláusulas:'

    p1 = '<b>PRIMERA: OBJETO</b>'

    prf2 = 'El presente documento tiene por objeto garantizar la absoluta reserva, confidencialidad y resguardo de la información contenida en la plataforma de recaudación <b>'+system_name+'</b>, así como establecer las normas de conducta y manejo técnico a las que se obliga el trabajador en el ejercicio de sus funciones.'

    p2 ='<b>SEGUNDA: MARCO LEGAL REFERENCIAL</b>'

    prf3 = 'El trabajador declara conocer que el manejo de la información pública y tributaria se rige por:'

    prf3_1 = '1. <b>Constitución de la República Bolivariana de Venezuela:</b> Protección de datos y honor (Art 60).'

    prf3_2 = '2. <b>Ley de Infogobierno:</b> Uso de tecnologías de información en el Estado.'

    prf3_3 = '3. <b>Ley Especial contra los Delitos Informáticos:</b> Sanciones por acceso indebido, revelación de datos o alteración de sistemas.'

    prf3_4 = '4. <b>Ley contra la Corrupción:</b> Responsabilidad del funcionario público en el manejo de recursos y datos estatales.'

    prf3_5 = '5. <b>Código Orgánico Tributario:</b> Resguardo del Secreto Tributario.'

    p3 = '<b>TERCERA: CONDICIONES MÍNIMAS DE MANEJO</b>'

    prf4 = 'El trabajador se compromete estrictamente a:'

    prf4_1 = '<b>•	Uso Personal de Credenciales:</b> Mantener la clave de acceso y usuario como información personal e intransferible. Queda prohibido ceder, prestar o mostrar credenciales a terceros, incluyendo compañeros de trabajo o superiores.'

    prf4_2 = '<b>•	Integridad de los Datos:</b> No alterar, modificar, insertar o borrar registros de la base de datos sin la debida autorización jerárquica y el respaldo administrativo correspondiente.'

    prf4_3 = '<b>•	Uso Institucional:</b> Utilizar la plataforma exclusivamente para fines relacionados con sus funciones laborales. Queda prohibido el uso de la base de datos para fines personales, políticos o comerciales.'

    prf4_4 = '<b>•	Cierre de Sesión:</b> Asegurar el cierre de la sesión de usuario cada vez que se retire de su puesto de trabajo, para evitar el acceso de terceros no autorizados.'


    pm = Paragraph(membrete, my_Style5)
    pm.wrap(600, 250)
    pm.drawOn(p, 0, 760)

    pt = Paragraph(titulo, my_Style2)
    pt.wrap(400, 250)
    pt.drawOn(p, 100, 710)

    pf1 = Paragraph(prf1, my_Style)
    pf1.wrap(490, 250)
    pf1.drawOn(p, 60, 600)

    pt1 = Paragraph(p1, my_Style)
    pt1.wrap(400, 250)
    pt1.drawOn(p, 30, 570)

    pf2 = Paragraph(prf2, my_Style)
    pf2.wrap(490, 250)
    pf2.drawOn(p, 60, 490)

    pt2 = Paragraph(p2, my_Style)
    pt2.wrap(400, 250)
    pt2.drawOn(p, 30, 460)

    pf3 = Paragraph(prf3, my_Style)
    pf3.wrap(490, 250)
    pf3.drawOn(p, 60, 410)

    pf3_1 = Paragraph(prf3_1, my_Style4)
    pf3_1.wrap(445, 250)
    pf3_1.drawOn(p, 90, 370)

    pf3_2 = Paragraph(prf3_2, my_Style4)
    pf3_2.wrap(445, 250)
    pf3_2.drawOn(p, 90, 350)

    pf3_3 = Paragraph(prf3_3, my_Style4)
    pf3_3.wrap(445, 250)
    pf3_3.drawOn(p, 90, 315)

    pf3_4 = Paragraph(prf3_4, my_Style4)
    pf3_4.wrap(445, 250)
    pf3_4.drawOn(p, 90, 280)

    pf3_5 = Paragraph(prf3_5, my_Style4)
    pf3_5.wrap(445, 250)
    pf3_5.drawOn(p, 90, 260)

    pt3 = Paragraph(p3, my_Style)
    pt3.wrap(400, 250)
    pt3.drawOn(p, 30, 225)

    pf4 = Paragraph(prf4, my_Style)
    pf4.wrap(490, 250)
    pf4.drawOn(p, 45, 195)

    pf4_1 = Paragraph(prf4_1, my_Style4)
    pf4_1.wrap(445, 250)
    pf4_1.drawOn(p, 90, 130)

    pf4_2 = Paragraph(prf4_2, my_Style4)
    pf4_2.wrap(445, 250)
    pf4_2.drawOn(p, 90, 90)

    pf4_3 = Paragraph(prf4_3, my_Style4)
    pf4_3.wrap(445, 250)
    pf4_3.drawOn(p, 90, 30)


    p.showPage()

    # --------------------------------------------------------------------------------

    p.drawImage(log, 35, 755, 110, 62)
    p.drawImage(logo, 6.2*inch, 755, 110, 62)

    pf4_4 = Paragraph(prf4_4, my_Style4)
    pf4_4.wrap(445, 250)
    pf4_4.drawOn(p, 90, 700)

    p4 = '<b>CUARTA: DEFINICIÓN DE INFORMACIÓN CONFIDENCIAL</b>'

    prf5 = 'Se considera información confidencial, y por ende bajo protección:'

    prf5_1 = '1. Datos de identificación y contacto de los contribuyentes.'

    prf5_2 = '2. Montos de ingresos brutos declarados, estados de cuenta y pagos realizados.'

    prf5_3 = '3. Arquitectura del sistema, códigos fuente y protocolos de seguridad de la plataforma.'

    prf5_4 = '4. Estrategias de fiscalización y metas de recaudación no públicas.'

    p5 = '<b>QUINTA: PROHIBICIÓN DE DIVULGACIÓN</b>'

    prf6 = 'El trabajador no podrá reproducir, extraer, fotografiar, ni transmitir por ningún medio (correo personal, WhatsApp, almacenamiento en la nube, etc.) la información contenida en el sistema. Esta obligación de confidencialidad permanecerá vigente incluso después de finalizada la relación laboral o contractual con el ente por un periodo de un (1) año.'

    p6 = '<b>SEXTA: RESPONSABILIDADES Y SANCIONES</b>'

    prf7 = 'El incumplimiento de las obligaciones aquí descritas dará lugar a la aplicación de:'

    prf7_1 = '1. <b>Sanciones Administrativas:</b> Amonestaciones, suspensión o destitución conforme a la Ley del Estatuto de la Función Pública o contrato de trabajo.'

    prf7_2 = '2. <b>Responsabilidad Penal:</b> Notificación inmediata al Ministerio Público por presunta comisión de delitos informáticos (acceso indebido, revelación de información) o delitos contra la fe pública.'

    prf7_3 = '3. <b>Responsabilidad Civil:</b> Reparación de daños y perjuicios causados al ente o a terceros por el manejo indebido de la información.'

    p7 = '<b>SÉPTIMA: CONFORMIDAD</b>'

    prf8 = 'El trabajador declara haber leído y entendido el contenido de esta acta, aceptando voluntariamente las condiciones de manejo y seguridad impuestas para el resguardo de la plataforma de recaudación.'

    prf9 = 'Se firman dos (02) ejemplares de un mismo tenor y a un solo efecto.'

    pt4 = Paragraph(p4, my_Style)
    pt4.wrap(400, 250)
    pt4.drawOn(p, 30, 670)

    pf5 = Paragraph(prf5, my_Style)
    pf5.wrap(490, 250)
    pf5.drawOn(p, 45, 640)

    pf5_1 = Paragraph(prf5_1, my_Style4)
    pf5_1.wrap(445, 250)
    pf5_1.drawOn(p, 90, 615)

    pf5_2 = Paragraph(prf5_2, my_Style4)
    pf5_2.wrap(445, 250)
    pf5_2.drawOn(p, 90, 595)

    pf5_3 = Paragraph(prf5_3, my_Style4)
    pf5_3.wrap(445, 250)
    pf5_3.drawOn(p, 90, 575)

    pf5_4 = Paragraph(prf5_4, my_Style4)
    pf5_4.wrap(445, 250)
    pf5_4.drawOn(p, 90, 555)

    pt5 = Paragraph(p5, my_Style)
    pt5.wrap(400, 250)
    pt5.drawOn(p, 30, 525)

    pf6 = Paragraph(prf6, my_Style)
    pf6.wrap(490, 250)
    pf6.drawOn(p, 60, 445)

    pt6 = Paragraph(p6, my_Style)
    pt6.wrap(400, 250)
    pt6.drawOn(p, 30, 415)

    pf7 = Paragraph(prf7, my_Style)
    pf7.wrap(490, 250)
    pf7.drawOn(p, 45, 385)

    pf7_1 = Paragraph(prf7_1, my_Style4)
    pf7_1.wrap(445, 250)
    pf7_1.drawOn(p, 90, 345)

    pf7_2 = Paragraph(prf7_2, my_Style4)
    pf7_2.wrap(445, 250)
    pf7_2.drawOn(p, 90, 290)

    pf7_3 = Paragraph(prf7_3, my_Style4)
    pf7_3.wrap(445, 250)
    pf7_3.drawOn(p, 90, 255)

    pt7 = Paragraph(p7, my_Style)
    pt7.wrap(400, 250)
    pt7.drawOn(p, 30, 225)

    pf8 = Paragraph(prf8, my_Style)
    pf8.wrap(490, 250)
    pf8.drawOn(p, 60, 165)

    pf9 = Paragraph(prf9, my_Style)
    pf9.wrap(490, 250)
    pf9.drawOn(p, 30, 140)

    pm = Paragraph(membrete, my_Style5)
    pm.wrap(600, 250)
    pm.drawOn(p, 0, 760)


    p.rect(60, 20, 490, 100, fill=0)
    p.rect(60, 20, 250, 100, fill=0)
    p.line(60, 35, 550, 35)
    p.line(60, 50, 550, 50)
    p.line(60, 105, 550, 105)

    p.setFont("Times-Bold", 10)

    p.drawString(65, 40, "Nombre y Apellido: Ing. Rudy Orellana de Lanza")
    p.drawString(65, 25, "Cargo: Gerente General del SEMAT")

    p.drawString(315, 40, "Nombre y Apellido: " + nombre)
    p.drawString(315, 25, "Cedula: " + cedula)

    p.drawString(65, 110, "POR EL ENTE PÚBLICO")
    p.drawString(315, 110, "EL TRABAJADOR / FUNCIONARIO")


    p.setFont("Times-Bold", 8)
    p.drawString(65, 55, "(FIRMA Y SELLO)")
    p.drawString(315, 55, "(FIRMA Y HUELLA DACTILAR)")

   





    p.save()

    buffer.seek(0)
    return FileResponse(buffer, as_attachment=True, filename='act_confid.pdf')