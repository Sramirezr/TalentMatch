from django.db import models
from django.conf import settings
from django.contrib.auth.models import User


class Vacante(models.Model):
    titulo = models.CharField(max_length=200)
    nombre_interno = models.CharField(max_length=200, blank=True, null=True)  # <-- este campo es solo para el reclutador
    descripcion = models.TextField()
    palabras_clave = models.CharField(max_length=300, blank=True, null=True)
    rango_salarial = models.CharField(max_length=100, blank=True, null=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)


    def __str__(self):
        return self.titulo


class Postulacion(models.Model):
    postulante = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    vacante = models.ForeignKey('Vacante', on_delete=models.CASCADE)
    cv_pdf = models.FileField(upload_to='cvs/', null=True, blank=True)
    fecha_postulacion = models.DateTimeField(auto_now_add=True)


class Profile(models.Model):
    USER_TYPE_CHOICES = (
        ("postulante", "Postulante"),
        ("reclutador", "Reclutador"),
    )
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    user_type = models.CharField(max_length=20, choices=USER_TYPE_CHOICES)

    def __str__(self):
        return f"{self.user.username} ({self.user_type})"