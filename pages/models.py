# pages/models.py
from django.db import models
from django.conf import settings
from django.contrib.auth.models import User

class Vacante(models.Model):
    titulo = models.CharField(max_length=200)
    nombre_interno = models.CharField(max_length=200, blank=True, null=True)
    descripcion = models.TextField()
    palabras_clave = models.CharField(max_length=300, blank=True, null=True)
    rango_salarial = models.CharField(max_length=100, blank=True, null=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.titulo


class Postulacion(models.Model):
    # Estados posibles
    ESTADO_CHOICES = [
        ('PENDIENTE', 'Pendiente'),
        ('REVISADO', 'Revisado'),
        ('ACEPTADO', 'Aceptado'),
        ('RECHAZADO', 'Rechazado'),
    ]
    
    postulante = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    vacante = models.ForeignKey('Vacante', on_delete=models.CASCADE)
    cv_pdf = models.FileField(upload_to='cvs/', null=True, blank=True)
    fecha_postulacion = models.DateTimeField(auto_now_add=True)
    
    # Campos para la IA
    score_ia = models.IntegerField(null=True, blank=True, help_text="Score de 0-100 generado por IA")
    razon_ia = models.TextField(null=True, blank=True, help_text="Razón del score generada por IA")
    
    # 🆕 NUEVOS CAMPOS DE ESTADO
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='PENDIENTE')
    notas_reclutador = models.TextField(blank=True, null=True, help_text="Notas del reclutador")
    
    class Meta:
        ordering = ['-score_ia', '-fecha_postulacion']
        # Evitar que un usuario se postule dos veces a la misma vacante
        unique_together = ['postulante', 'vacante']
    
    def __str__(self):
        return f"{self.postulante.username} -> {self.vacante.titulo} (Score: {self.score_ia}) [{self.estado}]"

# pages/models.py - Agregar DESPUÉS del modelo Profile

class Notificacion(models.Model):
    TIPO_CHOICES = [
        ('CAMBIO_ESTADO', 'Cambio de Estado'),
        ('NUEVA_VACANTE', 'Nueva Vacante'),
        ('MENSAJE', 'Mensaje'),
    ]
    
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notificaciones')
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES, default='MENSAJE')
    titulo = models.CharField(max_length=200)
    mensaje = models.TextField()
    postulacion = models.ForeignKey('Postulacion', on_delete=models.CASCADE, null=True, blank=True, related_name='notificaciones')
    leida = models.BooleanField(default=False)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-fecha_creacion']
    
    def __str__(self):
        return f"{self.usuario.username} - {self.titulo} ({'Leída' if self.leida else 'No leída'})"
    
class Profile(models.Model):
    USER_TYPE_CHOICES = (
        ("postulante", "Postulante"),
        ("reclutador", "Reclutador"),
    )
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    user_type = models.CharField(max_length=20, choices=USER_TYPE_CHOICES)

    def __str__(self):
        return f"{self.user.username} ({self.user_type})"