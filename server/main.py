from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from core import analyze_image

app = FastAPI(title="Math Draw AI", description="Analizador de imágenes matemáticas con Gemini AI")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class CalculateRequest(BaseModel):
    image: str
    dict_of_vars: dict = {}

@app.get("/")
def read_root():
    return {"message": "Servidor activo - Math Draw AI"}

@app.post("/calculate")
def calculate(req: CalculateRequest):
    """
    Endpoint principal que recibe una imagen base64 y variables,
    y devuelve las expresiones matemáticas analizadas.
    """
    try:
        result = analyze_image(req.image, req.dict_of_vars)
        return {"status": "success", "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="localhost", port=3000, reload=True)
