from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse, FileResponse
from reportlab.lib.pagesizes import A4, landscape
from django.utils.translation import gettext
from reportlab.lib.utils import ImageReader
from reportlab.platypus import Paragraph
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from django.contrib import messages
from num2words import num2words
from decimal import Decimal
from home.models import *
from .models import *
from .forms import *
import datetime 
import io
import re


def calcutations(request):
    return render(request, 'inmueble/calcutations.html')

def list_calcutations(request):

    entity = calculations.objects.all()
    data = [
            {
                'sap': c.cod_sap,
                'cast': c.cod_cast,
                'typo': c.typology,
                'date': c.date.strftime('%Y-%m-%d'),
                'total': c.tax + c.surcharges + c.interests + c.penalty,
                'id': c.id,
                } for c in entity
            ]
    return JsonResponse({'data':data}, safe=False)

def add_calcutations(request):

    if request.method == 'POST' and 'imprimir_pdf' in request.POST:
        resultados_por_periodo = request.session.get('resultados_temporales', {})
        cod_sap = request.POST.get('cod_sap', '')
        cod_cast = request.POST.get('cod_cast', '')
        
        if resultados_por_periodo:
            return generar_pdf_impuestos(resultados_por_periodo, cod_sap, cod_cast)

    sector = request.GET.get('sector')
    typo_1 = request.GET.get('typo_1')
    typo_2 = request.GET.get('typo_2')

    m_sector_str = request.GET.get('m_sect', '0')
    m_sector_str = m_sector_str.replace(',', '.')
    m_sector = float(m_sector_str)
    
    m_typo_1_str = request.GET.get('m_typo_1', '0')
    m_typo_1_str = m_typo_1_str.replace(',', '.')
    m_typo_1 = float(m_typo_1_str)
    
    m_typo_2_str = request.GET.get('m_typo_2', '0')
    m_typo_2_str = m_typo_2_str.replace(',', '.')
    m_typo_2 = float(m_typo_2_str)

    periodo = request.GET.get('periodo')
    cod_sap = request.GET.get('cod_sap')
    cod_cast = request.GET.get('cod_cast')
    periodos = request.GET.getlist('periodos')

    data = {
                'typo_1': typo_1,
                'typo_2': typo_2,
                'sector': sector,
                'm_sector': m_sector,
                'm_typo_1': m_typo_1,
                'm_typo_2': m_typo_2
            }
    
    resultados_por_periodo = {}

    for p in periodos:

        if p == '2019':

            resultado = calculo_periodo_2019(data)
            resultados_por_periodo['2019'] = resultado
            print ('estos son los resultado', resultado)

        if p == '2020':

            resultado = calculo_periodo_2020(data)
            resultados_por_periodo['2020'] = resultado
            print ('estos son los resultado', resultado)

        if p == '2021':

            resultado = calculo_periodo_2021(data)
            resultados_por_periodo['2021'] = resultado
            print ('estos son los resultado', resultado)

        if p == '2022':
            resultado = calculo_periodo_2022(data)
            resultados_por_periodo['2022'] = resultado
            print ('estos son los resultado', resultado)

        if p == '2023':
            resultado = calculo_periodo_2023(data)
            resultados_por_periodo['2023'] = resultado
            print ('estos son los resultado', resultado)

        if p == '2024':
            resultado = calculo_periodo_2024(data)
            resultados_por_periodo['2024'] = resultado
            print ('estos son los resultado', resultado)

        if p == '2025':
            resultado = calculo_periodo_2025(data)
            resultados_por_periodo['2025'] = resultado
            print ('estos son los resultado', resultado)

    request.session['resultados_temporales'] = resultados_por_periodo

    
    return render(request, 'inmueble/add_calc.html', {
        'resultados': resultados_por_periodo,
        'cod_sap': cod_sap,
        'cod_cast': cod_cast
    })


def solic_remi_h(request):
    return render(request, 'inmueble/solic_remi.html')

def list_solic_remi(request):

    entity = solic_remi.objects.all()
    data = [
            {
                'nriu': c.nriu,
                'cod_cast': c.cod_cast,
                'name': c.name,
                'document': c.document,
                'direction': c.direction,
                'phone': c.phone,
                'period': c.period,
                'date': c.date,
                'id': c.id,
                } for c in entity
            ]
    return JsonResponse({'data':data}, safe=False)

def add_solic_remi(request):
    if request.method == 'POST':
        form = solic_remi_form(request.POST)
        if form.is_valid():
            solic_remi_instance = form.save(commit=False)
            solic_remi_instance.user = request.user
            solic_remi_instance.save()
            messages.success(request, "Bien guardado correctamente")
            return redirect('solic_remi')
        else:
            messages.error(request, "Error al guardar el bien")
    else:
        form = solic_remi_form()
    return render(request, 'inmueble/add_solic_remi.html', {'form': form})


def edit_solic_remi(request, id):

    remi = get_object_or_404(solic_remi, id = id)

    if request.method == 'POST':

        form = solic_remi_form(request.POST, instance=remi)

        if form.is_valid():
            form.save()
            messages.success(request, "Remision actualizada correctamente")
            return redirect('solic_remi')
        
        else:
            messages.error(request, "Error al actualizar la remision")

    context = {
        'form': solic_remi_form(instance=remi)
    }


    return render(request, 'inmueble/edit_solic_remi.html', context)


# Función para generar el PDF 


def generar_pdf_impuestos(resultados, cod_sap="", cod_cast=""):
    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=A4)
    
    # Título
    p.setFont("Times-Bold", 14)
    p.drawString(150, 800, f"IMPUESTO DE INMUEBLES - CÁLCULO DE PERÍODOS")
    
    # Información de códigos
    p.setFont("Times-Roman", 10)
    cod_sap = cod_sap if cod_sap else "N/A"
    cod_cast = cod_cast if cod_cast else "N/A"
    p.drawString(35, 770, f"Código SAP: {cod_sap}")
    p.drawString(250, 770, f"Código CAST: {cod_cast}")
    
    # Fecha de generación
    from datetime import datetime
    fecha_actual = datetime.now().strftime("%d/%m/%Y %H:%M")
    p.drawString(450, 770, f"Fecha: {fecha_actual}")
    
    # Encabezados de tabla
    p.rect(35, 730, 530, 25)
    p.rect(35, 710, 530, 20)
    p.line(120, 710, 120, 730)
    p.line(220, 710, 220, 730)
    p.line(320, 710, 320, 730)
    p.line(420, 710, 420, 730)
    p.line(500, 710, 500, 730)
    
    p.setFont("Times-Bold", 10)
    p.drawString(45, 716, "PERÍODO")
    p.drawString(130, 716, "IMPUESTO")
    p.drawString(230, 716, "RECARGOS")
    p.drawString(330, 716, "INTERESES")
    p.drawString(430, 716, "MULTA")
    p.drawString(510, 716, "TOTAL")
    
    # Datos
    y_position = 690
    p.setFont("Times-Roman", 9)
    
    for periodo, resultado in resultados.items():
        # Verificar que existan las claves
        tax = resultado.get('tax', 0)
        recar = resultado.get('recar', 0)
        inter = resultado.get('inter', 0)
        mult = resultado.get('mult', 0)
        total = resultado.get('total', 0)
        
        p.drawString(50, y_position, str(periodo))
        p.drawRightString(210, y_position, tax)
        p.drawRightString(310, y_position, recar)
        p.drawRightString(410, y_position, inter)
        p.drawRightString(490, y_position, mult)
        p.drawRightString(555, y_position, total)

        
        y_position -= 20
        
        # Si llegamos al final de la página, crear una nueva
        if y_position < 50:
            p.showPage()
            y_position = 800
            # Re-dibujar encabezados en la nueva página
            p.setFont("Times-Bold", 10)
            p.rect(35, 730, 530, 25)
            p.rect(35, 710, 530, 20)
            p.line(120, 710, 120, 730)
            p.line(220, 710, 220, 730)
            p.line(320, 710, 320, 730)
            p.line(420, 710, 420, 730)
            p.line(500, 710, 500, 730)
            p.drawString(45, 716, "PERÍODO")
            p.drawString(130, 716, "IMPUESTO")
            p.drawString(230, 716, "RECARGOS")
            p.drawString(330, 716, "INTERESES")
            p.drawString(430, 716, "MULTA")
            p.drawString(510, 716, "TOTAL")
            p.setFont("Times-Roman", 9)
            y_position = 690
    
            p.rect(35, y_position - 10, 530, 20)
            p.setFont("Times-Bold", 10)
            p.drawString(45, y_position + 4, "TOTAL A PAGAR")
            #p.drawRightString(555, y_position + 4, total_a_pagar)


    p.showPage()
    p.save()
    
    buffer.seek(0)
    return FileResponse(buffer, as_attachment=True, filename=f'calculo_impuestos_{datetime.now().strftime("%Y%m%d_%H%M%S")}.pdf')


def remision_pdf(request, id):
    # Aquí iría la lógica para generar el PDF de remisión

    datos_remi = get_object_or_404(solic_remi, id=id)

    nriu = datos_remi.nriu
    cod_cast = datos_remi.cod_cast
    name = datos_remi.name
    document = datos_remi.document
    direction = datos_remi.direction
    date = datos_remi.date.strftime('%Y-%m-%d')
    period = datos_remi.period
    period_desc = datos_remi.period_desc
    funcionario = datos_remi.user.username

    user = User.objects.get(username = funcionario)
    nfuncionario = user.first_name

    dia = date.split('-')[2]
    mes = date.split('-')[1]
    ano = date.split('-')[0]

    mes_l = datos_remi.date.strftime('%B')
    fm = gettext(mes_l)

    iniciales = "".join([nfuncionario[0] for nfuncionario in nfuncionario.split()])

    my_Style = getSampleStyleSheet()
    my_Style=ParagraphStyle('My Para style',
        fontName='Times-Roman',
        firstLineIndent = 30,
        fontSize=10,
        rightIndent = 15,
        borderWidth=0,
        leading=14,
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
        fontSize=10,
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
        fontSize=9.5,
        rightIndent = 15,
        borderWidth=0,
        leading=13,
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

    p.setFont("Times-Bold", 11)
    p.drawString(50, 730, 'CIUDADANO(A):')
    p.setFont("Times-Bold", 9.5)
    p.drawString(50, 710, f'{name.upper()}')
    p.drawString(50, 695, f'{direction.upper()}')

    prf1 = 'Se le notifica que de conformidad con los artículos 171 y 172 del Decreto con Rango, Valor y Fuerza de Ley del Código Orgánico Tributario, la ciudadana <b>ING. RUDY VANESSA ORELLANA DE LANZA</b>, titular de la cédula de identidad N° <b>V-18.104.409</b>, en su carácter de Gerente  General  del  Servicio Municipal de Administración Tributaria <b>(SEMAT)</b>, según Resolución N° <b>RRHH-100-2025</b>, de fecha <b>25 de Agosto del 2025</b> y publicada en Gaceta Municipal Ordinaria Nº 593, de fecha 25/08/2025, dictó la Resolución N° <b>RIIU-'+nriu+'-2026</b> de fecha <b>'+dia+' de '+fm+' del '+ano+'</b>, en la cual se <b>Declara LA REMISIÓN PARCIAL DE LOS IMPUESTOS</b>, <b>ACCESORIOS Y MULTAS TRIBUTARIAS</b>, por concepto de impuesto, Accesorios tributarios y Multas respecto del Impuesto sobre Inmuebles Urbanos, a favor del contribuyente <b>'+name.upper()+'</b>. A los efectos legales se anexa el texto íntegro de la Resolución constante de <b>dos (02) folios</b> útiles. Igualmente se hace del conocimiento,en caso de considerar lesionados sus derechos e intereses por la presente Resolución, podrá optar entre interponer alguno de los dos recursos que se señalan a continuación. <b>a) El Recurso Jerárquico</b>, previsto en los artículos 272 y 274 del Decreto Constituyente mediante el cual se dicta el Decreto Constituyente de Reforma Parcial del Decreto con Rango, Valor y Fuerza de Ley del Código Orgánico Tributario según G.O. N° 6.507 Extraordinario de fecha 29/01/2020, el cual será decidido por el ciudadano Alcalde y deberá ser presentado por ante el Servicio Municipal de Administración Tributaria <b>(SEMAT)</b>, enla Gerencia de Asistencia al Contribuyente, ubicada en la Calle 26 entre Carreras 15 y 16, Torre David, Nivel Semi-Sótano, Barquisimeto-Estado Lara, dentro de los <b>Veinticinco (25) días</b> hábiles siguientes a la presente notificación. b) Interponer el Recurso Contencioso Tributario por ante el Tribunal Superior de lo Contencioso Tributario de la Región Centro Occidental, el cual se encuentra situado en el Tercer Piso del Palacio de Justicia (antiguo Edificio Nacional), ubicado en la Carrera 17 entre Calles 24 y 25 de esta ciudad de Barquisimeto conforme a los artículos 203, 272 al 282 el Decreto Constituyente de Reforma Parcial del Decreto con Rango, Valor y Fuerza de Ley del Código Orgánico Tributario según G.O N° 6.507 Extraordinario de fecha 29/01/2020, dentro de los <b>Veinticinco(25) días</b> hábiles siguientes a la notificación. En ambos casos los lapsos se inician con la notificación del presente acto. De igual manera se le informa que podrá <b>ejercer los mencionados recursos de forma subsidiaria</b>, es decir ejerciendo el <b>Recurso Jerárquico</b> arriba referido y señalando de forma expresa en el texto que lo contiene, que en caso que las resultas del mismo conllevasen a una expresa denegación total o parcial, o denegación tácita, usted tiene la intención de ejercer el Recurso ContenciosoTributario, todo ello a tenor de lo dispuesto en el artículo 286 parágrafo primero del Decreto Constituyente mediante el cual se dicta el Decreto Constituyente de Reforma Parcial del Decreto con Rango, Valor y Fuerza de Ley del Código Orgánico Tributario según G.O N° 6.507 Extraordinario de fecha 29/01/2020'

    prf2 = '<b>ING. RUDY ORELLANA DE LANZA<br/>GERENTE GENERAL DEL SEMAT<br/>Resoluciòn Nº RRHH-100-2025 de fecha 25/08/2025<br/>Publicado en Gaceta Municipal Ordinaria Nº 593 de fecha 25/08/2025<br/>DATOS DE NOTIFICACION</b>'
    p.drawString(50, 60, 'RVOL/'+iniciales)

    prf3 = '<b>NOMBRES Y APELLIDOS:________________________________________________________________________<br/>CEDULA DE IDENTIDAD Nº:_______________________________________________________________________<br/>FECHA Y HORA:________________________________  TELF/CEL:____________________________________<br/>FIRMA:_____________________ CARGO O CARÁCTER  CON EL QUE ACTUA: _________________________<br/>CORREO ELECTRONICO:__________________________________________________________________________<br/>NOTA: Deberá ser firmada por el Representante Legal de la empresa.</b>'

    pm = Paragraph(membrete, my_Style5)
    pm.wrap(600, 250)
    pm.drawOn(p, 0, 760)

    p1 = Paragraph(prf1, my_Style)
    p1.wrap(520, 575)
    p1.drawOn(p, 50, 295)

    p2 = Paragraph(prf2, my_Style2)
    p2.wrap(520, 200)
    p2.drawOn(p, 50, 170)

    p3 = Paragraph(prf3, my_Style3)
    p3.wrap(520, 400)
    p3.drawOn(p, 50, 72)

    p.showPage()

    #--------------------- SEGUNDA PÁGINA ---------------------

    p.drawImage(log, 35, 755, 110, 62)
    p.drawImage(logo, 6.2*inch, 755, 110, 62)

    resol = '<b>RESOLUCIÓN Nº RIIU-'+nriu+'-2026</b>'

    prf4 = 'Quien suscribe, <b>ING. RUDY VANESSA ORELLANA DE LANZA</b>, titular de la cédula de identidad N° <b>V-18.104.409</b>, en su carácter de Gerente General del Servicio Municipal de Administración Tributaria <b>(SEMAT)</b>, según Resolución  N° <b>RRHH-100-2025</b>, de fecha <b>25 de Agosto del 2025</b> y publicada en Gaceta Municipal Ordinaria Nº <b>593</b>, de fecha <b>25/08/2025</b>, en uso de las atribuciones establecidas en los numerales 1, 3, 4, 8 y 15 del Artículo 12 del Decreto N° 40-2016, publicado en la Gaceta Municipal Ordinaria  Nº 118, de fecha 06 de junio de 2016, en concordancia con lo establecido en el artículo 53 del Decreto Constituyente mediante el cual se dicta el Código Orgánico Tributario y de conformidad a lo establecido en la Ordenanza sobre Remisión de los Impuestos Municipales, Accesorios y Multas Tributarias, publicada en Gaceta Municipal Extraordinaria Nº 5203 de fecha 16 de abril de 2026, dicta la siguiente resolución:'

    cons1 = '<b>CONSIDERANDO 1°</b>'

    prf5 = 'Que en fecha '+dia+' de '+fm+' del '+ano+', '

    if document.startswith('J-') or document.startswith('j-'):

        prf5 += 'el contribuyente <b>'+name.upper()+'</b>, inscrito en el Registro de Informacion Fiscal (RIF) <b>'+document+'</b> en su carácter de propietario de un inmueble ubicado en la <b>'+direction+'</b>, con código catastral N° <b>'+cod_cast+'</b>, solicitó por ante la Administración Tributaria Municipal, la remisión del impuesto, accesorios y multas tributarias, causados por la falta de pago del Impuesto Sobre Inmuebles urbanos, correspondiente a la anualidad respecto '

    elif document.startswith('V-') or document.startswith('v-'): 

        prf5 += 'el cuidadano <b>'+name.upper()+'</b>, titular de la cédula de identidas <b>'+document+'</b> en su carácter de propietario de un inmueble ubicado en la <b>'+direction+'</b>, con código catastral N° <b>'+cod_cast+'</b>, solicitó por ante la Administración Tributaria Municipal, la remisión del impuesto, accesorios y multas tributarias, causados por la falta de pago del Impuesto Sobre Inmuebles urbanos, correspondiente a la anualidad respecto'

        if len(period) > 4:

            prf5 += 'a los ejercicios fiscales <b>'+period.lower()+'</b>'

        elif len(period) == 4:

            prf5 += 'al ejercicio fiscal <b>'+period.lower()+'</b>'

    cons2 = '<b>CONSIDERANDO 2°</b>'

    prf6 = 'Que se verificó ante la Gerencia de Recaudación del Servicio Municipal de Administración Tributaria <b>(SEMAT)</b> que efectivamente el contribuyente no ha realizado el pago del impuesto, accesorios tributarios y multas, respecto a los ejercicios fiscales <b>'+period.lower()+'</b>, <b>tal como consta en el estado de cuenta emitido por la Gerencia de recaudación.</b>'

    cons3 = '<b>CONSIDERANDO 3°</b>'

    prf7 = 'Que la contribuyente a los fines de gozar de la remisión establecida en la Ordenanza sobre Remisión de los Impuestos Municipales, Accesorios y Multas Tributarias, publicada en Gaceta Municipal Extraordinaria Nº 5203 de fecha 16 de abril del 2026, deberá hacer efectiva su obligación de pago de la parcialidad restante de la suma adeudada por concepto del mencionado impuesto ante el Servicio Municipal de Administración Tributaria <b>(SEMAT)</b>, determinado conforme a la Ordenanza que regula el impuesto.'

    cons4 = '<b>CONSIDERANDO 4°</b>'

    prf8 = 'Que la Ordenanza sobre Remisión de los Impuestos Municipales, Accesorios y Multas Tributarias, publicada en Gaceta Municipal Extraordinaria Nº 5203 de fecha 16  de abril de 2026  en los artículos 6 y 7, establecen lo siguiente: '

    prf9 = '<i><b>ARTÍCULO 6:</b> La Remisión Tributaria prevista en este Capítulo quedará condicionada a la presentación de las declaraciones y pago de la parcialidad restante de la obligación tributaria insoluta, correspondiente al Impuesto sobre Inmuebles Urbanos causado y omitido. De igual manera, se pagarán los montos por concepto de impuesto, accesorios tributarios (intereses y recargos) y multas conforme a la determinación y liquidación realizada por el Servicio Municipal de Administración Tributaria (SEMAT).</i>'

    prf10 = '<i><b>ARTÍCULO 7:</b> Cumplidos los requisitos y procedimientos establecidos en esta Ordenanza, la remisión será de: <br/><b><br/>1.</b> Un cien por ciento (100%) del monto del impuesto, accesorios tributarios (intereses y recargos) y multas respecto a los ejercicios fiscales 2018, 2019, 2020 y 2021; <br/><b>2.</b> Un ochenta por ciento (80%) respecto a los ejercicios fiscales 2022 y 2023, <br/><b>3.</b> Y un cincuenta por ciento (50%) respecto a los ejercicios fiscales 2024 y 2025.</i>'

    pm = Paragraph(membrete, my_Style5)
    pm.wrap(600, 250)
    pm.drawOn(p, 0, 760)

    pr = Paragraph(resol, my_Style6)
    pr.wrap(600, 250)
    pr.drawOn(p, 0, 720)

    pf4 = Paragraph(prf4, my_Style)
    pf4.wrap(520, 575)
    pf4.drawOn(p, 50, 595)

    pc1 = Paragraph(cons1, my_Style6)
    pc1.wrap(600, 250)
    pc1.drawOn(p, 0, 565)

    pf5 = Paragraph(prf5, my_Style)
    pf5.wrap(520, 575)
    pf5.drawOn(p, 50, 485)

    pc2 = Paragraph(cons2, my_Style6)
    pc2.wrap(600, 250)
    pc2.drawOn(p, 0, 460)

    pf6 = Paragraph(prf6, my_Style)
    pf6.wrap(520, 575)
    pf6.drawOn(p, 50, 410)

    pc3 = Paragraph(cons3, my_Style6)
    pc3.wrap(600, 250)
    pc3.drawOn(p, 0, 375)

    pf7 = Paragraph(prf7, my_Style)
    pf7.wrap(520, 575)
    pf7.drawOn(p, 50, 295)

    pc4 = Paragraph(cons4, my_Style6)
    pc4.wrap(600, 250)
    pc4.drawOn(p, 0, 270)

    pf8 = Paragraph(prf8, my_Style)
    pf8.wrap(520, 575)
    pf8.drawOn(p, 50, 230)

    pf9 = Paragraph(prf9, my_Style4)
    pf9.wrap(520, 575)
    pf9.drawOn(p, 50, 165)

    pf10 = Paragraph(prf10, my_Style4)
    pf10.wrap(520, 575)
    pf10.drawOn(p, 50, 75)

    p.setFont("Times-Bold", 9.5)

    p.drawString(50, 60, 'RVOL/'+iniciales)

    p.showPage()


    #--------------------- TERCERA PÁGINA ---------------------

    p.drawImage(log, 35, 755, 110, 62)
    p.drawImage(logo, 6.2*inch, 755, 110, 62)


    cons5 = '<b>CONSIDERANDO 5°</b>'

    prf11 = 'La falta de pago de los montos por concepto de Impuesto sobre Inmuebles Urbanos determinados por la Administración Tributaria Municipal, <u>implicará la pérdida del beneficio de remisión y la Administración Tributaria Municipal iniciará las acciones administrativas o judiciales tendientes al cobro de la totalidad de la deuda determinada</u>, conforme con lo establecido en la ordenanza eiusdem.'

    cons6 = '<b>CONSIDERANDO 6°</b>'

    prf12 = 'Que de conformidad a lo establecido en el artículo 92, Parágrafo Único de la Ordenanza de Hacienda Pública Municipal: <i>"El levantamiento del Acta prevista en el artículo 88 de esta Ordenanza podrá omitirse en los casos de imposición de sanciones por incumplimiento de deberes formales y en los casos de liquidación de oficio sobre base cierta, cuando tal liquidación se haga exclusivamente con fundamento en los datos de las declaraciones aportadas por los Contribuyentes”</i>'

    cons7 = '<b>CONSIDERANDO 7°</b>'

    prf13 = 'Que en virtud de las razones expuestas, este Despacho:'

    resol = '<b>RESUELVE:</b>'

    

    prf14 = '<b>ARTÍCULO 1:</b> Declarar <b>CON LUGAR</b> la Remisión del impuesto, Accesorios tributarios y Multas respecto del Impuesto sobre Inmuebles Urbanos causado causado y no pagado respecto a los ejercicios fiscales a la contribuyente <b>'+name.upper()+'</b>, '

    if document.startswith('j-') or document.startswith('J-'):

        prf14 += 'inscrito en el Registro de Informacion Fiscal (RIF) <b>'+document+'</b> en su carácter de propietario de un inmueble ubicado en la <b>'+direction+'</b>, con código catastral N° <b>'+cod_cast+'</b>.'

    if document.startswith('V-') or document.startswith('v-'):

        prf14 += 'titular de la cédula de identidas <b>'+document+'</b> en su carácter de propietario de un inmueble ubicado en la <b>'+direction+'</b>, con código catastral N° <b>'+cod_cast+'</b>.'

    if period_desc == '':

        prf15 = '<b>ARTÍCULO 2:</b> Se ordena el pago de la parcialidad restante de la suma adeudada del impuesto, accesorios tributarios y multas, del Impuesto sobre Inmuebles Urbanos causado y no pagado por la contribuyente, respecto a los ejercicios fiscales <b>2022 hasta 2025</b>.'

    else:

        prf15 = '<b>ARTÍCULO 2:</b> Se ordena el pago de la parcialidad restante de la suma adeudada del impuesto, accesorios tributarios y multas, del Impuesto sobre Inmuebles Urbanos causado y no pagado por la contribuyente, respecto a los ejercicios fiscales <b>'+period_desc+'</b>.'

    prf16 = '<b>ARTÍCULO 3:</b> Se ordena la <b><u>REMISIÓN PARCIAL</u></b>, de conformidad con los artículos 1 numeral 2 y 7 de la Ordenanza sobre Remisión de los Impuestos Municipales, Accesorios y Multas Tributarias , publicada en Gaceta Municipal Extraordinaria Nº 5203 de fecha 16  de abril de 2026 , de la siguiente manera: <br/><br/><b>1.</b> Un cien por ciento (100%) del monto del impuesto, accesorios tributarios (intereses y recargos) y multas respecto a los ejercicios fiscales 2019, 2020 y 2021; <br/><b>2.</b> Un ochenta por ciento (80%) respecto a los ejercicios fiscales 2022 y 2023, <br/><b>3.</b> Y un cincuenta por ciento (50%) respecto a los ejercicios fiscales 2024 y 2025.'

    prf17 = 'Dado, firmado y sellado en la Gerencia General del Servicio Municipal de Administración Tributaria <b>(SEMAT)</b> a los '+num2words(str(dia), lang='es')+' <b>('+dia+')</b> días del mes de '+fm+' del '+ano+'.'

    prf18 = '<b>ING. RUDY ORELLANA DE LANZA<br/>GERENTE GENERAL DEL SEMAT<br/>Resoluciòn Nº RRHH-100-2025 de fecha 25/08/2025<br/>Publicado en Gaceta Municipal Ordinaria Nº 593 de fecha 25/08/2025</b>'


    pm = Paragraph(membrete, my_Style5)
    pm.wrap(600, 250)
    pm.drawOn(p, 0, 760)


    pc5 = Paragraph(cons5, my_Style6)
    pc5.wrap(600, 250)
    pc5.drawOn(p, 0, 715)

    pf11 = Paragraph(prf11, my_Style)
    pf11.wrap(520, 575)
    pf11.drawOn(p, 50, 645)

    pc6 = Paragraph(cons6, my_Style6)
    pc6.wrap(600, 250)
    pc6.drawOn(p, 0, 615)

    pf12 = Paragraph(prf12, my_Style)
    pf12.wrap(520, 575)
    pf12.drawOn(p, 50, 545)

    pc7 = Paragraph(cons7, my_Style6)
    pc7.wrap(600, 250)
    pc7.drawOn(p, 0, 510)

    pf13 = Paragraph(prf13, my_Style)
    pf13.wrap(520, 575)
    pf13.drawOn(p, 50, 490)

    pr = Paragraph(resol, my_Style6)
    pr.wrap(600, 250)
    pr.drawOn(p, 0, 455)

    pf14 = Paragraph(prf14, my_Style4)
    pf14.wrap(520, 575)
    pf14.drawOn(p, 50, 385)

    pf15 = Paragraph(prf15, my_Style4)
    pf15.wrap(520, 575)
    pf15.drawOn(p, 50, 348)

    pf16 = Paragraph(prf16, my_Style4)
    pf16.wrap(520, 575)
    pf16.drawOn(p, 50, 235)

    p2 = Paragraph(prf18, my_Style2)
    p2.wrap(520, 200)
    p2.drawOn(p, 50, 75)

    pf17 = Paragraph(prf17, my_Style4)
    pf17.wrap(520, 575)
    pf17.drawOn(p, 50, 200)

    p.setFont("Times-Bold", 9.5)
    p.drawString(40, 30, 'RVOL/'+iniciales)
    p.showPage()

    p.save()

    buffer.seek(0)
    return FileResponse(buffer, as_attachment=True, filename='remision-'+nriu+'.pdf')

#- Funciones de cálculo por período

def calculo_periodo_2025(data):

    v_euro = euro.objects.last()
    valor_moneda = float(v_euro.valor)

    typo_1 = data['typo_1']
    typo_2 = data['typo_2']
    sector_1 = data['sector']
    m_sector = data['m_sector']
    m_typo_1 = data['m_typo_1']
    m_typo_2 = data['m_typo_2']

    val_sector = sector.objects.filter(number=sector_1, period='2025').first()
    val_typo_1 = tipologia.objects.filter(name=typo_1, period='2025').first()
    val_typo_2 = tipologia.objects.filter(name=typo_2, period='2025').first()

    tarfia_sector = (float(val_sector.value) * float(valor_moneda) * m_sector) / 100
    
    tarfia_typo_1 = (float(val_typo_1.value) * float(valor_moneda) * m_typo_1) / 100
    tarfia_typo_2 = (float(val_typo_2.value) * float(valor_moneda) * m_typo_2) / 100
    
    impuesto = float(tarfia_sector + tarfia_typo_1 + tarfia_typo_2)
    recargos = float(impuesto * 0.12)

    inicio_intereses = datetime.date(2025, 4, 1)
    final_intereses = datetime.date.today()

    total_intereses_mensual = Decimal('0')
    fecha_actual = inicio_intereses

    while fecha_actual <= final_intereses:
        # Obtener primer día del mes actual
        primer_dia_mes = fecha_actual.replace(day=1)
        
        # Calcular último día del mes
        if primer_dia_mes.month == 12:
            ultimo_dia_mes = primer_dia_mes.replace(day=31)
        else:
            ultimo_dia_mes = primer_dia_mes.replace(month=primer_dia_mes.month + 1, day=1) - datetime.timedelta(days=1)
        
        
        if ultimo_dia_mes > final_intereses:
            ultimo_dia_mes = final_intereses
        
        # Contar días en este período
        dias_en_periodo = (ultimo_dia_mes - fecha_actual).days + 1
        
        # Obtener tasa del mes
        mes_str = primer_dia_mes.strftime('%m')
        ano_str = str(primer_dia_mes.year)
        tasa_obj = tasas_interes.objects.filter(mes=mes_str, ano=ano_str).first()
        
        if tasa_obj:
            tasa_porcentaje = float(tasa_obj.value)
            
            interes_periodo = (impuesto * tasa_porcentaje / 100 / 360) * dias_en_periodo
            total_intereses_mensual += Decimal(str(interes_periodo))
        
        
        fecha_actual = ultimo_dia_mes + datetime.timedelta(days=1)

    intereses = total_intereses_mensual  # o total_intereses
    
    multa = float(valor_moneda * 10)

    total = float(impuesto) + float(recargos) + float(intereses) + float(multa)

    formatted_impuesto = f"{impuesto:.2f}"
    formatted_recargos = f"{recargos:.2f}"
    formatted_intereses = f"{intereses:.2f}"
    formatted_multa = f"{multa:.2f}"
    formatted_total = f"{total:.2f}"

    if '.' in formatted_impuesto:
        entero, decimal = formatted_impuesto.split('.')
    
    else:
        entero, decimal = formatted_impuesto, '00'

    if '.' in formatted_recargos:
        entero_recargos, decimal_recargos = formatted_recargos.split('.')
    else:
        entero_recargos, decimal_recargos = formatted_recargos, '00'
    
    if '.' in formatted_intereses:
        entero_intereses, decimal_intereses = formatted_intereses.split('.')
    else:
        entero_intereses, decimal_intereses = formatted_intereses, '00'

    if '.' in formatted_multa:
        entero_multa, decimal_multa = formatted_multa.split('.')
    else:
        entero_multa, decimal_multa = formatted_multa, '00'

    if '.' in formatted_total:
        entero_total, decimal_total = formatted_total.split('.')
    else:
        entero_total, decimal_total = formatted_total, '00'

    imp_ent_form = re.sub(r'(\d)(?=(\d{3})+(?!\d))', r'\1.', entero)
    impuesto_formateado = f"{imp_ent_form},{decimal}"
    
    rec_ent_form = re.sub(r'(\d)(?=(\d{3})+(?!\d))', r'\1.', entero_recargos)
    recargos = f"{rec_ent_form},{decimal_recargos}"
        
    int_ent_form = re.sub(r'(\d)(?=(\d{3})+(?!\d))', r'\1.', entero_intereses)
    intereses = f"{int_ent_form},{decimal_intereses}"

    mul_ent_form = re.sub(r'(\d)(?=(\d{3})+(?!\d))', r'\1.', entero_multa)
    multa = f"{mul_ent_form},{decimal_multa}"

    total_ent_form = re.sub(r'(\d)(?=(\d{3})+(?!\d))', r'\1.', entero_total)
    total = f"{total_ent_form},{decimal_total}"

    return {
        'tax': impuesto_formateado,
        'recar': recargos,
        'mult': multa,
        'inter': intereses,
        'total': total
    }

def calculo_periodo_2024(data):

    v_euro = euro.objects.last()
    valor_moneda = float(v_euro.valor)

    typo_1 = data['typo_1']
    typo_2 = data['typo_2']
    sector_1 = data['sector']
    m_sector = data['m_sector']
    m_typo_1 = data['m_typo_1']
    m_typo_2 = data['m_typo_2']

    val_sector = sector.objects.filter(number=sector_1, period='2024').first()
    val_typo_1 = tipologia.objects.filter(name=typo_1, period='2024').first()
    val_typo_2 = tipologia.objects.filter(name=typo_2, period='2024').first()

    tarfia_sector = (float(val_sector.value) * float(valor_moneda) * m_sector) / 100
    
    tarfia_typo_1 = (float(val_typo_1.value) * float(valor_moneda) * m_typo_1) / 100
    tarfia_typo_2 = (float(val_typo_2.value) * float(valor_moneda) * m_typo_2) / 100
    
    impuesto = float(tarfia_sector + tarfia_typo_1 + tarfia_typo_2)
    recargos = float(impuesto * 0.12)

    inicio_intereses = datetime.date(2024, 4, 1)
    final_intereses = datetime.date.today()

    total_intereses_mensual = Decimal('0')
    fecha_actual = inicio_intereses

    while fecha_actual <= final_intereses:
        # Obtener primer día del mes actual
        primer_dia_mes = fecha_actual.replace(day=1)
        
        # Calcular último día del mes
        if primer_dia_mes.month == 12:
            ultimo_dia_mes = primer_dia_mes.replace(day=31)
        else:
            ultimo_dia_mes = primer_dia_mes.replace(month=primer_dia_mes.month + 1, day=1) - datetime.timedelta(days=1)
        
        
        if ultimo_dia_mes > final_intereses:
            ultimo_dia_mes = final_intereses
        
        # Contar días en este período
        dias_en_periodo = (ultimo_dia_mes - fecha_actual).days + 1
        
        # Obtener tasa del mes
        mes_str = primer_dia_mes.strftime('%m')
        ano_str = str(primer_dia_mes.year)
        tasa_obj = tasas_interes.objects.filter(mes=mes_str, ano=ano_str).first()
        
        if tasa_obj:
            tasa_porcentaje = float(tasa_obj.value)
            
            interes_periodo = (impuesto * tasa_porcentaje / 100 / 360) * dias_en_periodo
            total_intereses_mensual += Decimal(str(interes_periodo))
        
        
        fecha_actual = ultimo_dia_mes + datetime.timedelta(days=1)

    intereses = total_intereses_mensual  # o total_intereses
    
    multa = float(valor_moneda * 10)

    total = float(impuesto) + float(recargos) + float(intereses) + float(multa)

    formatted_impuesto = f"{impuesto:.2f}"
    formatted_recargos = f"{recargos:.2f}"
    formatted_intereses = f"{intereses:.2f}"
    formatted_multa = f"{multa:.2f}"
    formatted_total = f"{total:.2f}"

    if '.' in formatted_impuesto:
        entero, decimal = formatted_impuesto.split('.')
    
    else:
        entero, decimal = formatted_impuesto, '00'

    if '.' in formatted_recargos:
        entero_recargos, decimal_recargos = formatted_recargos.split('.')
    else:
        entero_recargos, decimal_recargos = formatted_recargos, '00'
    
    if '.' in formatted_intereses:
        entero_intereses, decimal_intereses = formatted_intereses.split('.')
    else:
        entero_intereses, decimal_intereses = formatted_intereses, '00'

    if '.' in formatted_multa:
        entero_multa, decimal_multa = formatted_multa.split('.')
    else:
        entero_multa, decimal_multa = formatted_multa, '00'

    if '.' in formatted_total:
        entero_total, decimal_total = formatted_total.split('.')
    else:
        entero_total, decimal_total = formatted_total, '00'

    imp_ent_form = re.sub(r'(\d)(?=(\d{3})+(?!\d))', r'\1.', entero)
    impuesto_formateado = f"{imp_ent_form},{decimal}"
    
    rec_ent_form = re.sub(r'(\d)(?=(\d{3})+(?!\d))', r'\1.', entero_recargos)
    recargos = f"{rec_ent_form},{decimal_recargos}"
        
    int_ent_form = re.sub(r'(\d)(?=(\d{3})+(?!\d))', r'\1.', entero_intereses)
    intereses = f"{int_ent_form},{decimal_intereses}"

    mul_ent_form = re.sub(r'(\d)(?=(\d{3})+(?!\d))', r'\1.', entero_multa)
    multa = f"{mul_ent_form},{decimal_multa}"

    total_ent_form = re.sub(r'(\d)(?=(\d{3})+(?!\d))', r'\1.', entero_total)
    total = f"{total_ent_form},{decimal_total}"

    return {
        'tax': impuesto_formateado,
        'recar': recargos,
        'mult': multa,
        'inter': intereses,
        'total': total
    }

def calculo_periodo_2023(data):

    v_euro = euro.objects.last()
    valor_moneda = float(v_euro.valor * 60)

    typo_1 = data['typo_1']
    typo_2 = data['typo_2']
    sector_1 = data['sector']
    m_sector = data['m_sector']
    m_typo_1 = data['m_typo_1']
    m_typo_2 = data['m_typo_2']

    val_sector = sector.objects.filter(number=sector_1, period='2023').first()
    val_typo_1 = tipologia.objects.filter(name=typo_1, period='2023').first()
    val_typo_2 = tipologia.objects.filter(name=typo_2, period='2023').first()

    tarfia_sector = (float(val_sector.value) * float(valor_moneda) * m_sector) / 100
    
    tarfia_typo_1 = (float(val_typo_1.value) * float(valor_moneda) * m_typo_1) / 100
    tarfia_typo_2 = (float(val_typo_2.value) * float(valor_moneda) * m_typo_2) / 100
    
    impuesto = float(tarfia_sector + tarfia_typo_1 + tarfia_typo_2)
    recargos = float(impuesto * 0.12)

    inicio_intereses = datetime.date(2023, 4, 1)
    final_intereses = datetime.date.today()

    total_intereses_mensual = Decimal('0')
    fecha_actual = inicio_intereses

    while fecha_actual <= final_intereses:
        # Obtener primer día del mes actual
        primer_dia_mes = fecha_actual.replace(day=1)
        
        # Calcular último día del mes
        if primer_dia_mes.month == 12:
            ultimo_dia_mes = primer_dia_mes.replace(day=31)
        else:
            ultimo_dia_mes = primer_dia_mes.replace(month=primer_dia_mes.month + 1, day=1) - datetime.timedelta(days=1)
        
        
        if ultimo_dia_mes > final_intereses:
            ultimo_dia_mes = final_intereses
        
        # Contar días en este período
        dias_en_periodo = (ultimo_dia_mes - fecha_actual).days + 1
        
        # Obtener tasa del mes
        mes_str = primer_dia_mes.strftime('%m')
        ano_str = str(primer_dia_mes.year)
        tasa_obj = tasas_interes.objects.filter(mes=mes_str, ano=ano_str).first()
        
        if tasa_obj:
            tasa_porcentaje = float(tasa_obj.value)
            
            interes_periodo = (impuesto * tasa_porcentaje / 100 / 360) * dias_en_periodo
            total_intereses_mensual += Decimal(str(interes_periodo))
        
        
        fecha_actual = ultimo_dia_mes + datetime.timedelta(days=1)

    intereses = total_intereses_mensual  # o total_intereses
    
    multa = float(valor_moneda * 0.10)
    total = float(impuesto) + float(recargos) + float(intereses) + float(multa)

    formatted_impuesto = f"{impuesto:.2f}"
    formatted_recargos = f"{recargos:.2f}"
    formatted_intereses = f"{intereses:.2f}"
    formatted_multa = f"{multa:.2f}"
    formatted_total = f"{total:.2f}"

    if '.' in formatted_impuesto:
        entero, decimal = formatted_impuesto.split('.')
    
    else:
        entero, decimal = formatted_impuesto, '00'

    if '.' in formatted_recargos:
        entero_recargos, decimal_recargos = formatted_recargos.split('.')
    else:
        entero_recargos, decimal_recargos = formatted_recargos, '00'
    
    if '.' in formatted_intereses:
        entero_intereses, decimal_intereses = formatted_intereses.split('.')
    else:
        entero_intereses, decimal_intereses = formatted_intereses, '00'

    if '.' in formatted_multa:
        entero_multa, decimal_multa = formatted_multa.split('.')
    else:
        entero_multa, decimal_multa = formatted_multa, '00'

    if '.' in formatted_total:
        entero_total, decimal_total = formatted_total.split('.')
    else:
        entero_total, decimal_total = formatted_total, '00'

    imp_ent_form = re.sub(r'(\d)(?=(\d{3})+(?!\d))', r'\1.', entero)
    impuesto_formateado = f"{imp_ent_form},{decimal}"
    
    rec_ent_form = re.sub(r'(\d)(?=(\d{3})+(?!\d))', r'\1.', entero_recargos)
    recargos = f"{rec_ent_form},{decimal_recargos}"
        
    int_ent_form = re.sub(r'(\d)(?=(\d{3})+(?!\d))', r'\1.', entero_intereses)
    intereses = f"{int_ent_form},{decimal_intereses}"

    mul_ent_form = re.sub(r'(\d)(?=(\d{3})+(?!\d))', r'\1.', entero_multa)
    multa = f"{mul_ent_form},{decimal_multa}"

    total_ent_form = re.sub(r'(\d)(?=(\d{3})+(?!\d))', r'\1.', entero_total)
    total = f"{total_ent_form},{decimal_total}"

    return {
        'tax': impuesto_formateado,
        'recar': recargos,
        'mult': multa,
        'inter': intereses,
        'total': total
    }

def calculo_periodo_2022(data):

    v_euro = euro.objects.last()
    valor_moneda = float(v_euro.valor * 60)

    typo_1 = data['typo_1']
    typo_2 = data['typo_2']
    sector_1 = data['sector']
    m_sector = data['m_sector']
    m_typo_1 = data['m_typo_1']
    m_typo_2 = data['m_typo_2']

    val_sector = sector.objects.filter(number=sector_1, period='2022').first()
    val_typo_1 = tipologia.objects.filter(name=typo_1, period='2022').first()
    val_typo_2 = tipologia.objects.filter(name=typo_2, period='2022').first()

    tarfia_sector = (float(val_sector.value) * float(valor_moneda) * m_sector) / 100
    
    tarfia_typo_1 = (float(val_typo_1.value) * float(valor_moneda) * m_typo_1) / 100
    tarfia_typo_2 = (float(val_typo_2.value) * float(valor_moneda) * m_typo_2) / 100
    
    impuesto = float(tarfia_sector + tarfia_typo_1 + tarfia_typo_2)
    recargos = float(impuesto * 0.12)

    inicio_intereses = datetime.date(2022, 4, 1)
    final_intereses = datetime.date.today()

    total_intereses_mensual = Decimal('0')
    fecha_actual = inicio_intereses

    while fecha_actual <= final_intereses:
        # Obtener primer día del mes actual
        primer_dia_mes = fecha_actual.replace(day=1)
        
        # Calcular último día del mes
        if primer_dia_mes.month == 12:
            ultimo_dia_mes = primer_dia_mes.replace(day=31)
        else:
            ultimo_dia_mes = primer_dia_mes.replace(month=primer_dia_mes.month + 1, day=1) - datetime.timedelta(days=1)
        
        
        if ultimo_dia_mes > final_intereses:
            ultimo_dia_mes = final_intereses
        
        # Contar días en este período
        dias_en_periodo = (ultimo_dia_mes - fecha_actual).days + 1
        
        # Obtener tasa del mes
        mes_str = primer_dia_mes.strftime('%m')
        ano_str = str(primer_dia_mes.year)
        tasa_obj = tasas_interes.objects.filter(mes=mes_str, ano=ano_str).first()
        
        if tasa_obj:
            tasa_porcentaje = float(tasa_obj.value)
            
            interes_periodo = (impuesto * tasa_porcentaje / 100 / 360) * dias_en_periodo
            total_intereses_mensual += Decimal(str(interes_periodo))
        
        
        fecha_actual = ultimo_dia_mes + datetime.timedelta(days=1)

    intereses = total_intereses_mensual  # o total_intereses
    
    multa = float(valor_moneda * 0.10)

    total = float(impuesto) + float(recargos) + float(intereses) + float(multa)

    formatted_impuesto = f"{impuesto:.2f}"
    formatted_recargos = f"{recargos:.2f}"
    formatted_intereses = f"{intereses:.2f}"
    formatted_multa = f"{multa:.2f}"
    formatted_total = f"{total:.2f}"

    if '.' in formatted_impuesto:
        entero, decimal = formatted_impuesto.split('.')
    
    else:
        entero, decimal = formatted_impuesto, '00'

    if '.' in formatted_recargos:
        entero_recargos, decimal_recargos = formatted_recargos.split('.')
    else:
        entero_recargos, decimal_recargos = formatted_recargos, '00'
    
    if '.' in formatted_intereses:
        entero_intereses, decimal_intereses = formatted_intereses.split('.')
    else:
        entero_intereses, decimal_intereses = formatted_intereses, '00'

    if '.' in formatted_multa:
        entero_multa, decimal_multa = formatted_multa.split('.')
    else:
        entero_multa, decimal_multa = formatted_multa, '00'

    if '.' in formatted_total:
        entero_total, decimal_total = formatted_total.split('.')
    else:
        entero_total, decimal_total = formatted_total, '00'

    imp_ent_form = re.sub(r'(\d)(?=(\d{3})+(?!\d))', r'\1.', entero)
    impuesto_formateado = f"{imp_ent_form},{decimal}"
    
    rec_ent_form = re.sub(r'(\d)(?=(\d{3})+(?!\d))', r'\1.', entero_recargos)
    recargos = f"{rec_ent_form},{decimal_recargos}"
        
    int_ent_form = re.sub(r'(\d)(?=(\d{3})+(?!\d))', r'\1.', entero_intereses)
    intereses = f"{int_ent_form},{decimal_intereses}"

    mul_ent_form = re.sub(r'(\d)(?=(\d{3})+(?!\d))', r'\1.', entero_multa)
    multa = f"{mul_ent_form},{decimal_multa}"

    total_ent_form = re.sub(r'(\d)(?=(\d{3})+(?!\d))', r'\1.', entero_total)
    total = f"{total_ent_form},{decimal_total}"

    return {
        'tax': impuesto_formateado,
        'recar': recargos,
        'mult': multa,
        'inter': intereses,
        'total': total
    }

def calculo_periodo_2021(data):

    v_euro = euro.objects.last()
    valor_moneda = float(v_euro.valor * 60)

    typo_1 = data['typo_1']
    typo_2 = data['typo_2']
    sector_1 = data['sector']
    m_sector = data['m_sector']
    m_typo_1 = data['m_typo_1']
    m_typo_2 = data['m_typo_2']

    val_sector = sector.objects.filter(number=sector_1, period='2021').first()
    val_typo_1 = tipologia.objects.filter(name=typo_1, period='2021').first()
    val_typo_2 = tipologia.objects.filter(name=typo_2, period='2021').first()

    tarfia_sector = (float(val_sector.value) * float(valor_moneda) * m_sector) / 100
    
    tarfia_typo_1 = (float(val_typo_1.value) * float(valor_moneda) * m_typo_1) / 100
    tarfia_typo_2 = (float(val_typo_2.value) * float(valor_moneda) * m_typo_2) / 100
    
    impuesto = float(tarfia_sector + tarfia_typo_1 + tarfia_typo_2)
    recargos = float(impuesto * 0.12)
    

    inicio_intereses = datetime.date(2021, 4, 1)
    final_intereses = datetime.date.today()

    total_intereses_mensual = Decimal('0')
    fecha_actual = inicio_intereses

    while fecha_actual <= final_intereses:
        # Obtener primer día del mes actual
        primer_dia_mes = fecha_actual.replace(day=1)
        
        # Calcular último día del mes
        if primer_dia_mes.month == 12:
            ultimo_dia_mes = primer_dia_mes.replace(day=31)
        else:
            ultimo_dia_mes = primer_dia_mes.replace(month=primer_dia_mes.month + 1, day=1) - datetime.timedelta(days=1)
        
        
        if ultimo_dia_mes > final_intereses:
            ultimo_dia_mes = final_intereses
        
        # Contar días en este período
        dias_en_periodo = (ultimo_dia_mes - fecha_actual).days + 1
        
        # Obtener tasa del mes
        mes_str = primer_dia_mes.strftime('%m')
        ano_str = str(primer_dia_mes.year)
        tasa_obj = tasas_interes.objects.filter(mes=mes_str, ano=ano_str).first()
        
        if tasa_obj:
            tasa_porcentaje = float(tasa_obj.value)
            
            interes_periodo = (impuesto * tasa_porcentaje / 100 / 360) * dias_en_periodo
            total_intereses_mensual += Decimal(str(interes_periodo))
        
        
        fecha_actual = ultimo_dia_mes + datetime.timedelta(days=1)

    intereses = total_intereses_mensual  # o total_intereses
    
    multa = float(valor_moneda * 0.10)

    total = float(impuesto) + float(recargos) + float(intereses) + float(multa)

    formatted_impuesto = f"{impuesto:.2f}"
    formatted_recargos = f"{recargos:.2f}"
    formatted_intereses = f"{intereses:.2f}"
    formatted_multa = f"{multa:.2f}"
    formatted_total = f"{total:.2f}"

    if '.' in formatted_impuesto:
        entero, decimal = formatted_impuesto.split('.')
    
    else:
        entero, decimal = formatted_impuesto, '00'

    if '.' in formatted_recargos:
        entero_recargos, decimal_recargos = formatted_recargos.split('.')
    else:
        entero_recargos, decimal_recargos = formatted_recargos, '00'
    
    if '.' in formatted_intereses:
        entero_intereses, decimal_intereses = formatted_intereses.split('.')
    else:
        entero_intereses, decimal_intereses = formatted_intereses, '00'

    if '.' in formatted_multa:
        entero_multa, decimal_multa = formatted_multa.split('.')
    else:
        entero_multa, decimal_multa = formatted_multa, '00'

    if '.' in formatted_total:
        entero_total, decimal_total = formatted_total.split('.')
    else:
        entero_total, decimal_total = formatted_total, '00'

    imp_ent_form = re.sub(r'(\d)(?=(\d{3})+(?!\d))', r'\1.', entero)
    impuesto_formateado = f"{imp_ent_form},{decimal}"
    
    rec_ent_form = re.sub(r'(\d)(?=(\d{3})+(?!\d))', r'\1.', entero_recargos)
    recargos = f"{rec_ent_form},{decimal_recargos}"
        
    int_ent_form = re.sub(r'(\d)(?=(\d{3})+(?!\d))', r'\1.', entero_intereses)
    intereses = f"{int_ent_form},{decimal_intereses}"

    mul_ent_form = re.sub(r'(\d)(?=(\d{3})+(?!\d))', r'\1.', entero_multa)
    multa = f"{mul_ent_form},{decimal_multa}"

    total_ent_form = re.sub(r'(\d)(?=(\d{3})+(?!\d))', r'\1.', entero_total)
    total = f"{total_ent_form},{decimal_total}"

    return {
        'tax': impuesto_formateado,
        'recar': recargos,
        'mult': multa,
        'inter': intereses,
        'total': total
    }

def calculo_periodo_2020(data):

    valor_moneda = 315

    typo_1 = data['typo_1']
    typo_2 = data['typo_2']
    sector_1 = data['sector']
    m_sector = data['m_sector']
    m_typo_1 = data['m_typo_1']
    m_typo_2 = data['m_typo_2']

    val_sector = sector.objects.filter(number=sector_1, period='2019').first()
    val_typo_1 = tipologia.objects.filter(name=typo_1, period='2019').first()
    val_typo_2 = tipologia.objects.filter(name=typo_2, period='2019').first()

    tarfia_sector = (float(val_sector.value) * float(valor_moneda) * m_sector) / 100
    
    tarfia_typo_1 = (float(val_typo_1.value) * float(valor_moneda) * m_typo_1) / 100
    tarfia_typo_2 = (float(val_typo_2.value) * float(valor_moneda) * m_typo_2) / 100
    
    impuesto = float(tarfia_sector + tarfia_typo_1 + tarfia_typo_2)
    impuesto_final = (impuesto/1000000)
    recargos = float(impuesto_final * 0.12)

    if recargos < 0.01:

        recargo_final = 0.01

    else: 

        recargo_final = recargos

    inicio_intereses = datetime.date(2020, 4, 1)
    final_intereses = datetime.date.today()

    total_intereses_mensual = Decimal('0')
    fecha_actual = inicio_intereses

    while fecha_actual <= final_intereses:
        # Obtener primer día del mes actual
        primer_dia_mes = fecha_actual.replace(day=1)
        
        # Calcular último día del mes
        if primer_dia_mes.month == 12:
            ultimo_dia_mes = primer_dia_mes.replace(day=31)
        else:
            ultimo_dia_mes = primer_dia_mes.replace(month=primer_dia_mes.month + 1, day=1) - datetime.timedelta(days=1)
        
        
        if ultimo_dia_mes > final_intereses:
            ultimo_dia_mes = final_intereses
        
        # Contar días en este período
        dias_en_periodo = (ultimo_dia_mes - fecha_actual).days + 1
        
        # Obtener tasa del mes
        mes_str = primer_dia_mes.strftime('%m')
        ano_str = str(primer_dia_mes.year)
        tasa_obj = tasas_interes.objects.filter(mes=mes_str, ano=ano_str).first()
        
        if tasa_obj:
            tasa_porcentaje = float(tasa_obj.value)
            
            interes_periodo = (impuesto_final * tasa_porcentaje / 100 / 360) * dias_en_periodo
            total_intereses_mensual += Decimal(str(interes_periodo))
        
        
        fecha_actual = ultimo_dia_mes + datetime.timedelta(days=1)

    intereses = total_intereses_mensual  # o total_intereses
    multa = Decimal('0.01')
    multa = 0.01

    total = float(impuesto_final) + float(recargo_final) + float(intereses) + float(multa)

    formatted_impuesto = f"{impuesto_final:.2f}"
    formatted_recargos = f"{recargo_final:.2f}"
    formatted_intereses = f"{intereses:.2f}"
    formatted_multa = f"{multa:.2f}"
    formatted_total = f"{total:.2f}"

    if '.' in formatted_impuesto:
        entero, decimal = formatted_impuesto.split('.')
    
    else:
        entero, decimal = formatted_impuesto, '00'

    if '.' in formatted_recargos:
        entero_recargos, decimal_recargos = formatted_recargos.split('.')
    else:
        entero_recargos, decimal_recargos = formatted_recargos, '00'
    
    if '.' in formatted_intereses:
        entero_intereses, decimal_intereses = formatted_intereses.split('.')
    else:
        entero_intereses, decimal_intereses = formatted_intereses, '00'

    if '.' in formatted_multa:
        entero_multa, decimal_multa = formatted_multa.split('.')
    else:
        entero_multa, decimal_multa = formatted_multa, '00'

    if '.' in formatted_total:
        entero_total, decimal_total = formatted_total.split('.')
    else:
        entero_total, decimal_total = formatted_total, '00'

    imp_ent_form = re.sub(r'(\d)(?=(\d{3})+(?!\d))', r'\1.', entero)
    impuesto_formateado = f"{imp_ent_form},{decimal}"
    
    rec_ent_form = re.sub(r'(\d)(?=(\d{3})+(?!\d))', r'\1.', entero_recargos)
    recargos = f"{rec_ent_form},{decimal_recargos}"
        
    int_ent_form = re.sub(r'(\d)(?=(\d{3})+(?!\d))', r'\1.', entero_intereses)
    intereses = f"{int_ent_form},{decimal_intereses}"

    mul_ent_form = re.sub(r'(\d)(?=(\d{3})+(?!\d))', r'\1.', entero_multa)
    multa = f"{mul_ent_form},{decimal_multa}"

    total_ent_form = re.sub(r'(\d)(?=(\d{3})+(?!\d))', r'\1.', entero_total)
    total = f"{total_ent_form},{decimal_total}"

    return {
        'tax': impuesto_formateado,
        'recar': recargos,
        'mult': multa,
        'inter': intereses,
        'total': total
    }

def calculo_periodo_2019(data):

    valor_moneda = 315

    typo_1 = data['typo_1']
    typo_2 = data['typo_2']
    sector_1 = data['sector']
    m_sector = data['m_sector']
    m_typo_1 = data['m_typo_1']
    m_typo_2 = data['m_typo_2']

    val_sector = sector.objects.filter(number=sector_1, period='2019').first()
    val_typo_1 = tipologia.objects.filter(name=typo_1, period='2019').first()
    val_typo_2 = tipologia.objects.filter(name=typo_2, period='2019').first()

    tarfia_sector = (float(val_sector.value) * float(valor_moneda) * m_sector) / 100
    
    tarfia_typo_1 = (float(val_typo_1.value) * float(valor_moneda) * m_typo_1) / 100
    tarfia_typo_2 = (float(val_typo_2.value) * float(valor_moneda) * m_typo_2) / 100
    
    impuesto = float(tarfia_sector + tarfia_typo_1 + tarfia_typo_2)
    impuesto_final = (impuesto/1000000)

    print('tarifa_sector:', tarfia_sector)
    print('metros de sector:', sector_1)
    print('m_sector:', m_sector)


    recargos = float(impuesto_final * 0.12)
    recargo_final = ''

    if recargos < 0.01:

        recargo_final = 0.01

    else: 

        recargo_final = recargos

    inicio_intereses = datetime.date(2019, 4, 1)
    final_intereses = datetime.date.today()
    
    total_intereses_mensual = Decimal('0')
    fecha_actual = inicio_intereses
    
    while fecha_actual <= final_intereses:
        primer_dia_mes = fecha_actual.replace(day=1)
        
        # Calcular último día del mes
        if primer_dia_mes.month == 12:
            ultimo_dia_mes = primer_dia_mes.replace(day=31)
        else:
            ultimo_dia_mes = primer_dia_mes.replace(month=primer_dia_mes.month + 1, day=1) - datetime.timedelta(days=1)
        
        if ultimo_dia_mes > final_intereses:
            ultimo_dia_mes = final_intereses
        
        dias_en_periodo = (ultimo_dia_mes - fecha_actual).days + 1
        
        # OBTENER MES COMO NÚMERO ENTERO (NO STRING)
        mes_num = fecha_actual.month  # 1, 2, 3... 12
        ano_num = fecha_actual.year    # 2025, 2024, etc.
        
        # Filtrar con números enteros
        tasa_obj = tasas_interes.objects.filter(mes=mes_num, ano=ano_num).last()
        
        if tasa_obj:
            tasa_porcentaje = float(tasa_obj.value)
            interes_periodo = ((impuesto_final * (tasa_porcentaje / 100)) / 360) * dias_en_periodo
            total_intereses_mensual += Decimal(str(interes_periodo))
        else:
            print(f"⚠️ No se encontró tasa para mes={mes_num}, año={ano_num}")
        
        fecha_actual = ultimo_dia_mes + datetime.timedelta(days=1)
    
    intereses = total_intereses_mensual
    multa = 0.01

    total = float(impuesto_final) + float(recargo_final) + float(intereses) + float(multa)

    formatted_impuesto = f"{impuesto_final:.2f}"
    formatted_recargos = f"{recargo_final:.2f}"
    formatted_intereses = f"{intereses:.2f}"
    formatted_multa = f"{multa:.2f}"
    formatted_total = f"{total:.2f}"

    if '.' in formatted_impuesto:
        entero, decimal = formatted_impuesto.split('.')
    
    else:
        entero, decimal = formatted_impuesto, '00'

    if '.' in formatted_recargos:
        entero_recargos, decimal_recargos = formatted_recargos.split('.')
    else:
        entero_recargos, decimal_recargos = formatted_recargos, '00'
    
    if '.' in formatted_intereses:
        entero_intereses, decimal_intereses = formatted_intereses.split('.')
    else:
        entero_intereses, decimal_intereses = formatted_intereses, '00'

    if '.' in formatted_multa:
        entero_multa, decimal_multa = formatted_multa.split('.')
    else:
        entero_multa, decimal_multa = formatted_multa, '00'

    if '.' in formatted_total:
        entero_total, decimal_total = formatted_total.split('.')
    else:
        entero_total, decimal_total = formatted_total, '00'

    imp_ent_form = re.sub(r'(\d)(?=(\d{3})+(?!\d))', r'\1.', entero)
    impuesto_formateado = f"{imp_ent_form},{decimal}"
    
    rec_ent_form = re.sub(r'(\d)(?=(\d{3})+(?!\d))', r'\1.', entero_recargos)
    recargos = f"{rec_ent_form},{decimal_recargos}"
        
    int_ent_form = re.sub(r'(\d)(?=(\d{3})+(?!\d))', r'\1.', entero_intereses)
    intereses = f"{int_ent_form},{decimal_intereses}"

    mul_ent_form = re.sub(r'(\d)(?=(\d{3})+(?!\d))', r'\1.', entero_multa)
    multa = f"{mul_ent_form},{decimal_multa}"

    total_ent_form = re.sub(r'(\d)(?=(\d{3})+(?!\d))', r'\1.', entero_total)
    total = f"{total_ent_form},{decimal_total}"

    return {
        'tax': impuesto_formateado,
        'recar': recargos,
        'mult': multa,
        'inter': intereses,
        'total': total
    }






