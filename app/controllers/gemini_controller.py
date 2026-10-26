import uuid
from typing import Optional
from flask import Blueprint, request, jsonify, Response
from app.services.gemini_service import GeminiService, GeminiServiceError
from app.models import ResponseDTO


class GeminiController:
    """
    Capa de Controlador para las consultas asistidas por la IA de Gemini.
    Gestiona el endpoint REST, asegura el ID de conversación y responde con ResponseDTO.
    """

    def __init__(self, service: Optional[GeminiService] = None):
        self.service = service or GeminiService()

    def consultar(self) -> Response:
        """POST /api/gemini/consulta - Realiza una consulta en lenguaje natural."""
        response_dto = ResponseDTO(
            code=200,
            message="Ok",
            data=None,
            total=None
        )

        datos = request.get_json(silent=True)
        if not datos or not isinstance(datos, dict):
            response_dto.code = 400
            response_dto.message = "El cuerpo de la petición debe ser un objeto JSON válido con el campo 'mensaje'."
            return jsonify(response_dto.to_dict()), 400

        mensaje = datos.get("mensaje", "")
        if not mensaje or not str(mensaje).strip():
            response_dto.code = 400
            response_dto.message = "El campo 'mensaje' es obligatorio y no puede estar vacío."
            return jsonify(response_dto.to_dict()), 400

        # Obtener o autogenerar identificador de conversación para trazabilidad de logs
        conversacion_id = str(datos.get("conversacion_id") or f"conv-{uuid.uuid4().hex[:8]}").strip()

        try:
            resultado = self.service.procesar_consulta(
                mensaje=str(mensaje).strip(),
                conversacion_id=conversacion_id
            )
            response_dto.data = resultado
            response_dto.message = "Consulta procesada correctamente por la IA."
            return jsonify(response_dto.to_dict()), 200

        except GeminiServiceError as e:
            response_dto.code = 500
            response_dto.message = str(e)
            return jsonify(response_dto.to_dict()), 500
        except Exception as e:
            response_dto.code = 500
            response_dto.message = f"Error no controlado al procesar consulta: {str(e)}"
            return jsonify(response_dto.to_dict()), 500


def registrar_rutas_gemini(controller: Optional[GeminiController] = None) -> Blueprint:
    """Crea y registra las rutas HTTP de un Blueprint con los métodos de GeminiController."""
    # Si no pasan un controlador, crea uno por defecto aquí mismo
    ctrl = controller or GeminiController()

    bp = Blueprint(f"gemini_{id(controller)}", __name__, url_prefix="/api/gemini")

    @bp.route("/consulta", methods=["POST"])
    def consulta():
        return ctrl.consultar()

    return bp
