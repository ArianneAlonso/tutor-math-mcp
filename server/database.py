import os
from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie

async def init_db():
    mongo_uri = os.getenv("MONGO_URI")
    
    if not mongo_uri:
        raise ValueError("MONGO_URI no está configurada")

    client = AsyncIOMotorClient(mongo_uri)
    db_name = mongo_uri.split("/")[-1].split("?")[0]

    from models import User, Conversation

    await init_beanie(
        database=client[db_name], 
        document_models=[User, Conversation]
    )
    return f"Base de datos {db_name} inicializada"