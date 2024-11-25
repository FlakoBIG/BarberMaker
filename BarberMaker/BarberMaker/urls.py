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
    path('administrar_barberia/<str:barberia_id>/', views.administrar_barberia, name='administrar_barberia'),
    path('modificar_barberia/<str:barberia_id>/', views.modificar_barberia, name='modificar_barberia'),
    path('agregar_corte/<str:barberia_id>/', views.agregar_corte, name='agregar_corte'),
    path('eliminar_corte/<str:barberia_id>/<str:corte_nombre>/', views.eliminar_corte, name='eliminar_corte'),

    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.login_view, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('postular/<str:barberia_id>', views.postular, name='postular'),  
    path('lista_de_postulantes/<str:barberia_id>', views.lista_de_postulantes, name='lista_de_postulantes'),
    path('contratar_postulante/<str:barberia_id>/<str:postulante_uid>/', views.contratar_postulante, name='contratar_postulante'),
  






    
    ]