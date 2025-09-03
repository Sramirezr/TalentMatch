from django.shortcuts import render, redirect
from .models import Vacante

# Create your views here.
def home_view(request):
    return render(request, 'pages/home.html')

def postulante_view(request):
    vacantes = Vacante.objects.all().order_by('-fecha_creacion')
    return render(request, 'pages/postulante.html', {"vacantes": vacantes})
    

def reclutador_view(request):
    return render(request, 'pages/reclutador.html')

def crear_vacante_view(request):
    return render(request, 'pages/crear_vacante.html')

def crear_vacante(request):
   
    if request.method == "POST":
        titulo = request.POST.get("titulo")
        descripcion = request.POST.get("descripcion")
        palabras_clave = request.POST.get("palabras_clave", "")
        rango_salarial = request.POST.get("rango_salarial", "")

        Vacante.objects.create(
            titulo=titulo,
            descripcion=descripcion,
            palabras_clave=palabras_clave,
            rango_salarial=rango_salarial
        )

        return redirect("reclutador")  # Vuelve al panel del reclutador

    return render(request, "crear_vacante.html")

def panel_reclutador(request):
    vacantes = Vacante.objects.all().order_by('-fecha_creacion')
    return render(request, "panel_reclutador.html", {"vacantes": vacantes})



