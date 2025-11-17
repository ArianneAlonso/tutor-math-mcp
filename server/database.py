import os
from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from dotenv import load_dotenv

async def init_db():
    load_dotenv()
    mongo_uri = os.getenv("MONGO_URI")
    
    if not mongo_uri:
        raise ValueError("MONGO_URI no está configurada en el archivo .env")

    client = AsyncIOMotorClient(mongo_uri)
    db_name = mongo_uri.split("/")[-1].split("?")[0]

    from models import User, Conversation

    await init_beanie(
        database=client[db_name], 
        document_models=[User, Conversation]
    )
    print(f"Beanie inicializado con la base de datos: {db_name}")