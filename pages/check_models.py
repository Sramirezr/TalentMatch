# check_models.py
import google.generativeai as genai
import os

# OPTION 1: Use environment variable (recommended)
api_key = os.environ.get("GEMINI_API_KEY")

# OPTION 2: Hardcode for testing (not recommended for production)
if not api_key:
    api_key = "AIzaSyAZhebkaU43ADZvgIHJnOOvSuQZzwfSpmM"  # Your actual key

if not api_key:
    print("⚠️ GEMINI_API_KEY not found!")
    exit()

print(f"🔑 Using API key: {api_key[:10]}...")

genai.configure(api_key=api_key)

print("🔍 Checking available Gemini models...\n")

try:
    models = genai.list_models()
    print("✓ Available models that support generateContent:")
    count = 0
    for m in models:
        if 'generateContent' in m.supported_generation_methods:
            print(f"  • {m.name}")
            count += 1
    
    if count == 0:
        print("  ⚠️ No models found that support generateContent")
    print()
except Exception as e:
    print(f"✗ Error listing models: {e}\n")