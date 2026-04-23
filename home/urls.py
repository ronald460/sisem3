from django.urls import path
from  .views import *
from home import views

urlpatterns = [
    path('reportes/', views.reportes, name='reportes'),






    #--------------Reportes-----------------------
    path('listado_reportes/', views.listado_reportes, name='lista_reportes'),
]