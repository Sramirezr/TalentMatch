from django.db import models

class Vacante(models.Model):
    titulo = models.CharField(max_length=200)
    nombre_interno = models.CharField(max_length=200, blank=True, null=True)  # <-- este campo es solo para el reclutador
    descripcion = models.TextField()
    palabras_clave = models.CharField(max_length=300, blank=True, null=True)
    rango_salarial = models.CharField(max_length=100, blank=True, null=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)


    def __str__(self):
        return self.titulo

