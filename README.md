# API REST de Gestión de Clientes en Capas con Asistente IA (Gemini)

Este proyecto implementa una arquitectura limpia por capas (**Controlador**, **Servicio** y **Repositorio**) exponiendo una **API REST** construida con **Flask** en Python puro. 

Incluye un módulo de **Inteligencia Artificial con Google Gemini** conectado mediante llamadas REST directas, capaz de responder consultas en lenguaje natural consumiendo **herramientas (Tools / Function Calling)** de nuestro proyecto para leer información en tiempo real desde el archivo `resources/clientes.csv`.

---

## 🏛️ Arquitectura del Proyecto

```
[ Petición HTTP (Cliente Web / Frontend / Postman / cURL) ]
                          │
         ┌────────────────┴────────────────┐
         ▼                                 ▼
[ ClienteController ]             [ GeminiController ]
  • Endpoints /api/clientes         • Endpoint /api/gemini/consulta
         │                                 │
         ▼                                 ▼
 [ ClienteService ]                 [ GeminiService ]
  • Validaciones de negocio         • Orquestador de Tools (Function Calling)
  • Búsqueda y filtrado             • Invoca ClienteService según las tools
         │                                 │
         ▼                                 ▼
[ ClienteRepository ]              [ GeminiRepository ]
  • Lectura/escritura CSV           • Peticiones REST directas a Gemini API
  • resources/clientes.csv          • Logs con ID de conversación (req/res)
```

---

## 📁 Estructura del Proyecto

```text
demo/
│
├── resources/
│   └── clientes.csv                   <- Almacenamiento CSV con datos de clientes
│
├── app/
│   ├── __init__.py
│   ├── models/
│   │   ├── __init__.py
│   │   ├── cliente.py                 <- Modelo de dominio Cliente
│   │   └── response_dto.py            <- DTO estándar de respuesta de la API
│   ├── repositories/
│   │   ├── __init__.py
│   │   ├── cliente_repository.py      <- Repositorio para persistencia en CSV
│   │   └── gemini_repository.py       <- Repositorio de llamadas REST a Gemini con logs
│   ├── services/
│   │   ├── __init__.py
│   │   ├── cliente_service.py         <- Lógica de negocio de clientes y filtros
│   │   └── gemini_service.py          <- Ciclo de Function Calling y ejecución de tools
│   └── controllers/
│       ├── __init__.py
│       ├── cliente_controller.py      <- Controlador REST para CRUD de clientes
│       └── gemini_controller.py       <- Controlador REST para consultas a la IA
│
├── main.py                            <- Punto de entrada de la aplicación web Flask
├── requirements.txt                   <- Dependencias (flask, requests, python-dotenv)
├── .env.example                       <- Plantilla de variables de entorno (GEMINI_API_KEY)
├── test_capas.py                      <- Pruebas del CRUD y arquitectura de clientes
├── test_gemini.py                     <- Pruebas del módulo de Gemini y Tools
└── README.md                          <- Documentación del proyecto
```

---

## 🚀 Instalación y Configuración

### 1. Instalar dependencias
```bash
pip install -r requirements.txt
```

### 2. Configurar la clave de Gemini
Crea un archivo `.env` en la raíz copiando la plantilla:
```bash
copy .env.example .env
```
Y asigna tu API Key obtenida de Google AI Studio:
```env
GEMINI_API_KEY=tu_api_key_aqui
GEMINI_MODEL=gemini-3.5-flash-lite
PORT=5000
```

### 3. Iniciar el servidor web REST
```bash
python main.py
```
El servidor escuchará en `http://localhost:5000`.

---

## 📡 Catálogo de Endpoints REST

| Método | Endpoint | Descripción | Códigos HTTP |
| :--- | :--- | :--- | :--- |
| **GET** | `/` | Documentación general de la API | `200` |
| **GET** | `/api/clientes` | Consultar todos los clientes | `200`, `500` |
| **GET** | `/api/clientes/<id>` | Consultar cliente específico por ID | `200`, `400`, `404` |
| **POST** | `/api/clientes` | Registrar un nuevo cliente | `201`, `400`, `500` |
| **PUT** | `/api/clientes/<id>` | Modificar un cliente existente | `200`, `400`, `404` |
| **POST** | `/api/gemini/consulta` | Consultar a la IA sobre clientes mediante Tools | `200`, `400`, `500` |

---

## 🤖 Consulta a la IA con Tools

El endpoint `/api/gemini/consulta` permite hacer preguntas en lenguaje natural sobre los clientes. La IA decide autónomamente qué herramienta local invocar:
- `listar_clientes`: Obtiene la lista completa de clientes.
- `buscar_cliente_por_id`: Busca por ID numérico/alfanumérico.
- `filtrar_clientes`: Busca por coincidencia parcial en nombre, apellido o email.

### Ejemplo de petición:
```bash
curl -X POST http://localhost:5000/api/gemini/consulta \
  -H "Content-Type: application/json" \
  -d '{
    "mensaje": "¿Cuántos clientes activos tenemos y cuáles son sus correos?",
    "conversacion_id": "mi-sesion-01"
  }'
```

### Ejemplo de respuesta (`ResponseDTO`):
```json
{
  "code": 200,
  "message": "Consulta procesada correctamente por la IA.",
  "data": {
    "conversacion_id": "mi-sesion-01",
    "mensaje": "¿Cuántos clientes activos tenemos y cuáles son sus correos?",
    "respuesta": "Actualmente hay 3 clientes activos en el sistema:\n1. Juan Perez (juan.perez@example.com)\n2. Maria Gomez (maria.gomez@example.com)\n3. Laura Rodriguez (laura.rodriguez@example.com)",
    "herramientas_utilizadas": [
      {
        "nombre": "listar_clientes",
        "argumentos": {},
        "resultado": [...]
      }
    ],
    "total_herramientas": 1
  },
  "total": null
}
```

---

## 📝 Trazabilidad y Logs Detallados

Cada llamada a la IA registra en consola bloques claramente identificados con el `conversacion_id`:
- `[IA REQUEST | CONV: <id>]`: Endpoint, headers y payload JSON exacto con las `tools` declaradas.
- `[IA RESPONSE | CONV: <id>]`: Status code y body recibido de Google Gemini.
- `[TOOL EXECUTION | CONV: <id>]`: Nombre de la función invocada y argumentos.
- `[TOOL RESULT | CONV: <id>]`: Resultado devuelto por `ClienteService` antes de reenviarlo al modelo.

---

## 🧪 Pruebas Automatizadas

```bash
# Probar endpoints del CRUD de clientes y ResponseDTO
python test_capas.py

# Probar ciclo de Function Calling, Tools y logging de Gemini
python test_gemini.py
```
