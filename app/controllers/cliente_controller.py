from flask import Blueprint, request, jsonify, Response
from typing import Optional
from app.services.cliente_service import (
    ClienteService,
    ClienteServiceError,
    ClienteNoEncontradoError,
    ClienteValidacionError,
)

# Definimos el Blueprint para agrupar las rutas REST de clientes
cliente_bp = Blueprint("clientes", __name__, url_prefix="/api/clientes")


class ClienteController:
    """
    Capa de Controlador REST.
    Maneja las peticiones HTTP, extrae parámetros/cuerpos JSON,
    delega a la capa de Servicio y devuelve respuestas HTTP con códigos de estado REST estándar.
    """

    def __init__(self, service: Optional[ClienteService] = None):
        self.service = service or ClienteService()

    def listar_clientes(self) -> Response:
        """GET /api/clientes - Consulta todos los clientes."""
        try:
            clientes = self.service.listar_clientes()
            return jsonify({
                "exito": True,
                "mensaje": f"Se obtuvieron {len(clientes)} clientes correctamente.",
                "total": len(clientes),
                "datos": [c.to_dict() for c in clientes],
            }), 200
        except ClienteServiceError as e:
            return jsonify({"exito": False, "mensaje": str(e), "datos": []}), 500

    def obtener_cliente(self, cliente_id: str) -> Response:
        """GET /api/clientes/<id> - Consulta un cliente por ID."""
        try:
            cliente = self.service.buscar_por_id(cliente_id)
            return jsonify({
                "exito": True,
                "mensaje": "Cliente encontrado.",
                "datos": cliente.to_dict(),
            }), 200
        except ClienteNoEncontradoError as e:
            return jsonify({"exito": False, "mensaje": str(e), "datos": None}), 404
        except ClienteValidacionError as e:
            return jsonify({"exito": False, "mensaje": str(e), "datos": None}), 400
        except ClienteServiceError as e:
            return jsonify({"exito": False, "mensaje": str(e), "datos": None}), 500

    def crear_cliente(self) -> Response:
        """POST /api/clientes - Crea un nuevo cliente a partir de un JSON."""
        datos = request.get_json(silent=True)
        if not datos or not isinstance(datos, dict):
            return jsonify({
                "exito": False,
                "mensaje": "El cuerpo de la petición debe ser un objeto JSON válido con los datos del cliente.",
                "datos": None
            }), 400

        try:
            nuevo_cliente = self.service.crear_cliente(
                nombre=datos.get("nombre", ""),
                apellido=datos.get("apellido", ""),
                email=datos.get("email", ""),
                telefono=datos.get("telefono", ""),
                activo=datos.get("activo", True),
                cliente_id=datos.get("id"),
            )
            return jsonify({
                "exito": True,
                "mensaje": f"Cliente '{nuevo_cliente.nombre} {nuevo_cliente.apellido}' creado exitosamente con ID {nuevo_cliente.id}.",
                "datos": nuevo_cliente.to_dict(),
            }), 201
        except ClienteValidacionError as e:
            return jsonify({"exito": False, "mensaje": str(e), "datos": None}), 400
        except ClienteServiceError as e:
            return jsonify({"exito": False, "mensaje": str(e), "datos": None}), 500

    def modificar_cliente(self, cliente_id: str) -> Response:
        """PUT /api/clientes/<id> - Modifica la información básica de un cliente."""
        datos = request.get_json(silent=True)
        if not datos or not isinstance(datos, dict):
            return jsonify({
                "exito": False,
                "mensaje": "El cuerpo de la petición debe ser un objeto JSON válido con los campos a modificar.",
                "datos": None
            }), 400

        try:
            cliente_actualizado = self.service.modificar_cliente(cliente_id, datos)
            return jsonify({
                "exito": True,
                "mensaje": f"Cliente con ID {cliente_id} modificado exitosamente.",
                "datos": cliente_actualizado.to_dict(),
            }), 200
        except ClienteNoEncontradoError as e:
            return jsonify({"exito": False, "mensaje": str(e), "datos": None}), 404
        except ClienteValidacionError as e:
            return jsonify({"exito": False, "mensaje": str(e), "datos": None}), 400
        except ClienteServiceError as e:
            return jsonify({"exito": False, "mensaje": str(e), "datos": None}), 500


def registrar_rutas(controller: Optional[ClienteController] = None) -> Blueprint:
    """Registra y enlaza las rutas HTTP del Blueprint con los métodos del controlador."""
    ctrl = controller or ClienteController()

    @cliente_bp.route("", methods=["GET"])
    def listar():
        return ctrl.listar_clientes()

    @cliente_bp.route("/<cliente_id>", methods=["GET"])
    def obtener(cliente_id):
        return ctrl.obtener_cliente(cliente_id)

    @cliente_bp.route("", methods=["POST"])
    def crear():
        return ctrl.crear_cliente()

    @cliente_bp.route("/<cliente_id>", methods=["PUT", "PATCH"])
    def modificar(cliente_id):
        return ctrl.modificar_cliente(cliente_id)

    return cliente_bp
