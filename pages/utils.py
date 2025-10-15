# pages/utils.py
import google.generativeai as genai
import json
import PyPDF2
import os

# Configurar Gemini API
genai.configure(api_key=os.environ.get("GEMINI_API_KEY", "AIzaSyAZhebkaU43ADZvgIHJnOOvSuQZzwfSpmM"))

DEFAULT_PALABRAS_CLAVE = "trabajo en equipo, comunicación, responsabilidad, proactividad"


def extraer_texto_pdf(archivo_pdf):
    """
    Extrae texto de un archivo PDF (Django FileField)
    
    Args:
        archivo_pdf: FileField de Django con el PDF
    
    Returns:
        str: Texto extraído del PDF
    """
    try:
        texto = ""
        # Abrir el archivo desde el FileField
        archivo_pdf.seek(0)  # Asegurar que estamos al inicio del archivo
        lector = PyPDF2.PdfReader(archivo_pdf)
        
        for pagina in lector.pages:
            texto += pagina.extract_text() + "\n"
        
        if not texto.strip():
            return None
        
        return texto.strip()
        
    except Exception as e:
        print(f"❌ Error extrayendo PDF: {e}")
        return None


def analizar_cv_con_gemini(texto_cv, palabras_clave):
    """
    Analiza un CV usando Gemini AI
    
    Args:
        texto_cv: Texto del CV a analizar
        palabras_clave: Palabras clave de la vacante
    
    Returns:
        tuple: (score, razon)
    """
    if not palabras_clave:
        palabras_clave = DEFAULT_PALABRAS_CLAVE
    
    prompt = (
        f"Vacante busca: {palabras_clave}.\n"
        "Analiza el siguiente CV y responde ÚNICAMENTE con un JSON válido con dos campos: "
        "'score' (número de 0 a 100 que representa el match con las palabras clave) y "
        "'razon' (explicación breve del puntaje y habilidades encontradas relevantes).\n\n"
        f"CV: {texto_cv}\n\n"
        "Responde SOLO el JSON, sin texto adicional. Ejemplo: {\"score\": 85, \"razon\": \"Buen match porque...\"}"
    )
    
    try:
        model = genai.GenerativeModel("models/gemini-2.5-flash")
        
        response = model.generate_content(prompt)
        response_text = response.text.strip()
        
        print(f"📝 Respuesta IA: {response_text[:200]}...")
        
        # Limpiar markdown si existe
        if "```json" in response_text:
            response_text = response_text.split("```json")[1].split("```")[0]
        elif "```" in response_text:
            lines = response_text.split("```")
            for line in lines:
                if line.strip().startswith("{"):
                    response_text = line
                    break
        
        response_text = response_text.strip()
        
        resultado = json.loads(response_text)
        score = resultado.get("score")
        razon = resultado.get("razon")
        
        # Validar score
        if score is not None:
            score = int(score)
            score = max(0, min(100, score))  # Asegurar que esté entre 0-100
        
        return score, razon
        
    except json.JSONDecodeError as e:
        print(f"⚠️ Error parseando JSON: {e}")
        return 50, f"No se pudo analizar correctamente: {response_text[:100]}"
        
    except Exception as e:
        print(f"❌ Error en análisis IA: {e}")
        return None, f"Error: {str(e)}"