# test_gemini.py
from utils import analizar_cv_con_gemini

# Simula un texto de CV
cv_texto = """
Juan Pérez
Desarrollador Python con 4 años de experiencia en backend, APIs REST, Django.
Habilidades: Python, Django, SQL, liderazgo, trabajo en equipo, comunicación efectiva.
"""

palabras_clave = "Python, liderazgo, comunicación, APIs, Django"

print("🚀 Iniciando análisis de CV con Gemini AI...\n")
print(f"CV: {cv_texto[:100]}...")
print(f"Palabras clave: {palabras_clave}\n")
print("=" * 60)

try:
    score, razon = analizar_cv_con_gemini(cv_texto, palabras_clave)
    
    if score is not None:
        print(f"✓ Score IA: {score}/100")
        print(f"✓ Razón IA: {razon}")
    else:
        print(f"✗ Error: {razon}")
        
except Exception as e:
    print(f"❌ Error: {e}")

print("=" * 60)