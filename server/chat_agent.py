import os
from dotenv import load_dotenv
load_dotenv()

import google.generativeai as genai
from mcp_tools import TOOLS_FUNCTIONS, TOOLS_METADATA

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY no encontrada")

genai.configure(api_key=GEMINI_API_KEY)

gemini_tools = []
for tool_name, metadata in TOOLS_METADATA.items():
    gemini_tools.append({
        "function_declarations": [{
            "name": metadata["name"],
            "description": metadata["description"],
            "parameters": metadata["inputSchema"]
        }]
    })

SYSTEM_PROMPT = """
Eres un tutor especializado EXCLUSIVAMENTE en matemáticas de nivel secundaria, enfocado en álgebra y ecuaciones.
Tienes la capacidad de ver capturas de pantalla de una pizarra donde el usuario puede escribir ecuaciones o problemas matemáticos.
Puedes proponer actividades prácticas para que el estudiante refuerce su aprendizaje que deban ser contestadas en la pizarra con ejercicios.
Puedes proponer soluciones paso a paso y explicar conceptos matemáticos de manera clara y sencilla.}
Se proactivo y siempre intenta dar ejercicios para que el estudiante practique en la pizarra.

TUS CAPACIDADES:
- resolver_ecuacion_lineal(m, b): Para ecuaciones de la forma mx + b = 0
- resolver_ecuacion_cuadratica(a, b, c): Para ecuaciones de la forma ax² + bx + c = 0
- realizar_operacion(expresion): Para evaluar operaciones matemáticas

REGLAS ESTRICTAS:
1. SOLO MATEMÁTICAS: Si el usuario pregunta sobre cualquier tema que NO sea matemáticas, responde:
   "Lo siento, soy un tutor especializado ÚNICAMENTE en matemáticas de nivel secundaria. No puedo ayudarte con [tema]. Puedo ayudarte con ecuaciones lineales, cuadráticas y operaciones algebraicas."

2. USA TUS HERRAMIENTAS: Siempre llama a las herramientas cuando el estudiante pida resolver algo.

3. SE DIDÁCTICO: Explica los resultados paso a paso, como un profesor.

4. MANEJA ERRORES: Si una herramienta devuelve error, explícalo claramente al estudiante.

MENSAJE INICIAL: Saluda brevemente y pregunta: "¿En qué tema de matemáticas necesitas ayuda hoy?"
"""

model = genai.GenerativeModel(
    'gemini-2.5-flash',
    system_instruction=SYSTEM_PROMPT,
    tools=gemini_tools
)

def format_chat_history(history: list[dict]) -> list:
    gemini_history = []
    for msg in history:
        role = "user" if msg["sender"] == "user" else "model"
        gemini_history.append({
            "role": role,
            "parts": [{"text": msg["text"]}]
        })
    return gemini_history

async def get_tutor_response(user_message: str, history: list[dict]) -> str:
    try:
        chat_history = format_chat_history(history)
        chat = model.start_chat(history=chat_history)
        response = chat.send_message(user_message)

        if response.candidates and response.candidates[0].content.parts:
            for part in response.candidates[0].content.parts:
                if hasattr(part, 'function_call') and part.function_call:
                    function_call = part.function_call
                    tool_name = function_call.name
                    tool_args = {}

                    if hasattr(function_call, 'args'):
                        tool_args = dict(function_call.args)

                    if tool_name not in TOOLS_FUNCTIONS:
                        function_response_content = {"error": f"Herramienta '{tool_name}' no reconocida"}
                    else:
                        try:
                            tool_function = TOOLS_FUNCTIONS[tool_name]
                            tool_result = tool_function(**tool_args)
                            function_response_content = tool_result
                        except Exception as e:
                            function_response_content = {"error": f"Error ejecutando {tool_name}: {str(e)}"}

                    response = chat.send_message({
                        "function_response": {
                            "name": tool_name,
                            "response": function_response_content
                        }
                    })

        result = response.text
        return result

    except Exception as e:
        print(f"Error en get_tutor_response: {e}")
        return f"Lo siento, tuve un error interno. Intenta de nuevo. (Error: {str(e)})"