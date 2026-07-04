from django.urls import path
from  .views import *
from home import views

urlpatterns = [
    path('reportes/', views.reportes, name='reportes'),
    path('act_confid/', views.act_confid, name='act_confid'),
    path('listado_act_confid/', views.listado_act_confid, name='lista_act_confid'),
    path('act_confid_create/', views.act_confid_create, name='act_confid_create'),
    path('delete_act/<int:id>/', views.delete_actconf, name='delete_actconf'),
    path('act_confid_pdf/<int:id>/', views.ActconfiPdf, name='act_confid_pdf'),






    #--------------Reportes-----------------------
    path('listado_reportes/', views.listado_reportes, name='lista_reportes'),
]