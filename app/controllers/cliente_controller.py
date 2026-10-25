from flask import Blueprint, request, jsonify, Response
from typing import Optional
from app.services.cliente_service import (
    ClienteService,
    ClienteServiceError,
    ClienteNoEncontradoError,
    ClienteValidacionError,
)
from app.models import ResponseDTO


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
        response_dto = ResponseDTO(
            code=200,
            message="Ok",
            data=None,
            total=None
        )
        try:
            clientes = self.service.listar_clientes()
            response_dto.data = [cliente.to_dict() for cliente in clientes]
            response_dto.total = len(clientes)
            return jsonify(response_dto.to_dict()), 200
        except ClienteServiceError as e:
            response_dto.code = 500
            response_dto.message = str(e)
            return jsonify(response_dto.to_dict()), 500

    def obtener_cliente(self, cliente_id: str) -> Response:
        """GET /api/clientes/<id> - Consulta un cliente por ID."""
        response_dto = ResponseDTO(
            code=200,
            message="Ok",
            data=None,
            total=None
        )
        try:
            cliente = self.service.buscar_por_id(cliente_id)
            response_dto.data = cliente.to_dict()
            response_dto.message = "Cliente encontrado."
            return jsonify(response_dto.to_dict()), 200
        except ClienteNoEncontradoError as e:
            response_dto.code = 404
            response_dto.message = str(e)
            return jsonify(response_dto.to_dict()), 404
        except ClienteValidacionError as e:
            response_dto.code = 400
            response_dto.message = str(e)
            return jsonify(response_dto.to_dict()), 400
        except ClienteServiceError as e:
            response_dto.code = 500
            response_dto.message = str(e)
            return jsonify(response_dto.to_dict()), 500

    def crear_cliente(self) -> Response:
        """POST /api/clientes - Crea un nuevo cliente a partir de un JSON."""
        response_dto = ResponseDTO(
            code=201,
            message="Ok",
            data=None,
            total=None
        )
        datos = request.get_json(silent=True)
        if not datos or not isinstance(datos, dict):
            response_dto.code = 400
            response_dto.message = "El cuerpo de la petición debe ser un objeto JSON válido con los datos del cliente."
            return jsonify(response_dto.to_dict()), 400

        try:
            nuevo_cliente = self.service.crear_cliente(
                nombre=datos.get("nombre", ""),
                apellido=datos.get("apellido", ""),
                email=datos.get("email", ""),
                telefono=datos.get("telefono", ""),
                activo=datos.get("activo", True),
                cliente_id=datos.get("id"),
            )
            response_dto.data = nuevo_cliente.to_dict()
            response_dto.message = f"Cliente '{nuevo_cliente.nombre} {nuevo_cliente.apellido}' creado exitosamente con ID {nuevo_cliente.id}."
            return jsonify(response_dto.to_dict()), 201
        except ClienteValidacionError as e:
            response_dto.code = 400
            response_dto.message = str(e)
            return jsonify(response_dto.to_dict()), 400
        except ClienteServiceError as e:
            response_dto.code = 500
            response_dto.message = str(e)
            return jsonify(response_dto.to_dict()), 500

    def modificar_cliente(self, cliente_id: str) -> Response:
        """PUT /api/clientes/<id> - Modifica la información básica de un cliente."""
        response_dto = ResponseDTO(
            code=200,
            message="Ok",
            data=None,
            total=None
        )
        datos = request.get_json(silent=True)
        if not datos or not isinstance(datos, dict):
            response_dto.code = 400
            response_dto.message = "El cuerpo de la petición debe ser un objeto JSON válido con los campos a modificar."
            return jsonify(response_dto.to_dict()), 400

        try:
            cliente_actualizado = self.service.modificar_cliente(cliente_id, datos)
            response_dto.data = cliente_actualizado.to_dict()
            response_dto.message = f"Cliente con ID {cliente_id} modificado exitosamente."
            return jsonify(response_dto.to_dict()), 200
        except ClienteNoEncontradoError as e:
            response_dto.code = 404
            response_dto.message = str(e)
            return jsonify(response_dto.to_dict()), 404
        except ClienteValidacionError as e:
            response_dto.code = 400
            response_dto.message = str(e)
            return jsonify(response_dto.to_dict()), 400
        except ClienteServiceError as e:
            response_dto.code = 500
            response_dto.message = str(e)
            return jsonify(response_dto.to_dict()), 500


# Blueprint para agrupar las rutas REST de clientes
cliente_bp = Blueprint("clientes", __name__, url_prefix="/api/clientes")
_cliente_controller_default = ClienteController()


@cliente_bp.route("", methods=["GET"])
def listar_clientes_default():
    return _cliente_controller_default.listar_clientes()


@cliente_bp.route("/<cliente_id>", methods=["GET"])
def obtener_cliente_default(cliente_id):
    return _cliente_controller_default.obtener_cliente(cliente_id)


@cliente_bp.route("", methods=["POST"])
def crear_cliente_default():
    return _cliente_controller_default.crear_cliente()


@cliente_bp.route("/<cliente_id>", methods=["PUT", "PATCH"])
def modificar_cliente_default(cliente_id):
    return _cliente_controller_default.modificar_cliente(cliente_id)


def registrar_rutas_cliente(controller: Optional[ClienteController] = None) -> Blueprint:
    """Crea y registra las rutas HTTP de un Blueprint con los métodos del controlador."""
    if controller is None:
        return cliente_bp

    bp = Blueprint(f"clientes_{id(controller)}", __name__, url_prefix="/api/clientes")

    @bp.route("", methods=["GET"])
    def listar():
        return controller.listar_clientes()

    @bp.route("/<cliente_id>", methods=["GET"])
    def obtener(cliente_id):
        return controller.obtener_cliente(cliente_id)

    @bp.route("", methods=["POST"])
    def crear():
        return controller.crear_cliente()

    @bp.route("/<cliente_id>", methods=["PUT", "PATCH"])
    def modificar(cliente_id):
        return controller.modificar_cliente(cliente_id)

    return bp


# Alias para retrocompatibilidad
registrar_rutas = registrar_rutas_cliente
