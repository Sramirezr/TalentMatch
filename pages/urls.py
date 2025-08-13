from django.urls import path
from . import views

urlpatterns = [
      path('', views.home_view, name='home'), 
      path('postulante/', views.postulante_view, name='postulante'),
      path('Reclutador/', views.reclutador_view, name='reclutador'),
      path('Crear_Vacante/', views.crear_vacante_view, name='crear_vacante'),
]
