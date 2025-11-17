from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
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

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Lifespan: Iniciando servidor...")
    await init_db()
    print("Lifespan: Base de datos inicializada y lista.")
    yield
    print("Lifespan: Servidor cerrándose.")

app = FastAPI(
    title="Math Draw AI", 
    description="Analizador de imágenes matemáticas con Gemini AI (MongoDB)",
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
    return {"message": "Servidor activo - Math Draw AI (MongoDB)"}

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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="localhost", port=3000, reload=True)
