import json
import io
from google import genai
from google.genai.types import GenerateContentConfig
from PIL import Image
import base64
import logging
from dotenv import load_dotenv
import os

load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

client = genai.Client(api_key=GEMINI_API_KEY)
logging.basicConfig(level=logging.INFO)

def analyze_image(image_base64: str, dict_of_vars: dict):
    dict_of_vars_str = json.dumps(dict_of_vars)

    prompt = f"""
Se te ha dado una imagen con algunas expresiones matemáticas, ecuaciones o problemas gráficos, y necesitas resolverlos.
Aplica las reglas de derivación, álgebra y cálculo según corresponda.
Usa el siguiente diccionario de variables: {dict_of_vars_str}
Responde siempre en formato JSON válido, como una lista de objetos con las claves "expr", "result" y "assign".
NO devuelvas texto fuera del JSON. NO devuelvas explicaciones, solo JSON puro.
"""

    try:
        image_data = base64.b64decode(image_base64.split(",")[-1])
        image = Image.open(io.BytesIO(image_data))

        img_bytes = io.BytesIO()
        image.save(img_bytes, format="PNG")
        img_bytes.seek(0)

        result = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=[{
                "role": "user",
                "parts": [
                    {"text": prompt},
                    {"inline_data": {"mime_type": "image/png", "data": img_bytes.getvalue()}}
                ]
            }],
            config=GenerateContentConfig(max_output_tokens=1024)
        )

        text = result.text.strip()
        clean = text.replace("```json", "").replace("```", "").replace("`", "").strip()

        try:
            parsed = json.loads(clean)
        except json.JSONDecodeError:
            logging.error("Error al parsear la respuesta: %s", text)
            parsed = [{"expr": "error", "result": clean, "assign": False}]

        return parsed

    except Exception as e:
        logging.error(f"Error procesando imagen: {e}")
        return [{"expr": "error", "result": str(e), "assign": False}]