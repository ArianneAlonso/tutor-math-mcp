from pydantic import BaseModel, Field
from enum import Enum
import math
import re
from typing import List

class TipoEcuacion(str, Enum):
    lineal = "lineal"
    cuadratica = "cuadratica"

class SolucionLineal(BaseModel):
    tipo: TipoEcuacion = Field(default=TipoEcuacion.lineal)
    ecuacion_original: str = Field(description="Ecuación tal como fue ingresada")
    solucion: float = Field(description="Valor de x que satisface la ecuación")
    pasos: List[str] = Field(description="Pasos detallados de la solución")
    verificacion: str = Field(description="Verificación de la solución")

class SolucionCuadratica(BaseModel):
    tipo: TipoEcuacion = Field(default=TipoEcuacion.cuadratica)
    ecuacion_original: str = Field(description="Ecuación tal como fue ingresada")
    a: float = Field(description="Coeficiente a de ax² + bx + c = 0")
    b: float = Field(description="Coeficiente b de ax² + bx + c = 0")
    c: float = Field(description="Coeficiente c de ax² + bx + c = 0")
    discriminante: float = Field(description="Valor del discriminante (b² - 4ac)")
    soluciones: List[float] = Field(description="Lista de soluciones reales")
    tipo_solucion: str = Field(description="Tipo de soluciones")
    pasos: List[str] = Field(description="Pasos detallados de la solución")

class ResultadoOperacion(BaseModel):
    expresion_original: str = Field(description="Expresión matemática ingresada")
    resultado: float = Field(description="Resultado numérico de la operación")
    pasos: List[str] = Field(description="Explicación paso a paso del cálculo")

def resolver_ecuacion_lineal(m: float, b: float) -> dict:
    if m == 0:
        raise ValueError("El coeficiente 'm' no puede ser cero")
    
    solucion = -b / m
    
    pasos = [
        f"Ecuación: {m}x + {b} = 0",
        f"Despejamos x: {m}x = {-b}",
        f"Dividimos por {m}: x = {-b}/{m}",
        f"Resultado: x = {solucion:.4f}"
    ]
    
    verificacion_valor = m * solucion + b
    verificacion = f"Verificación: {m}({solucion:.4f}) + {b} = {verificacion_valor:.6f} ≈ 0 ✓"
    
    resultado = SolucionLineal(
        ecuacion_original=f"{m}x + {b} = 0",
        solucion=solucion,
        pasos=pasos,
        verificacion=verificacion
    )
    
    return resultado.model_dump()

def resolver_ecuacion_cuadratica(a: float, b: float, c: float) -> dict:
    if a == 0:
        raise ValueError("El coeficiente 'a' no puede ser cero")
    
    discriminante = b**2 - 4*a*c
    
    pasos = [
        f"Ecuación: {a}x² + {b}x + {c} = 0",
        f"Coeficientes: a={a}, b={b}, c={c}",
        f"Discriminante: Δ = {b}² - 4({a})({c}) = {discriminante:.4f}"
    ]
    
    soluciones = []
    tipo_solucion = ""
    
    if discriminante > 0:
        x1 = (-b + math.sqrt(discriminante)) / (2*a)
        x2 = (-b - math.sqrt(discriminante)) / (2*a)
        soluciones = [x1, x2]
        tipo_solucion = "Dos soluciones reales distintas"
        pasos.extend([
            f"x₁ = (-b + √Δ)/2a = ({-b} + √{discriminante:.4f})/{2*a} = {x1:.4f}",
            f"x₂ = (-b - √Δ)/2a = ({-b} - √{discriminante:.4f})/{2*a} = {x2:.4f}"
        ])
    elif discriminante == 0:
        x = -b / (2*a)
        soluciones = [x]
        tipo_solucion = "Una solución real doble"
        pasos.append(f"x = -b/2a = {-b}/{2*a} = {x:.4f}")
    else:
        tipo_solucion = "Sin soluciones reales"
        pasos.append("Δ < 0: No hay soluciones reales")
    
    resultado = SolucionCuadratica(
        ecuacion_original=f"{a}x² + {b}x + {c} = 0",
        a=a,
        b=b,
        c=c,
        discriminante=discriminante,
        soluciones=soluciones,
        tipo_solucion=tipo_solucion,
        pasos=pasos
    )
    
    return resultado.model_dump()

def realizar_operacion(expresion: str) -> dict:
    expresion_original = expresion
    expresion = expresion.strip().replace(" ", "")
    
    caracteres_permitidos = re.compile(r'^[0-9+\-*/().^a-z,]+$', re.IGNORECASE)
    if not caracteres_permitidos.match(expresion):
        raise ValueError(f"Caracteres no permitidos en: '{expresion}'")
    
    expresion_eval = expresion.replace("^", "**")
    namespace_seguro = {
        "sqrt": math.sqrt,
        "sin": math.sin,
        "cos": math.cos,
        "tan": math.tan,
        "log": math.log10,
        "pi": math.pi,
        "e": math.e,
        "__builtins__": {}
    }
    
    resultado = eval(expresion_eval, namespace_seguro)
    
    pasos = [
        f"Expresión: {expresion_original}",
        f"Procesada: {expresion_eval}",
        f"Resultado: {resultado:.6f}"
    ]
    
    resultado_obj = ResultadoOperacion(
        expresion_original=expresion_original,
        resultado=float(resultado),
        pasos=pasos
    )
    
    return resultado_obj.model_dump()

TOOLS_METADATA = {
    "resolver_ecuacion_lineal": {
        "name": "resolver_ecuacion_lineal",
        "description": "Resuelve ecuaciones lineales de la forma mx + b = 0",
        "inputSchema": {
            "type": "object",
            "properties": {
                "m": {"type": "number", "description": "Coeficiente de x (no puede ser cero)"},
                "b": {"type": "number", "description": "Término independiente"}
            },
            "required": ["m", "b"]
        }
    },
    "resolver_ecuacion_cuadratica": {
        "name": "resolver_ecuacion_cuadratica",
        "description": "Resuelve ecuaciones cuadráticas de la forma ax² + bx + c = 0",
        "inputSchema": {
            "type": "object",
            "properties": {
                "a": {"type": "number", "description": "Coeficiente cuadrático (no puede ser cero)"},
                "b": {"type": "number", "description": "Coeficiente lineal"},
                "c": {"type": "number", "description": "Término independiente"}
            },
            "required": ["a", "b", "c"]
        }
    },
    "realizar_operacion": {
        "name": "realizar_operacion",
        "description": "Evalúa expresiones matemáticas con operaciones básicas y funciones",
        "inputSchema": {
            "type": "object",
            "properties": {
                "expresion": {"type": "string", "description": "Expresión matemática a evaluar"}
            },
            "required": ["expresion"]
        }
    }
}

TOOLS_FUNCTIONS = {
    "resolver_ecuacion_lineal": resolver_ecuacion_lineal,
    "resolver_ecuacion_cuadratica": resolver_ecuacion_cuadratica,
    "realizar_operacion": realizar_operacion
}