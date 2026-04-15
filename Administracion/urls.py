from django.urls import path
from  .views import *
from Administracion import views

urlpatterns = [
    path('home/', Home, name='home'),
    path("profile/<int:id>", views.profile, name="profile"),
    path('editar_funcionario/<int:id>/', views.editar_funcionario, name='editar_funcionario'),
    path('eliminar_funcionario/<int:id>/', views.eliminar_funcionario, name='eliminar_funcionario'),
    



    #--------------Funcionarios-----------------------
    path('funcionarios/', Funcionarios, name='funcionarios'),
    path('listado_funcionarios/', views.lista_funcionarios, name='lista_funcionarios'),
    path('crear_funcionario/', views.crear_funcionario, name='crear_funcionario'),

]