from beanie import Document, Link, PydanticObjectId
from pydantic import BaseModel, Field, EmailStr, field_validator
from typing import Optional, List
from uuid import UUID, uuid4

class ChatMessage(BaseModel):
    sender: str
    text: str
    image_base64: Optional[str] = None
    analysis_result: Optional[List[dict]] = None
    message_type: str = "text"

class Conversation(Document):
    title: str
    messages: List[ChatMessage] = []
    
    class Settings:
        name = "conversations"

class User(Document):
    id: UUID = Field(default_factory=uuid4)
    name: str
    email: EmailStr = Field(unique=True, index=True)
    hashed_password: str
    conversations: List[Link[Conversation]] = []
    
    class Settings:
        name = "users"

class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str

    @field_validator('password')
    @classmethod
    def validate_password(cls, v: str) -> str:
        if not v:
            raise ValueError('La contraseña no puede estar vacía')
        if len(v) < 8:
            raise ValueError('La contraseña debe tener al menos 8 caracteres')
        return v

class UserRead(BaseModel):
    id: UUID
    name: str
    email: EmailStr

class ConversationRead(BaseModel):
    id: PydanticObjectId
    title: str

class Token(BaseModel):
    access_token: str
    token_type: str

class CalculateRequest(BaseModel):
    image: str
    dict_of_vars: dict = {}
    conversation_id: Optional[str] = None

class ChatRequest(BaseModel):
    message: str
    conversation_id: Optional[str] = None
    history: List[ChatMessage] = []

class ChatResponse(BaseModel):
    status: str
    response: str
    conversation_id: Optional[str] = None