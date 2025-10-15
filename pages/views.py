from django.shortcuts import render, redirect, get_object_or_404
from .models import Vacante
from django.contrib import messages
from django.db.models.functions import Lower  
from .forms import PostulacionForm
from django.contrib.auth import authenticate, login, logout
from .models import Profile
from django.contrib.auth.forms import AuthenticationForm
from .forms import UserRegisterForm
from .models import Profile, Postulacion
from .utils import extraer_texto_pdf, analizar_cv_con_gemini

# Create your views here.
def home_view(request):
    return render(request, 'pages/home.html')

def postulante_view(request):
    """
    Vista que muestra vacantes Y procesa la subida de CV con análisis de IA
    """
    query = request.GET.get("q", "").strip()
    rango_salarial = request.GET.get("rango_salarial", "").strip()
    selected_id = request.GET.get('vacante_id')

    # PROCESAR SUBIDA DE CV (POST)
    if request.method == "POST" and selected_id:
        vacante = get_object_or_404(Vacante, id=selected_id)
        cv_pdf = request.FILES.get('cv_pdf')
        
        if cv_pdf and request.user.is_authenticated:
            # Crear la postulación
            postulacion = Postulacion(
                postulante=request.user,
                vacante=vacante,
                cv_pdf=cv_pdf
            )
            
            # ANALIZAR CON IA
            try:
                print(f"🤖 Analizando CV con IA para vacante: {vacante.titulo}")
                
                # Extraer texto del PDF
                texto_cv = extraer_texto_pdf(cv_pdf.file)
                
                if texto_cv:
                    # Analizar con Gemini
                    palabras_clave = vacante.palabras_clave or ""
                    score, razon = analizar_cv_con_gemini(texto_cv, palabras_clave)
                    
                    # Guardar resultados
                    postulacion.score_ia = score
                    postulacion.razon_ia = razon
                    
                    print(f"✓ Score IA: {score}/100")
                else:
                    print("⚠️ No se pudo extraer texto del PDF")
                    postulacion.score_ia = 0
                    postulacion.razon_ia = "No se pudo extraer texto del CV"
            except Exception as e:
                print(f"❌ Error: {e}")
                postulacion.score_ia = 0
                postulacion.razon_ia = f"Error: {str(e)}"
            
            postulacion.save()
            messages.success(request, f"¡Postulación exitosa! Tu CV fue calificado con {postulacion.score_ia}/100 por IA.")
            
            # Redirigir para evitar reenvío
            return redirect(f'/postulante/?vacante_id={selected_id}')
        else:
            messages.error(request, "Debes subir un PDF y estar autenticado.")

    # MOSTRAR VACANTES (GET)
    vacantes = Vacante.objects.all().order_by('-fecha_creacion')
    if query:
        vacantes = vacantes.annotate(titulo_lower=Lower('titulo')).filter(titulo_lower__icontains=query.lower())
    if rango_salarial:
        vacantes = vacantes.filter(rango_salarial__icontains=rango_salarial)

    vacante_seleccionada = Vacante.objects.filter(pk=selected_id).first() if selected_id else None
    
    return render(request, 'pages/postulante.html', {
        "vacantes": vacantes,
        "vacante_seleccionada": vacante_seleccionada,
        "selected_id": selected_id,
        "query": query,
        "rango_salarial": rango_salarial,
    })


def reclutador_view(request):
    vacantes = Vacante.objects.all().order_by('-fecha_creacion')
    return render(request, 'pages/reclutador.html', {'vacantes': vacantes})

def crear_vacante_view(request):
    return render(request, 'pages/crear_vacante.html')


def crear_vacante(request):
    if request.method == "POST":
        titulo = request.POST.get("titulo")
        nombre_interno = request.POST.get("nombre_interno", "")  # <-- nuevo
        descripcion = request.POST.get("descripcion")
        palabras_clave = request.POST.get("palabras_clave", "")
        rango_salarial = request.POST.get("rango_salarial", "")

        Vacante.objects.create(
            titulo=titulo,
            nombre_interno=nombre_interno,
            descripcion=descripcion,
            palabras_clave=palabras_clave,
            rango_salarial=rango_salarial
        )

        return redirect("reclutador")

    return render(request, "crear_vacante.html")

def panel_reclutador(request):
    vacantes = Vacante.objects.all().order_by('-fecha_creacion')
    return render(request, "panel_reclutador.html", {"vacantes": vacantes})

def detalle_vacante_reclutador(request, vacante_id):
    vacante = get_object_or_404(Vacante, id=vacante_id)
    return render(request, 'pages/detalle_vacante_reclutador.html', {'vacante': vacante})

def eliminar_vacante(request, vacante_id):
    try:
        vacante = Vacante.objects.get(id=vacante_id)
        vacante.delete()
        messages.success(request, "Vacante eliminada correctamente.")
    except Vacante.DoesNotExist:
        messages.warning(request, "La vacante no existe o ya fue eliminada.")
    return redirect('reclutador')

def editar_vacante(request, vacante_id):
    vacante = get_object_or_404(Vacante, id=vacante_id)
    if request.method == "POST":
        vacante.titulo = request.POST.get("titulo")
        vacante.nombre_interno = request.POST.get("nombre_interno")
        vacante.descripcion = request.POST.get("descripcion")
        vacante.palabras_clave = request.POST.get("palabras_clave")
        vacante.rango_salarial = request.POST.get("rango_salarial")
        vacante.save()
        return redirect("reclutador")
    return render(request, "pages/editar_vacante.html", {"vacante": vacante})



def register_view(request):
    if request.method == "POST":
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data["password"])
            user.save()
            # SIEMPRE crea el perfil como postulante
            Profile.objects.create(user=user, user_type="postulante")
            messages.success(request, "¡Registro exitoso! Ya puedes iniciar sesión.")
            return redirect("login")
    else:
        form = UserRegisterForm()
    # Usar el mismo template, pero en modo registro
    return render(request, "pages/login_register.html", {"form": form, "register_mode": True})

def login_view(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            # Redirige según el tipo de usuario
            if hasattr(user, "profile") and user.profile.user_type == "reclutador":
                return redirect("reclutador")
            else:
                return redirect("postulante")
        else:
            messages.error(request, "Usuario o contraseña incorrectos.")
    # Usar el mismo template, pero en modo login
    form = UserRegisterForm()
    return render(request, "pages/login_register.html", {"form": form, "register_mode": False})

def logout_view(request):
    logout(request)
    return redirect("login")

def login_reclutador_view(request):
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            try:
                profile = Profile.objects.get(user=user)
                if profile.user_type == "reclutador":
                    login(request, user)
                    return redirect("reclutador")
                else:
                    form.add_error(None, "Este usuario no es reclutador.")
            except Profile.DoesNotExist:
                form.add_error(None, "No se encontró el perfil de este usuario.")
    else:
        form = AuthenticationForm()
    return render(request, "pages/login_reclutador.html", {"form": form})

def detalle_vacante_reclutador(request, vacante_id):
    vacante = get_object_or_404(Vacante, id=vacante_id)
    postulaciones = Postulacion.objects.filter(vacante=vacante)
    top_candidatos = postulaciones.exclude(score_ia=None).order_by('-score_ia')[:5]
    recientes = postulaciones.order_by('-fecha_postulacion')[:5]
    todos = postulaciones.order_by('-score_ia')
    return render(request, 'pages/detalle_vacante_reclutador.html', {
        'vacante': vacante,
        'top_candidatos': top_candidatos,
        'recientes': recientes,
        'todos': todos,
    })