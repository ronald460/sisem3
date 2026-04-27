from django.urls import path
from  .views import *
from Bienes import views


urlpatterns = [
    path('bienes/', views.bienes, name='bienes'),
    path('add_bien/<int:id>/', views.add_bien, name='add_bien'),
    path('bienes_detallado/<int:id>/', views.bienes_detallado, name='bienes_detallado'),
    path('edit_bien_det/<int:id>/', views.editar_asignacion, name='edit_bien_det'),
    path('borrar_asignacion/<int:id>/', views.borrar_asignacion, name='borrar_asignacion'),
    path('bienes_det/', views.bienes_det, name='bienes_det'),
    path('bienes_pd/', views.bienes_pd, name='bienes_pd'),
    path('add_bien_pd/', views.add_bien_pd, name='add_bien_pd'),
    path('delete_bien_pd/<int:id>/', views.delete_bien_pd, name='delete_bien_pd'),
    path('bienes_ci/', views.bienes_ci, name='bienes_ci'),
    path('add_bien_ci/', views.add_bien_ci, name='add_bien_ci'),
    path('delete_bien_ci/<int:id>/', views.delete_bien_ci, name='delete_bien_ci'),
    path('etiquetas_bm_pdf/', views.etiquetas_bm_pdf, name='etiquetas_bm'),
    path('etiquetas_ci_pdf/', views.etiquetas_ci_pdf, name='etiquetas_ci'),
    path('etiquetas_pd_pdf/', views.etiquetas_pd_pdf, name='etiquetas_pd'),
    path('rpu_pdf/', views.rpu_pdf, name='rpu_pdf'),
    

    #--------------Reportes Bienes-----------------------
    path('reporte_bxa_excel/', views.reporte_bxa_excel, name='reporte_bxa_excel'),
    path('export_bxa_excel/', export_bxa_excel.as_view(), name='export_bxa_excel'),
    path('reporte_bienes_excel/', views.reporte_bienes_excel, name='reporte_bienes_excel'),
    path('export_bienes_excel/', export_bienes_excel.as_view(), name='export_bienes_excel'),




    #--------------Listado Bienes-----------------------
    path('listado_bienes/', views.lista_bienes, name='lista_bienes'),
    path('listado_bienes_det/', views.lista_bienes_det, name='lista_bienes_det'),
    path('listado_bienes_asignados/', views.listado_bienes_det, name='lista_bienes_asignados'),
    path('lisado_bienes_pd/', views.lista_bienes_pd, name='lista_bienes_pd'),
    path('listado_bienes_ci/', views.lista_bienes_ci, name='lista_bienes_ci'),
    
   

]