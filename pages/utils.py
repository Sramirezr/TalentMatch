# pages/utils.py
import google.generativeai as genai
import json
import PyPDF2
import os

# Configurar Gemini API (SOLO desde variable de entorno)
api_key = os.environ.get("GEMINI_API_KEY")
if not api_key:
    print("⚠️ ADVERTENCIA: GEMINI_API_KEY no está configurada")
else:
    genai.configure(api_key=api_key)

DEFAULT_PALABRAS_CLAVE = "trabajo en equipo, comunicación, responsabilidad, proactividad"


def extraer_texto_pdf(archivo_pdf):
    """
    Extrae texto de un archivo PDF (Django FileField)
    """
    try:
        texto = ""
        archivo_pdf.seek(0)  # Ir al inicio del archivo
        
        print(f"📄 Intentando leer PDF...")
        lector = PyPDF2.PdfReader(archivo_pdf)
        
        num_paginas = len(lector.pages)
        print(f"📄 PDF tiene {num_paginas} página(s)")
        
        for i, pagina in enumerate(lector.pages):
            texto_pagina = pagina.extract_text()
            print(f"   Página {i+1}: {len(texto_pagina)} caracteres extraídos")
            texto += texto_pagina + "\n"
        
        texto = texto.strip()
        
        if not texto:
            print("❌ El PDF no contiene texto extraíble (posiblemente es una imagen escaneada)")
            return None
        
        print(f"✅ Total texto extraído: {len(texto)} caracteres")
        print(f"Primeros 300 caracteres:\n{texto[:300]}...\n")
        
        return texto
        
    except Exception as e:
        print(f"❌ Error extrayendo PDF: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return None


def analizar_cv_con_gemini(texto_cv, palabras_clave):
    """
    Analiza un CV usando Gemini AI y proporciona feedback constructivo al candidato
    """
    if not palabras_clave:
        palabras_clave = DEFAULT_PALABRAS_CLAVE
    
    # 🆕 PROMPT MEJORADO CON FEEDBACK CONSTRUCTIVO
    prompt = (
        f"Eres un experto reclutador de recursos humanos con 15 años de experiencia.\n\n"
        f"PALABRAS CLAVE DEL PUESTO: {palabras_clave}\n\n"
        f"CV DEL CANDIDATO:\n{texto_cv}\n\n"
        "INSTRUCCIONES:\n"
        "1. Evalúa el match del CV con las palabras clave (score de 0 a 100)\n"
        "2. Proporciona FEEDBACK CONSTRUCTIVO que incluya:\n"
        "   - Fortalezas principales del candidato\n"
        "   - Áreas de mejora o habilidades que debería destacar más\n"
        "   - Recomendaciones específicas para mejorar su perfil\n\n"
        "IMPORTANTE:\n"
        "- Sé honesto pero motivador\n"
        "- Menciona habilidades específicas encontradas (o que faltan)\n"
        "- Máximo 3-4 líneas de feedback útil y accionable\n\n"
        "Responde ÚNICAMENTE con un JSON válido en este formato:\n"
        '{"score": [número 0-100], "razon": "[feedback constructivo de 3-4 líneas]"}\n\n'
        "Ejemplo:\n"
        '{"score": 75, "razon": "Excelente experiencia en trabajo en equipo y comunicación. '
        'Tu CV destaca liderazgo de proyectos. Recomendación: Incluye logros cuantificables '
        'y certifica tus conocimientos técnicos para fortalecer tu candidatura."}'
    )
    
    try:
        print(f"🤖 Enviando a Gemini AI...")
        model = genai.GenerativeModel("models/gemini-2.0-flash-exp")
        
        response = model.generate_content(prompt)
        response_text = response.text.strip()
        
        print(f"📝 Respuesta de IA (primeros 200 chars):\n{response_text[:200]}...\n")
        
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
            score = max(0, min(100, score))
        else:
            # Si no hay score, asignar uno por defecto
            score = 50
            razon = "Tu CV ha sido recibido. Recomendamos incluir más información sobre tus habilidades y experiencia."
        
        # Validar que haya razón
        if not razon or len(razon) < 20:
            razon = "Tu CV muestra potencial. Recomendación: Destaca tus logros principales y habilidades específicas para el puesto."
        
        print(f"✅ Score: {score}/100")
        print(f"✅ Razón: {razon}\n")
        
        return score, razon
        
    except json.JSONDecodeError as e:
        print(f"⚠️ Error parseando JSON: {e}")
        print(f"Respuesta recibida: {response_text}\n")
        return 50, "Tu CV ha sido recibido. Recomendamos destacar tus habilidades y experiencia relevante al puesto."
        
    except Exception as e:
        print(f"❌ Error en análisis IA: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return 50, "Error al procesar tu CV. Por favor, verifica que el archivo sea legible e intenta nuevamente."