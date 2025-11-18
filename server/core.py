import os
from dotenv import load_dotenv
load_dotenv()

import json
import io
import google.generativeai as genai
from PIL import Image
import base64
import logging
import re

logging.basicConfig(level=logging.INFO)

def clean_response_text(clean_text: str) -> str:
    pattern = r'``````'
    cleaned = re.sub(pattern, '', clean_text, flags=re.DOTALL)
    logging.info(f'Contenido original respuesta del modelo:\n{clean_text}')
    return cleaned

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise ValueError("No se encontró la variable de entorno GEMINI_API_KEY")

genai.configure(api_key=GEMINI_API_KEY)

model = genai.GenerativeModel('gemini-2.5-flash')

def analyze_image(image_base64: str, dict_of_vars: dict):
    dict_of_vars_str = json.dumps(dict_of_vars)
    prompt = f"""
Se te ha dado una imagen con algunas expresiones matemáticas o ecuaciones, y necesitas resolverlas.
Usa el diccionario de variables: {dict_of_vars_str}
Responde SOLO en JSON válido. no escribas backticks ni nada más. no pongas ```` ni etiquetas de ningún tipo.
Formato:
[
  {{"expr": "...", "result": ..., "assign": true/false}}
]
NO incluyas texto fuera del JSON.
"""
    try:
        logging.info('Iniciando decodificación de imagen base64')
        image_data = base64.b64decode(image_base64.split(",")[-1])
        image = Image.open(io.BytesIO(image_data))
        logging.info('Imagen decodificada y cargada exitosamente')

        logging.info('Enviando prompt y la imagen al modelo generativo')
        response = model.generate_content([
            prompt,
            image
        ])

        clean_text = clean_response_text(response.text)

        parsed = json.loads(clean_text)
        logging.info('JSON parseado exitosamente')
        return parsed
    except json.JSONDecodeError as e:
        logging.error(f"Error al decodificar JSON: {e}")
        return [{"expr": "error", "result": "JSON inválido", "assign": False}]