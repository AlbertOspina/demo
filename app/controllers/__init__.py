from app.controllers.cliente_controller import (
    ClienteController,
    registrar_rutas_cliente
)
from app.controllers.gemini_controller import (
    GeminiController,
    registrar_rutas_gemini
)

__all__ = [
    "ClienteController",
    "registrar_rutas_cliente",
    "GeminiController",
    "registrar_rutas_gemini"
]
