from app.controllers.cliente_controller import (
    ClienteController,
    cliente_bp,
    registrar_rutas_cliente,
    registrar_rutas,
)
from app.controllers.gemini_controller import (
    GeminiController,
    gemini_bp,
    registrar_rutas_gemini,
)

__all__ = [
    "ClienteController",
    "cliente_bp",
    "registrar_rutas_cliente",
    "registrar_rutas",
    "GeminiController",
    "gemini_bp",
    "registrar_rutas_gemini",
]
