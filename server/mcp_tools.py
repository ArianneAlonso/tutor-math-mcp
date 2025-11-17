from pydantic import BaseModel, Field
from enum import Enum
import math
import re
from typing import List

class TipoEcuacion(str, Enum):
    lineal = "Ecuación Lineal"
    cuadratica = "Ecuación Cuadrática"

class SolucionLineal(BaseModel):
    """Modelo de respuesta para ecuaciones lineales"""
    tipo: TipoEcuacion = Field(
        default=TipoEcuacion.lineal,
        description="Tipo de ecuación resuelta"
    )
    ecuacion_original: str = Field(description="Ecuación tal como fue ingresada")
    solucion: float = Field(description="Valor de x que satisface la ecuación")
    pasos: List[str] = Field(description="Pasos detallados de la solución")
    verificacion: str = Field(description="Verificación de la solución")

class SolucionCuadratica(BaseModel):
    """Modelo de respuesta para ecuaciones cuadráticas"""
    tipo: TipoEcuacion = Field(
        default=TipoEcuacion.cuadratica,
        description="Tipo de ecuación resuelta"
    )
    ecuacion_original: str = Field(description="Ecuación tal como fue ingresada")
    a: float = Field(description="Coeficiente a de ax² + bx + c = 0")
    b: float = Field(description="Coeficiente b de ax² + bx + c = 0")
    c: float = Field(description="Coeficiente c de ax² + bx + c = 0")
    discriminante: float = Field(description="Valor del discriminante (b² - 4ac)")
    soluciones: List[float] = Field(description="Lista de soluciones reales")
    tipo_solucion: str = Field(description="Tipo: dos reales, una real doble, o sin soluciones reales")
    pasos: List[str] = Field(description="Pasos detallados de la solución")

class ResultadoOperacion(BaseModel):
    """Modelo de respuesta para operaciones matemáticas generales"""
    expresion_original: str = Field(description="Expresión matemática ingresada")
    resultado: float = Field(description="Resultado numérico de la operación")
    pasos: List[str] = Field(description="Explicación paso a paso del cálculo")

def resolver_ecuacion_lineal(m: float, b: float) -> dict:
    """
    Resuelve una ecuación lineal de la forma mx + b = 0
    
    Args:
        m: Coeficiente de x (pendiente). No puede ser cero.
        b: Término independiente (ordenada al origen)
    
    Returns:
        dict con la solución completa y pasos explicativos
    
    Raises:
        ValueError: Si m = 0 (no es una ecuación lineal válida)
    """
    try:
        if m == 0:
            raise ValueError("El coeficiente 'm' no puede ser cero. La ecuación 0x + b = 0 no es lineal.")
        
        solucion = -b / m
        
        pasos = [
            f"Ecuación dada: {m}x + {b} = 0",
            f"Despejamos x: {m}x = {-b}",
            f"Dividimos ambos lados por {m}: x = {-b}/{m}",
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
    
    except ValueError as e:
        raise ValueError(f"Error al resolver ecuación lineal: {str(e)}")
    except Exception as e:
        raise Exception(f"Error inesperado: {str(e)}")


def resolver_ecuacion_cuadratica(a: float, b: float, c: float) -> dict:
    """
    Resuelve una ecuación cuadrática de la forma ax² + bx + c = 0 usando la fórmula cuadrática
    
    Args:
        a: Coeficiente cuadrático (debe ser diferente de cero)
        b: Coeficiente lineal
        c: Término independiente
    
    Returns:
        dict con todas las soluciones y pasos explicativos
    
    Raises:
        ValueError: Si a = 0 (no es una ecuación cuadrática)
    """
    try:
        if a == 0:
            raise ValueError("El coeficiente 'a' no puede ser cero. Si a=0, use resolver_ecuacion_lineal.")
        discriminante = b**2 - 4*a*c
        
        pasos = [
            f"Ecuación dada: {a}x² + {b}x + {c} = 0",
            f"Identificamos: a = {a}, b = {b}, c = {c}",
            f"Calculamos el discriminante: Δ = b² - 4ac = {b}² - 4({a})({c})",
            f"Δ = {discriminante:.4f}"
        ]
        
        soluciones = []
        tipo_solucion = ""
        
        if discriminante > 0:
            x1 = (-b + math.sqrt(discriminante)) / (2*a)
            x2 = (-b - math.sqrt(discriminante)) / (2*a)
            soluciones = [x1, x2]
            tipo_solucion = "Dos soluciones reales distintas"
            pasos.extend([
                f"Como Δ > 0, hay dos soluciones reales:",
                f"x₁ = (-b + √Δ) / 2a = ({-b} + √{discriminante:.4f}) / {2*a} = {x1:.4f}",
                f"x₂ = (-b - √Δ) / 2a = ({-b} - √{discriminante:.4f}) / {2*a} = {x2:.4f}"
            ])
        
        elif discriminante == 0:
            x = -b / (2*a)
            soluciones = [x]
            tipo_solucion = "Una solución real doble (raíz repetida)"
            pasos.extend([
                f"Como Δ = 0, hay una solución real doble:",
                f"x = -b / 2a = {-b} / {2*a} = {x:.4f}"
            ])
        
        else:
            soluciones = []
            tipo_solucion = "Sin soluciones reales (dos soluciones complejas conjugadas)"
            pasos.append(f"Como Δ < 0, no hay soluciones reales. Las soluciones son complejas.")
        
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
    
    except ValueError as e:
        raise ValueError(f"Error al resolver ecuación cuadrática: {str(e)}")
    except Exception as e:
        raise Exception(f"Error inesperado: {str(e)}")


def realizar_operacion(expresion: str) -> dict:
    """
    Evalúa una expresión matemática simple con operaciones básicas y funciones comunes.
    Soporta: +, -, *, /, ^(potencia), sqrt(), sin(), cos(), tan(), log()
    
    Args:
        expresion: Expresión matemática a evaluar (ej: "2*3 + 5", "sqrt(16)", "2^3")
    
    Returns:
        dict con el resultado y pasos de cálculo
    
    Raises:
        ValueError: Si la expresión contiene caracteres no permitidos o es inválida
    """
    try:
        expresion_original = expresion
        expresion = expresion.strip().replace(" ", "")
        caracteres_permitidos = re.compile(r'^[0-9+\-*/().^a-z,]+$', re.IGNORECASE)
        if not caracteres_permitidos.match(expresion):
            raise ValueError(f"La expresión contiene caracteres no permitidos: '{expresion}'")
        expresion_eval = expresion.replace("^", "**")
        namespace_seguro = {
            "sqrt": math.sqrt,
            "sin": math.sin,
            "cos": math.cos,
            "tan": math.tan,
            "log": math.log,
            "log10": math.log10,
            "exp": math.exp,
            "pi": math.pi,
            "e": math.e,
            "__builtins__": {}
        }
        resultado = eval(expresion_eval, namespace_seguro)
        
        pasos = [
            f"Expresión original: {expresion_original}",
            f"Expresión procesada: {expresion_eval}",
            f"Evaluación paso a paso:",
            f"→ Resultado final: {resultado:.6f}"
        ]
        
        resultado_obj = ResultadoOperacion(
            expresion_original=expresion_original,
            resultado=float(resultado),
            pasos=pasos
        )
        
        return resultado_obj.model_dump()
    
    except ZeroDivisionError:
        raise ValueError("Error: División por cero detectada")
    except NameError as e:
        raise ValueError(f"Error: Función o variable no reconocida: {str(e)}")
    except SyntaxError:
        raise ValueError(f"Error de sintaxis en la expresión: '{expresion}'")
    except Exception as e:
        raise Exception(f"Error al evaluar la expresión: {str(e)}")

TEMAS_MATEMATICAS = {
    "Álgebra Básica": [
        "Operaciones con números reales",
        "Propiedades de las operaciones",
        "Ecuaciones lineales",
        "Sistemas de ecuaciones"
    ],
    "Ecuaciones Cuadráticas": [
        "Forma estándar ax² + bx + c = 0",
        "Fórmula cuadrática",
        "Discriminante y tipos de soluciones",
        "Factorización de ecuaciones cuadráticas"
    ],
    "Funciones": [
        "Concepto de función",
        "Funciones lineales y cuadráticas",
        "Dominio y rango",
        "Gráficas de funciones"
    ],
    "Geometría": [
        "Teorema de Pitágoras",
        "Áreas y perímetros",
        "Volúmenes de cuerpos geométricos",
        "Teoremas básicos de triángulos"
    ]
}

def get_temas_matematicas() -> dict:
    """
    Retorna la lista completa de temas de matemáticas de nivel secundaria
    que el tutor puede ayudar a resolver.
    """
    return TEMAS_MATEMATICAS


def get_contenido_area(area: str) -> list:
    """
    Retorna los contenidos específicos de un área de matemáticas.
    
    Args:
        area: Nombre del área (ej: "Álgebra Básica", "Ecuaciones Cuadráticas")
    """
    return TEMAS_MATEMATICAS.get(area, [])

TOOLS_METADATA = {
    "resolver_ecuacion_lineal": {
        "name": "resolver_ecuacion_lineal",
        "description": "Resuelve una ecuación lineal de la forma mx + b = 0",
        "inputSchema": {
            "type": "object",
            "properties": {
                "m": {
                    "type": "number",
                    "description": "Coeficiente de x (pendiente). No puede ser cero."
                },
                "b": {
                    "type": "number",
                    "description": "Término independiente (ordenada al origen)"
                }
            },
            "required": ["m", "b"]
        }
    },
    "resolver_ecuacion_cuadratica": {
        "name": "resolver_ecuacion_cuadratica",
        "description": "Resuelve una ecuación cuadrática de la forma ax² + bx + c = 0 usando la fórmula cuadrática",
        "inputSchema": {
            "type": "object",
            "properties": {
                "a": {
                    "type": "number",
                    "description": "Coeficiente cuadrático (debe ser diferente de cero)"
                },
                "b": {
                    "type": "number",
                    "description": "Coeficiente lineal"
                },
                "c": {
                    "type": "number",
                    "description": "Término independiente"
                }
            },
            "required": ["a", "b", "c"]
        }
    },
    "realizar_operacion": {
        "name": "realizar_operacion",
        "description": "Evalúa una expresión matemática simple. Soporta: +, -, *, /, ^(potencia), sqrt(), sin(), cos(), tan(), log()",
        "inputSchema": {
            "type": "object",
            "properties": {
                "expresion": {
                    "type": "string",
                    "description": "Expresión matemática a evaluar (ej: '2*3 + 5', 'sqrt(16)', '2^3')"
                }
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