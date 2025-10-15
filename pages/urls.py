from django.urls import path
from . import views

urlpatterns = [
      path('', views.home_view, name='home'), 
      path('postulante/', views.postulante_view, name='postulante'),

      path('Reclutador/', views.reclutador_view, name='reclutador'),
      path('Crear_Vacante/', views.crear_vacante_view, name='crear_vacante'),
      path('guardar_vacante/', views.crear_vacante, name='guardar_vacante'), 
      path('vacante/reclutador/<int:vacante_id>/', views.detalle_vacante_reclutador, name='detalle_vacante_reclutador'),
      path('vacante/eliminar/<int:vacante_id>/', views.eliminar_vacante, name='eliminar_vacante'),
      path('vacante/<int:vacante_id>/editar/', views.editar_vacante, name='editar_vacante'),
      path("login/", views.login_view, name="login"),
      path("logout/", views.logout_view, name="logout"),
      path("register/", views.register_view, name="register"),
      path("login_reclutador/", views.login_reclutador_view, name="login_reclutador"),
      path('postulacion/<int:postulacion_id>/cambiar-estado/', views.cambiar_estado_postulacion, name='cambiar_estado_postulacion'),
      path('perfil/', views.perfil_postulante, name='perfil_postulante'),
      path('notificacion/<int:notificacion_id>/leer/', views.marcar_notificacion_leida, name='marcar_notificacion_leida'),
      path('notificaciones/marcar-todas-leidas/', views.marcar_todas_leidas, name='marcar_todas_leidas'),
     
]




