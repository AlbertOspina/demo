import os
import logging
from flask import Flask, jsonify
from dotenv import load_dotenv
from app.controllers import ClienteController, GeminiController, registrar_rutas_cliente, registrar_rutas_gemini
from app.models import ResponseDTO

# Configuración de logging detallado para la aplicación y llamadas a la IA
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] [%(name)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger("app.main")


def create_app() -> Flask:
    """Fábrica de la aplicación web Flask."""
    # Cargar variables de entorno desde archivo .env si existe
    load_dotenv()

    app = Flask(__name__)

    # 1. Registrar el Blueprint del controlador de clientes
    app.register_blueprint(registrar_rutas_cliente(ClienteController()))

    # 2. Registrar el Blueprint del controlador de Gemini (IA con Tools)
    app.register_blueprint(registrar_rutas_gemini(GeminiController()))

    # Ruta raíz informativa con la documentación de los endpoints
    @app.route("/", methods=["GET"])
    def index():
        response_dto = ResponseDTO(
            code=200,
            message="Ok",
            data={
                "aplicacion": "API REST de Gestión de Clientes con Asistente IA (Gemini)",
                "arquitectura": "Por capas (Controlador -> Servicio -> Repositorio)",
                "persistencia": "Archivo CSV en resources/clientes.csv",
                "endpoints": {
                    "GET /api/clientes": "Consultar todos los clientes registrados",
                    "GET /api/clientes/<id>": "Consultar cliente específico por ID",
                    "POST /api/clientes": "Crear un nuevo cliente (JSON con nombre, apellido, email, telefono, activo)",
                    "PUT /api/clientes/<id>": "Modificar datos de un cliente existente (JSON)",
                    "POST /api/gemini/consulta": "Consultar a la IA sobre clientes mediante lenguaje natural y Tools"
                },
                "estado": "activo"
            },
            total=None
        )
        return jsonify(response_dto.to_dict()), 200

    # Manejo de rutas inexistentes (404)
    @app.errorhandler(404)
    def ruta_no_encontrada(error):
        response_dto = ResponseDTO(
            code=404,
            message="Recurso no encontrado. Consulte GET / para ver los endpoints disponibles.",
            data=None,
            total=None
        )
        return jsonify(response_dto.to_dict()), 404

    # Manejo de errores internos del servidor (500)
    @app.errorhandler(500)
    def error_servidor(error):
        response_dto = ResponseDTO(
            code=500,
            message="Error interno del servidor.",
            data=None,
            total=None
        )
        return jsonify(response_dto.to_dict()), 500

    return app


if __name__ == "__main__":
    app = create_app()
    puerto = int(os.environ.get("PORT", 5000))
    print(f"[*] Iniciando servidor REST en http://localhost:{puerto}")
    print("[*] Presione CTRL+C para detener el servidor.")
    app.run(host="0.0.0.0", port=puerto, debug=False)
