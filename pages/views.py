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

def postularse_view(request, vacante_id):
    vacante = get_object_or_404(Vacante, id=vacante_id)
    
    if request.method == "POST":
        form = PostulacionForm(request.POST, request.FILES)
        if form.is_valid():
            postulacion = form.save(commit=False)
            postulacion.postulante = request.user
            postulacion.vacante = vacante
            
            # ⭐ ANALIZAR CON IA AUTOMÁTICAMENTE
            if postulacion.cv_pdf:
                print(f"🤖 Analizando CV con IA para vacante: {vacante.titulo}")
                
                # Extraer texto del PDF
                texto_cv = extraer_texto_pdf(postulacion.cv_pdf.file)
                
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
            
            postulacion.save()
            messages.success(request, "¡Has postulado exitosamente! Tu CV ha sido analizado por IA.")
            return redirect('postulante')
    else:
        form = PostulacionForm()
    
    return render(request, 'pages/postularse.html', {'form': form, 'vacante': vacante})

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


def postularse_view(request, vacante_id):
    vacante = get_object_or_404(Vacante, id=vacante_id)
    if request.method == "POST":
        form = PostulacionForm(request.POST, request.FILES)
        if form.is_valid():
            postulacion = form.save(commit=False)
            postulacion.postulante = request.user  # Ajusta según tu modelo de usuario
            postulacion.vacante = vacante
            postulacion.save()
            messages.success(request, "¡Has postulado exitosamente!")
            return redirect('postulante')
    else:
        form = PostulacionForm()
    return render(request, 'pages/postularse.html', {'form': form, 'vacante': vacante})

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
    
    # ⭐ OBTENER POSTULACIONES ORDENADAS POR SCORE IA
    postulaciones = Postulacion.objects.filter(vacante=vacante).order_by('-score_ia')
    
    mejores_candidatos = []
    for post in postulaciones:
        if post.score_ia is not None:
            mejores_candidatos.append({
                'nombre': post.postulante.username,
                'email': post.postulante.email,
                'score': post.score_ia,
                'ia_razon': post.razon_ia,
                'cv_url': post.cv_pdf.url if post.cv_pdf else '#'
            })
    
    return render(request, 'pages/detalle_vacante_reclutador.html', {
        'vacante': vacante,
        'mejores_candidatos': mejores_candidatos
    })