import os
import json
import logging
from typing import Dict, Any, Optional
import requests

logger = logging.getLogger("gemini.ia")


class GeminiRepositoryError(Exception):
    """Excepción para errores de comunicación con la API de Gemini."""
    pass


class GeminiRepository:
    """
    Capa de Repositorio para la interacción REST directa con Google Gemini API.
    Realiza las peticiones HTTP y registra detalladamente requests y responses por ID de conversación.
    """

    BASE_URL = "https://generativelanguage.googleapis.com/v1beta/models"
    DEFAULT_MODEL = "gemini-2.5-flash"

    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        self.api_key = api_key or os.environ.get("GEMINI_API_KEY", "")
        self.model = model or os.environ.get("GEMINI_MODEL", self.DEFAULT_MODEL)

    def generar_contenido(self, payload: Dict[str, Any], conversacion_id: str) -> Dict[str, Any]:
        """
        Envía una petición POST directa a la API de Gemini para generateContent.
        Registra detalladamente la request y response asociadas al conversacion_id.
        """
        if not self.api_key:
            logger.error(f"[{conversacion_id}] GEMINI_API_KEY no está configurada en las variables de entorno.")
            raise GeminiRepositoryError("GEMINI_API_KEY no está configurada en las variables de entorno.")

        url = f"{self.BASE_URL}/{self.model}:generateContent?key={self.api_key}"
        # URL enmascarada para logs seguros
        url_masked = f"{self.BASE_URL}/{self.model}:generateContent?key=***{self.api_key[-4:] if len(self.api_key) > 4 else '***'}"

        headers = {
            "Content-Type": "application/json"
        }

        # Log muy específico de la Request hacia Gemini
        payload_json = json.dumps(payload, indent=2, ensure_ascii=False)
        logger.info(
            f"\n==================== [IA REQUEST | CONV: {conversacion_id}] ====================\n"
            f"Endpoint: {url_masked}\n"
            f"Headers: {json.dumps(headers)}\n"
            f"Payload:\n{payload_json}\n"
            f"=================================================================================="
        )

        try:
            response = requests.post(url, headers=headers, json=payload, timeout=30)
        except requests.RequestException as e:
            logger.error(f"[{conversacion_id}] Error de red al conectar con Gemini: {str(e)}")
            raise GeminiRepositoryError(f"Error de conexión con la API de Gemini: {str(e)}")

        # Log muy específico de la Response desde Gemini
        try:
            response_data = response.json()
            response_json = json.dumps(response_data, indent=2, ensure_ascii=False)
        except ValueError:
            response_data = {"raw_text": response.text}
            response_json = response.text

        logger.info(
            f"\n==================== [IA RESPONSE | CONV: {conversacion_id}] ====================\n"
            f"Status Code: {response.status_code}\n"
            f"Body:\n{response_json}\n"
            f"=================================================================================="
        )

        if response.status_code != 200:
            mensaje_error = response_data.get("error", {}).get("message", response.text)
            raise GeminiRepositoryError(f"Error de API Gemini ({response.status_code}): {mensaje_error}")

        return response_data
