# Tutor de Matemáticas — MCP (Model Context Protocol)

**Trabajo Práctico Final — "Desarrollando una Solución de IA Aplicada"**

**Materia:** S.A.C. Modelos y Aplicaciones de la Inteligencia Artificial

## 1. **Tutor de Matemáticas (MCP)** — Agente tutor basado en IA para alumnos de secundaria, especializado en álgebra y resolución de ecuaciones.

## 2. Descripción del problema
Los estudiantes de nivel secundario necesitan apoyo personalizado para comprender álgebra y resolver ecuaciones lineales y cuadráticas. Este proyecto entrega un tutor virtual que **explica** los pasos, **resuelve** problemas cuando el usuario lo solicita y **propone ejercicios** para practicar usando una pizarra visual.

**Público objetivo:** estudiantes de secundaria y docentes que quieran un asistente para prácticas y explicaciones de álgebra.

## 3. Demo (GIF)

## 4. Stack tecnológico
- Python 3.10+
- FastAPI — backend y endpoints REST
- Uvicorn — servidor ASGI
- Beanie + Motor — ODM/driver para MongoDB (async)
- Pydantic — validación de modelos
- React + Vite — frontend (client)
- Gemini SDK / Google Generative AI (`google.generativeai`) — integración con el modelo generativo
- PIL (Pillow) — manipulación y decodificación de imágenes
- passlib, jose, OAuth2 — autenticación y hashing de contraseñas
- Otros: `python-dotenv`, `uvicorn`, `motor`, `beanie`, `pydantic`, `pytest` (opcional)

## 5. Requisitos previos
- Node.js (v16+) y npm
- Python 3.10 o superior
- MongoDB (local o URL Atlas)
- Variables de entorno en un archivo `.env`:
  - `MONGO_URI` — cadena de conexión a MongoDB
  - `SECRET_KEY` — clave para JWT
  - `GEMINI_API_KEY` — API key para Gemini SDK

## 6. Instalación (clonar e instalar)
```bash
# Clonar
git clone https://github.com/ArianneAlonso/tutor-math-mcp.git
cd <repo>
```

### Frontend (client)
```bash
cd client
npm install
npm run dev
# El frontend correrá en http://localhost:5173 por defecto (Vite)
```

### Backend (server)
```bash
cd server
# Crear entorno virtual
python -m venv env
# Windows (PowerShell)
.\env\Scripts\Activate.ps1
# Windows (cmd.exe)
.\env\Scripts\activate
# macOS / Linux
source env/bin/activate

# Instalar dependencias
pip install -r requirements.txt

# Correr server (desarrollo)
uvicorn main:app --reload --host 0.0.0.0 --port 3000
```

## 7. Uso / Ejecución
1. Levantar MongoDB (local o configurar `MONGO_URI`).
2. Levantar frontend y backend según instrucciones anteriores.
3. Abrir la app en el navegador (frontend).
4. Registrar un usuario (endpoint `/register`) o usar la UI.
5. Iniciar sesión para obtener token (endpoint `/token`).
6. Crear o seleccionar una conversación y usar:
   - Chat: `/chat` — envía mensajes al agente tutor.
   - Pizarra: `/calculate` — enviar imagen base64 de la pizarra para análisis y cálculo.
   - MCP JSON-RPC: `/mcp` — para listar herramientas, inicializar protocolo y llamarlas.

## 8. Endpoints importantes
- `POST /register` — registrar usuario
- `POST /token` — login (OAuth2 Password)
- `GET /users/me` — info del usuario actual
- `POST /conversations/new` — crear conversación
- `DELETE /conversations/{conversation_id}` — eliminar conversación
- `GET /conversations` — listar conversaciones del usuario
- `POST /chat` — enviar mensaje al tutor (requiere token)
- `POST /calculate` — analizar pizarra (imagen base64)
- `POST /mcp` — handler MCP (initialize, tools/list, tools/call)

## 9. Documentación de las herramientas (Tools)
Todas las herramientas están documentadas y expuestas para el protocolo MCP. Si se utiliza salida estructurada (objetos JSON), también están documentadas.

### 1) `resolver_ecuacion_lineal(m: float, b: float)`
- **Descripción:** Resuelve ecuaciones de la forma `m x + b = 0`.
- **Argumentos:**
  - `m` (number) — coeficiente de `x` (no puede ser 0).
  - `b` (number) — término independiente.
- **Salida (JSON):** `SolucionLineal` con campos:
  - `tipo`: "lineal"
  - `ecuacion_original`: string
  - `solucion`: float
  - `pasos`: lista de strings (paso a paso)
  - `verificacion`: string
- **Errores posibles:**
  - `ValueError` si `m == 0` (devuelve error de validación con código -32602 en MCP).

### 2) `resolver_ecuacion_cuadratica(a: float, b: float, c: float)`
- **Descripción:** Resuelve `a x² + b x + c = 0`.
- **Argumentos:**
  - `a` (number) — coeficiente cuadrático (no puede ser 0)
  - `b` (number)
  - `c` (number)
- **Salida (JSON):** `SolucionCuadratica` con campos:
  - `tipo`: "cuadratica"
  - `ecuacion_original`, `a`, `b`, `c`, `discriminante`, `soluciones`, `tipo_solucion`, `pasos`
- **Errores posibles:**
  - `ValueError` si `a == 0`.

### 3) `realizar_operacion(expresion: str)`
- **Descripción:** Evalúa expresiones aritméticas/algebraicas simples, soportando `^` como potencia y funciones `sqrt`, `sin`, `cos`, etc.
- **Argumentos:**
  - `expresion` (string) — la expresión a evaluar.
- **Salida (JSON):** `ResultadoOperacion` con campos:
  - `expresion_original`, `resultado` (float), `pasos` (explicación paso a paso).
- **Seguridad y validación:** la función filtra caracteres mediante regex y usa un `namespace_seguro` con funciones permitidas. Si la expresión contiene caracteres no permitidos, lanza `ValueError`.

## 10. Manejo de errores
El servidor captura excepciones y las transforma en respuestas JSON-RPC o HTTP con códigos apropiados.
- En `/mcp`:
  - Herramienta no encontrada → error JSON-RPC con `code: -32602`.
  - Error de validación (ej: `a == 0`) → devuelve `code: -32602` y mensaje claro.
  - Error interno → devuelve `code: -32603` con mensaje del servidor.
- En endpoints REST:
  - Excepciones convertidas a `HTTPException` con `status_code` y `detail` legible.

En el flujo con Gemini, si la herramienta devuelve un error, el agente lo muestra al usuario y puede sugerir reintentar con otros argumentos.

## 11. Restricciones de dominio y reglas del agente
El agente sigue estrictamente las reglas solicitadas por el enunciado:
- **Sólo matemáticas de nivel secundaria.** Si el usuario pregunta por algo fuera de ese dominio, el agente responde con un mensaje que explica que no puede ayudar en ese tema y ofrece ejemplos de lo que sí puede hacer.
- **Uso obligatorio de herramientas**: cuando el usuario pide resolver una ecuación o realizar un cálculo, el agente debe invocar la herramienta adecuada.
- **Botón de limpieza**: la interfaz incluye un botón para limpiar el chat e iniciar una nueva conversación (implementado en el frontend). El endpoint `DELETE /conversations/{id}` permite borrar una conversación en el backend.

## 12. Cumplimiento con MCP (Model Context Protocol)
- `POST /mcp` implementa los métodos mínimos requeridos:
  - `initialize` — devuelve `protocolVersion`, `capabilities` y `serverInfo`.
  - `tools/list` — lista las herramientas disponibles (metadata).
  - `tools/call` — permite ejecutar una herramienta con `arguments` y devuelve la respuesta estructurada o un error JSON-RPC.


## 13. Generar `requirements.txt`
Esto es por si usas el repo y necesitas instalar otras dependencias, y actualizar tu txt:

Desde el entorno virtual activado:
```bash
pip freeze > requirements.txt
```