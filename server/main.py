from fastapi import FastAPI, HTTPException, Depends, status, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.responses import JSONResponse
from datetime import datetime, timedelta
from typing import List
from uuid import UUID
from contextlib import asynccontextmanager

from core import analyze_image
from database import init_db
import auth
from models import (
    User, UserCreate, UserRead, 
    Conversation, ConversationRead, 
    CalculateRequest, Token
)

from mcp_tools import (
    TOOLS_METADATA, 
    TOOLS_FUNCTIONS,
    get_temas_matematicas,
    get_contenido_area
)

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Lifespan: Iniciando servidor...")
    await init_db()
    print("Lifespan: Base de datos inicializada y lista.")
    print("="*60)
    print("SERVIDOR MCP DEL TUTOR DE MATEMÁTICAS ACTIVO")
    print("="*60)
    print(f"Endpoint MCP: http://localhost:3000/mcp")
    print(f"API REST: http://localhost:3000")
    print(f"🔧 Tools disponibles: {len(TOOLS_METADATA)}")
    for tool_name in TOOLS_METADATA.keys():
        print(f"   - {tool_name}")
    print("="*60)
    yield
    print("Lifespan: Servidor cerrándose.")

app = FastAPI(
    title="Math Draw AI + Tutor MCP", 
    description="Analizador de imágenes matemáticas con Gemini AI y Tutor MCP integrado",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3001", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/register", response_model=UserRead, status_code=status.HTTP_201_CREATED)
async def register_user(user_create: UserCreate):
    db_user = await auth.get_user_by_email(email=user_create.email)
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="El correo electrónico ya está registrado"
        )
    hashed_password = auth.get_password_hash(user_create.password)
    db_user = User(
        name=user_create.name,
        email=user_create.email,
        hashed_password=hashed_password
    )
    await db_user.insert()
    return db_user

@app.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = await auth.authenticate_user(email=form_data.username, password=form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email o contraseña incorrectos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=auth.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth.create_access_token(
        data={"sub": str(user.id)}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/users/me", response_model=UserRead)
async def read_users_me(current_user: User = Depends(auth.get_current_user)):
    return current_user

@app.get("/conversations", response_model=List[ConversationRead])
async def get_user_conversations(current_user: User = Depends(auth.get_current_user)):
    if not current_user.conversations:
        return []
    await current_user.fetch_links(User.conversations)
    return current_user.conversations

@app.get("/")
def read_root():
    return {
        "message": "Servidor activo - Math Draw AI + Tutor MCP",
        "endpoints": {
            "api": "http://localhost:3000",
            "mcp": "http://localhost:3000/mcp"
        }
    }

@app.post("/calculate", status_code=status.HTTP_200_OK)
async def calculate(
    req: CalculateRequest,
    current_user: User = Depends(auth.get_current_user)
):
    print(f"Cálculo solicitado por el usuario: {current_user.email} (ID: {current_user.id})")
    try:
        result = analyze_image(req.image, req.dict_of_vars)
        new_conv_title = f"Análisis de {datetime.now().strftime('%Y-%m-%d %H:%M')}"
        new_conv = Conversation(title=new_conv_title)
        await new_conv.insert()
        current_user.conversations.append(new_conv)
        await current_user.save() 
        print(f"Nueva conversación creada (ID: {new_conv.id}) y vinculada al usuario.")
        return {
            "status": "success", 
            "data": result, 
            "conversation_id": str(new_conv.id)
        }
    except Exception as e:
        print(f"Error en /calculate: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/mcp")
async def mcp_handler(request: Request):
    """
    Endpoint principal para el protocolo MCP (Model Context Protocol)
    Maneja todas las operaciones del servidor MCP según el estándar.
    """
    try:
        body = await request.json()
        method = body.get("method")
        
        if method == "initialize":
            return handle_initialize(body)
        elif method == "tools/list":
            return handle_tools_list()
        elif method == "tools/call":
            return handle_tools_call(body)
        elif method == "resources/list":
            return handle_resources_list()
        elif method == "resources/read":
            return handle_resources_read(body)
        elif method == "prompts/list":
            return handle_prompts_list()
        elif method == "prompts/get":
            return handle_prompts_get(body)
        else:
            return JSONResponse(
                status_code=400,
                content={
                    "jsonrpc": "2.0",
                    "error": {
                        "code": -32601,
                        "message": f"Método no soportado: {method}"
                    },
                    "id": body.get("id")
                }
            )
    except Exception as e:
        print(f"Error en MCP handler: {e}")
        return JSONResponse(
            status_code=500,
            content={
                "jsonrpc": "2.0",
                "error": {
                    "code": -32603,
                    "message": f"Error interno del servidor: {str(e)}"
                },
                "id": body.get("id", None)
            }
        )

def handle_initialize(body: dict) -> dict:
    """Maneja la inicialización del protocolo MCP"""
    return {
        "jsonrpc": "2.0",
        "result": {
            "protocolVersion": "2024-11-05",
            "capabilities": {
                "tools": {},
                "resources": {},
                "prompts": {}
            },
            "serverInfo": {
                "name": "Tutor de Matemáticas",
                "version": "1.0.0"
            }
        },
        "id": body.get("id")
    }

def handle_tools_list() -> dict:
    """Retorna la lista de herramientas disponibles"""
    tools = []
    for tool_name, metadata in TOOLS_METADATA.items():
        tools.append(metadata)
    
    return {
        "jsonrpc": "2.0",
        "result": {
            "tools": tools
        }
    }

def handle_tools_call(body: dict) -> dict:
    """Ejecuta una herramienta solicitada"""
    params = body.get("params", {})
    tool_name = params.get("name")
    arguments = params.get("arguments", {})
    
    if tool_name not in TOOLS_FUNCTIONS:
        return {
            "jsonrpc": "2.0",
            "error": {
                "code": -32602,
                "message": f"Herramienta no encontrada: {tool_name}"
            },
            "id": body.get("id")
        }
    
    try:
        tool_function = TOOLS_FUNCTIONS[tool_name]
        result = tool_function(**arguments)
        
        return {
            "jsonrpc": "2.0",
            "result": {
                "content": [
                    {
                        "type": "text",
                        "text": str(result)
                    }
                ]
            },
            "id": body.get("id")
        }
    except ValueError as e:
        return {
            "jsonrpc": "2.0",
            "error": {
                "code": -32602,
                "message": f"Error de validación: {str(e)}"
            },
            "id": body.get("id")
        }
    except Exception as e:
        return {
            "jsonrpc": "2.0",
            "error": {
                "code": -32603,
                "message": f"Error al ejecutar herramienta: {str(e)}"
            },
            "id": body.get("id")
        }

def handle_resources_list() -> dict:
    """Retorna la lista de recursos disponibles"""
    return {
        "jsonrpc": "2.0",
        "result": {
            "resources": [
                {
                    "uri": "matematicas://temas",
                    "name": "Temas de Matemáticas - Secundaria",
                    "description": "Lista completa de temas de matemáticas disponibles",
                    "mimeType": "application/json"
                },
                {
                    "uri": "matematicas://temas/{area}",
                    "name": "Contenidos de un área específica",
                    "description": "Contenidos detallados de un área de matemáticas",
                    "mimeType": "application/json"
                }
            ]
        }
    }

def handle_resources_read(body: dict) -> dict:
    """Lee un recurso específico"""
    params = body.get("params", {})
    uri = params.get("uri", "")
    
    if uri == "matematicas://temas":
        content = get_temas_matematicas()
    elif uri.startswith("matematicas://temas/"):
        area = uri.split("/")[-1]
        content = get_contenido_area(area)
    else:
        return {
            "jsonrpc": "2.0",
            "error": {
                "code": -32602,
                "message": f"Recurso no encontrado: {uri}"
            },
            "id": body.get("id")
        }
    
    return {
        "jsonrpc": "2.0",
        "result": {
            "contents": [
                {
                    "uri": uri,
                    "mimeType": "application/json",
                    "text": str(content)
                }
            ]
        },
        "id": body.get("id")
    }

def handle_prompts_list() -> dict:
    """Retorna la lista de prompts disponibles"""
    return {
        "jsonrpc": "2.0",
        "result": {
            "prompts": [
                {
                    "name": "tutor_matematicas",
                    "description": "Configura al asistente como tutor de matemáticas personalizado",
                    "arguments": [
                        {
                            "name": "nivel_estudiante",
                            "description": "Nivel del estudiante (principiante, medio, avanzado)",
                            "required": False
                        }
                    ]
                },
                {
                    "name": "resolver_problema",
                    "description": "Configura una sesión enfocada en resolver un tipo específico de problema",
                    "arguments": [
                        {
                            "name": "tipo_problema",
                            "description": "Tipo de problema (ecuacion_lineal, ecuacion_cuadratica, operacion_general)",
                            "required": True
                        }
                    ]
                }
            ]
        }
    }

def handle_prompts_get(body: dict) -> dict:
    """Retorna un prompt específico"""
    params = body.get("params", {})
    name = params.get("name")
    arguments = params.get("arguments", {})
    
    if name == "tutor_matematicas":
        nivel = arguments.get("nivel_estudiante", "medio")
        prompt_text = f"""
Actúa como un tutor experto de matemáticas de nivel secundaria, especializado en álgebra y ecuaciones.

Nivel del estudiante: {nivel}

TUS CAPACIDADES:
- Puedes resolver ecuaciones lineales (mx + b = 0)
- Puedes resolver ecuaciones cuadráticas (ax² + bx + c = 0)
- Puedes realizar operaciones matemáticas generales

REGLAS IMPORTANTES:
1. Siempre explica los conceptos de manera clara y adaptada al nivel "{nivel}"
2. Cuando el estudiante te pida resolver una ecuación, DEBES usar las herramientas disponibles
3. Después de usar una herramienta, explica los pasos de manera didáctica
4. Si la consulta NO es sobre matemáticas, explica amablemente que solo puedes ayudar con temas matemáticos
5. Fomenta el aprendizaje preguntando al estudiante qué parte no entiende
6. Usa ejemplos cuando sea necesario para aclarar conceptos

ESTILO DE ENSEÑANZA:
- Paciente y motivador
- Usa emojis ocasionalmente para hacer la interacción más amigable (📝, ✅, 🤔)
- Reformula las explicaciones si el estudiante no entiende
- Siempre verifica que el estudiante haya comprendido antes de avanzar

Pregúntale al estudiante: "¿En qué tema de matemáticas necesitas ayuda hoy?" y continúa desde allí.
"""
    elif name == "resolver_problema":
        tipo = arguments.get("tipo_problema", "ecuacion_lineal")
        instrucciones = {
            "ecuacion_lineal": "ecuaciones lineales de la forma mx + b = 0",
            "ecuacion_cuadratica": "ecuaciones cuadráticas de la forma ax² + bx + c = 0",
            "operacion_general": "operaciones matemáticas y cálculos numéricos"
        }
        tipo_desc = instrucciones.get(tipo, "problemas matemáticos")
        
        prompt_text = f"""
Eres un tutor especializado en resolver {tipo_desc}.

PROCESO DE RESOLUCIÓN:
1. Primero, identifica claramente los datos del problema
2. Usa la herramienta correspondiente para resolver
3. Explica cada paso de la solución de manera detallada
4. Verifica el resultado
5. Pregunta al estudiante si tiene dudas sobre algún paso

Espera a que el estudiante te presente su problema de {tipo_desc}.
"""
    else:
        return {
            "jsonrpc": "2.0",
            "error": {
                "code": -32602,
                "message": f"Prompt no encontrado: {name}"
            },
            "id": body.get("id")
        }
    
    return {
        "jsonrpc": "2.0",
        "result": {
            "description": f"Prompt: {name}",
            "messages": [
                {
                    "role": "user",
                    "content": {
                        "type": "text",
                        "text": prompt_text
                    }
                }
            ]
        },
        "id": body.get("id")
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="localhost", port=3000, reload=True)