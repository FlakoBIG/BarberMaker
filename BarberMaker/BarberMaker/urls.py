"""BarberMaker URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from  BarberMakerApp import views
urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.opciones, name='opciones'),
    path('crear_barberia/', views.crear_barberia, name='crear_barberia'),
    path('listar_barberias/', views.listar_barberias, name='listar_barberias'),
    path('barberia/<str:barberia_id>/', views.barberia_seleccionada, name='barberia_seleccionada'),
    path('administrar_barberia/', views.administrar_barberia, name='administrar_barberia'),
    path('modificar_barberia/<str:barberia_id>/', views.modificar_barberia, name='modificar_barberia'),
    path('eliminar_barberia/<str:barberia_id>/', views.eliminar_barberia, name='eliminar_barberia'),
    path('agregar_corte/<str:barberia_id>/', views.agregar_corte, name='agregar_corte'),
    path('modificar_corte/<str:barberia_id>/<str:corte_nombre>/', views.modificar_corte, name='modificar_corte'),
    path('eliminar_corte/<str:barberia_id>/<str:corte_nombre>/', views.eliminar_corte, name='eliminar_corte'),

    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.login_view, name='logout'),
    
    path('postular/<str:barberia_id>', views.postular, name='postular'),  
    path('lista_de_postulantes/<str:barberia_id>', views.lista_de_postulantes, name='lista_de_postulantes'),
    path('contratar_postulante/<str:barberia_id>/<str:postulante_uid>/', views.contratar_postulante, name='contratar_postulante'),
    path('lista_de_trabajadores/<str:barberia_id>', views.lista_de_trabajadores, name='lista_de_trabajadores'),
    path('galeria/<str:barberia_id>/', views.galeria_fotos, name='galeria_fotos'),
    path('agregar-foto/<str:barberia_id>/', views.agregar_foto, name='agregar_foto'),
    path('agregar_foto_cliente/<str:barberia_id>/', views.agregar_foto_cliente, name='agregar_foto_cliente'),
    path('administrar_barberia/<str:barberia_id>/Fotos/<str:id_foto>/eliminar/', views.eliminar_foto, name='eliminar_foto'),
    #----------------------------------------nuevo el cambio de estado aun no funciona
    path('login2/<str:barberia_id>/', views.login_view2, name='login2'),#
    path('cambiar_estado/<str:cita_id>/', views.cambiar_estado, name='cambiar_estado'),
    path('eliminar_cita/<str:cita_id>/', views.eliminar_cita, name='eliminar_cita'),
    ]