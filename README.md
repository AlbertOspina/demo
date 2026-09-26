# API REST de Gestión de Clientes en Capas (Python + Flask)

Este proyecto implementa una arquitectura limpia por capas (**Controlador**, **Servicio** y **Repositorio**) exponiendo una **API REST**. No cuenta con menús de consola interactivos; todas las operaciones se realizan mediante peticiones HTTP.

Los datos se leen y persisten en un archivo CSV ubicado en `resources/clientes.csv`.

---

## 🏛️ Arquitectura del Proyecto

El flujo de una petición HTTP sigue el principio de separación de responsabilidades:

```
[ Petición HTTP (Cliente Web / Frontend / Postman / cURL) ]
                          │
                          ▼
        [ Capa Controlador (ClienteController) ]
  • Enrutamiento REST (/api/clientes).
  • Extrae parámetros y payloads JSON (request.get_json()).
  • Convierte respuestas a formato JSON con códigos HTTP (200, 201, 400, 404, 500).
                          │
                          ▼
          [ Capa Servicio (ClienteService) ]
  • Validación de datos (formato de email, campos requeridos).
  • Reglas de negocio (unicidad de email e IDs, existencia de registros).
  • Desacoplado del protocolo web (lanza excepciones de dominio).
                          │
                          ▼
       [ Capa Repositorio (ClienteRepository) ]
  • Lee y escribe en el archivo CSV (`resources/clientes.csv`).
  • Mapea datos hacia y desde la entidad `Cliente`.
  • Generación de IDs secuenciales.
```

---

## 📁 Estructura del Proyecto

```text
demo/
│
├── resources/
│   └── clientes.csv                   <- Almacenamiento CSV con datos iniciales
│
├── app/
│   ├── __init__.py
│   ├── models/
│   │   ├── __init__.py
│   │   └── cliente.py                 <- Modelo de dominio Cliente
│   ├── repositories/
│   │   ├── __init__.py
│   │   └── cliente_repository.py      <- Capa de persistencia CSV
│   ├── services/
│   │   ├── __init__.py
│   │   └── cliente_service.py         <- Capa de negocio y validaciones
│   └── controllers/
│       ├── __init__.py
│       └── cliente_controller.py      <- Capa controladora REST (Flask Blueprint)
│
├── main.py                            <- Servidor web REST (sin menús interactivos)
├── requirements.txt                   <- Dependencias del proyecto (Flask)
├── test_capas.py                      <- Pruebas automatizadas de la API REST
└── README.md                          <- Documentación del proyecto
```

---

## 🚀 Instalación y Ejecución

### 1. Instalar dependencias
```bash
pip install -r requirements.txt
```

### 2. Iniciar el servidor web REST
```bash
python main.py
```
El servidor quedará escuchando en `http://localhost:5000`.

---

## 📡 Catálogo de Endpoints REST

| Método | Endpoint | Descripción | Códigos HTTP |
| :--- | :--- | :--- | :--- |
| **GET** | `/` | Documentación general de la API | `200` |
| **GET** | `/api/clientes` | Consultar todos los clientes | `200`, `500` |
| **GET** | `/api/clientes/<id>` | Consultar cliente específico por ID | `200`, `400`, `404` |
| **POST** | `/api/clientes` | Registrar un nuevo cliente | `201`, `400`, `500` |
| **PUT** | `/api/clientes/<id>` | Modificar un cliente existente | `200`, `400`, `404` |

---

## 💻 Ejemplos de Peticiones

### 1. Consultar todos los clientes
```bash
curl -X GET http://localhost:5000/api/clientes
```
**Respuesta:**
```json
{
  "exito": true,
  "mensaje": "Se obtuvieron 4 clientes correctamente.",
  "total": 4,
  "datos": [
    {
      "id": "1",
      "nombre": "Juan",
      "apellido": "Perez",
      "email": "juan.perez@example.com",
      "telefono": "555-1234",
      "activo": "True"
    }
  ]
}
```

### 2. Consultar cliente por ID
```bash
curl -X GET http://localhost:5000/api/clientes/1
```

### 3. Crear un nuevo cliente
```bash
curl -X POST http://localhost:5000/api/clientes \
  -H "Content-Type: application/json" \
  -d '{
    "nombre": "Sofia",
    "apellido": "Herrera",
    "email": "sofia.herrera@example.com",
    "telefono": "555-7788",
    "activo": true
  }'
```

### 4. Modificar un cliente
```bash
curl -X PUT http://localhost:5000/api/clientes/1 \
  -H "Content-Type: application/json" \
  -d '{
    "telefono": "555-9999",
    "activo": false
  }'
```

---

## 🧪 Pruebas Automatizadas
Para verificar que todas las capas y los endpoints REST respondan correctamente:
```bash
python test_capas.py
```
