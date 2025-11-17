from fastapi import FastAPI, HTTPException, Depends, status, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.responses import JSONResponse
from datetime import datetime, timedelta
from typing import List
from uuid import UUID
from contextlib import asynccontextmanager
import json

from core import analyze_image
from database import init_db
import auth
from models import (
    User, UserCreate, UserRead, 
    Conversation, ConversationRead, 
    CalculateRequest, Token,
    ChatRequest, ChatResponse, ChatMessage
)
from chat_agent import get_tutor_response
from mcp_tools import TOOLS_METADATA, TOOLS_FUNCTIONS

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Iniciando servidor...")
    await init_db()
    print("Servidor MCP del Tutor de Matemáticas activo")
    yield
    print("Servidor cerrándose.")

app = FastAPI(
    title="Tutor de Matemáticas MCP",
    description="Agente tutor especializado en matemáticas de nivel secundaria",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000", "*"],
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

@app.post("/conversations/new")
async def create_conversation(current_user: User = Depends(auth.get_current_user)):
    title = f"Conversación {datetime.now().strftime('%Y-%m-%d %H:%M')}"
    new_conv = Conversation(title=title)
    await new_conv.insert()
    
    current_user.conversations.append(new_conv)
    await current_user.save()
    
    return {"conversation_id": str(new_conv.id), "title": title}

@app.delete("/conversations/{conversation_id}")
async def delete_conversation(conversation_id: str, current_user: User = Depends(auth.get_current_user)):
    conversation = await Conversation.get(conversation_id)
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversación no encontrada")
    
    await conversation.delete()
    current_user.conversations = [conv for conv in current_user.conversations if str(conv.id) != conversation_id]
    await current_user.save()
    
    return {"message": "Conversación eliminada"}

@app.post("/calculate", status_code=status.HTTP_200_OK)
async def calculate(
    req: CalculateRequest,
    current_user: User = Depends(auth.get_current_user)
):
    print(f"Cálculo de pizarra solicitado por el usuario: {current_user.email}")
    try:
        result = analyze_image(req.image, req.dict_of_vars)
        
        new_conv_title = f"Análisis Pizarra {datetime.now().strftime('%Y-%m-%d %H:%M')}"
        new_conv = Conversation(title=new_conv_title)
        await new_conv.insert()
        
        current_user.conversations.append(new_conv)
        await current_user.save() 
        
        return {
            "status": "success", 
            "data": result, 
            "conversation_id": str(new_conv.id)
        }
    except Exception as e:
        print(f"Error en /calculate: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/chat", response_model=ChatResponse)
async def chat_handler(
    req: ChatRequest,
    current_user: User = Depends(auth.get_current_user)
):
    try:
        response_text = await get_tutor_response(req.message, [msg.model_dump() for msg in req.history])
        
        if req.conversation_id:
            conversation = await Conversation.get(req.conversation_id)
            if conversation:
                conversation.messages.append(ChatMessage(sender="user", text=req.message))
                conversation.messages.append(ChatMessage(sender="ai", text=response_text))
                await conversation.save()
        
        return ChatResponse(
            status="success",
            response=response_text,
            conversation_id=req.conversation_id
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
def read_root():
    return {
        "message": "Tutor de Matemáticas MCP - Servidor Activo",
        "endpoints": {
            "api": "/",
            "chat": "/chat",
            "calculate": "/calculate",
            "mcp": "/mcp",
            "auth": "/token"
        }
    }

@app.post("/mcp")
async def mcp_handler(request: Request):
    try:
        body = await request.json()
        method = body.get("method")
        
        if method == "initialize":
            return {
                "jsonrpc": "2.0",
                "result": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {"tools": {}, "resources": {}, "prompts": {}},
                    "serverInfo": {"name": "Tutor de Matemáticas", "version": "1.0.0"}
                },
                "id": body.get("id")
            }
        elif method == "tools/list":
            tools = []
            for tool_name, metadata in TOOLS_METADATA.items():
                tools.append(metadata)
            return {
                "jsonrpc": "2.0",
                "result": {"tools": tools},
                "id": body.get("id")
            }
        elif method == "tools/call":
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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="localhost", port=3000, reload=True)