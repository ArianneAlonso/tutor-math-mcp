from beanie import Document, Link, PydanticObjectId
from pydantic import BaseModel, Field, EmailStr, field_validator
from typing import Optional, List
from uuid import UUID, uuid4

class Conversation(Document):
    title: str
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
        try:
            password_bytes = v.encode('utf-8')
        except UnicodeEncodeError:
            raise ValueError('La contraseña contiene caracteres inválidos')
        if len(password_bytes) > 72:
            raise ValueError('La contraseña es demasiado larga (límite de 72 bytes de bcrypt)')
        if len(v) < 8:
            raise ValueError('La contraseña debe tener al menos 8 caracteres')
        return v

class UserRead(BaseModel):
    id: UUID
    name: str
    email: EmailStr
    class Config:
        from_attributes = True 

class ConversationRead(BaseModel):
    id: PydanticObjectId
    title: str
    class Config:
        from_attributes = True
        json_encoders = { PydanticObjectId: str }

class Token(BaseModel):
    access_token: str
    token_type: str

class CalculateRequest(BaseModel):
    image: str
    dict_of_vars: dict = {}
