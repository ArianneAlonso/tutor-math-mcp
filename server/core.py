import os
from dotenv import load_dotenv
load_dotenv()

import json
import io
import google.generativeai as genai
from PIL import Image
import base64
import logging

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise ValueError("No se encontró la variable de entorno GEMINI_API_KEY")

genai.configure(api_key=GEMINI_API_KEY)

logging.basicConfig(level=logging.INFO)

model = genai.GenerativeModel('gemini-2.5-flash')

def analyze_image(image_base64: str, dict_of_vars: dict):
    dict_of_vars_str = json.dumps(dict_of_vars)

    prompt = f"""
Se te ha dado una imagen con algunas expresiones matemáticas o ecuaciones, y necesitas resolverlas.
Usa el diccionario de variables: {dict_of_vars_str}
Responde SOLO en JSON válido.
Formato:
[
  {{"expr": "...", "result": ..., "assign": true/false}}
]
NO incluyas texto fuera del JSON.
"""

    try:
        image_data = base64.b64decode(image_base64.split(",")[-1])
        image = Image.open(io.BytesIO(image_data))
        
        response = model.generate_content([
            prompt,
            image
        ])

        clean_text = response.text

        try:
            parsed = json.loads(clean_text)
        except json.JSONDecodeError:
            logging.error(f"Error al decodificar JSON del modelo: {clean_text}")
            parsed = [{"expr": "error", "result": f"El modelo no generó JSON válido: {clean_text}", "assign": False}]

        return parsed

    except Exception as e:
        logging.error(f"Error en analyze_image: {e}")
        return [{"expr": "error", "result": str(e), "assign": False}]