from django.urls import path
from  .views import *
from Inmuebles import views


urlpatterns = [
    path('calcutations/', views.calcutations, name='calcutations'),
    path('add_calcutations/', views.add_calcutations, name='add_calcutations'),
    path('solic_remi/', views.solic_remi_h, name='solic_remi'),
    path('add_solic_remi/', views.add_solic_remi, name='add_solic_remi'),


    #-------------PDF-----------------------
    path('remi_pdf/<int:id>/', views.remision_pdf, name='remision_pdf'),


    #-------------Listado Calcutations-----------------------
    path('list_calcutations/', views.list_calcutations, name='list_calcutations'),
    path('list_solic_remi/', views.list_solic_remi, name='list_solic_remi'),
]