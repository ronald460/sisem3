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
    



    #--------------Bienes-----------------------
    path('listado_bienes/', views.lista_bienes, name='lista_bienes'),
    path('listado_bienes_det/', views.lista_bienes_det, name='lista_bienes_det'),
    path('listado_bienes_asignados/', views.listado_bienes_det, name='lista_bienes_asignados'),
    path('lisado_bienes_pd/', views.lista_bienes_pd, name='lista_bienes_pd'),
    
   

]