import os
from flask import Flask, jsonify
from app.controllers.cliente_controller import registrar_rutas


def create_app() -> Flask:
    """Fábrica de la aplicación web Flask."""
    app = Flask(__name__)

    # Registrar el Blueprint del controlador de clientes
    bp = registrar_rutas()
    app.register_blueprint(bp)

    # Ruta raíz informativa con la documentación de los endpoints
    @app.route("/", methods=["GET"])
    def index():
        return jsonify({
            "aplicacion": "API REST de Gestión de Clientes",
            "arquitectura": "Por capas (Controlador -> Servicio -> Repositorio)",
            "persistencia": "Archivo CSV en resources/clientes.csv",
            "endpoints": {
                "GET /api/clientes": "Consultar todos los clientes registrados",
                "GET /api/clientes/<id>": "Consultar cliente específico por ID",
                "POST /api/clientes": "Crear un nuevo cliente (JSON con nombre, apellido, email, telefono, activo)",
                "PUT /api/clientes/<id>": "Modificar datos de un cliente existente (JSON)"
            },
            "estado": "activo"
        }), 200

    # Manejo de rutas inexistentes (404)
    @app.errorhandler(404)
    def ruta_no_encontrada(error):
        return jsonify({
            "exito": False,
            "mensaje": "Recurso no encontrado. Consulte GET / para ver los endpoints disponibles.",
            "datos": None
        }), 404

    return app


if __name__ == "__main__":
    app = create_app()
    puerto = int(os.environ.get("PORT", 5000))
    print(f"[*] Iniciando servidor REST en http://localhost:{puerto}")
    print("[*] Presione CTRL+C para detener el servidor.")
    app.run(host="0.0.0.0", port=puerto, debug=False)
