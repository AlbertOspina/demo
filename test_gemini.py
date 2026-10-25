"""
Pruebas automatizadas para la integración de Gemini con arquitectura por capas y Tools.
"""
from pathlib import Path
from flask import Flask
from app.models import Cliente
from app.repositories.cliente_repository import ClienteRepository
from app.repositories.gemini_repository import GeminiRepository
from app.services.cliente_service import ClienteService
from app.services.gemini_service import GeminiService
from app.controllers.gemini_controller import GeminiController, registrar_rutas_gemini


class MockGeminiRepository(GeminiRepository):
    """Repositorio mock para simular las respuestas de la API de Gemini sin consumir cuota real."""

    def __init__(self):
        super().__init__(api_key="fake_key_for_test")
        self.llamadas = []

    def generar_contenido(self, payload, conversacion_id):
        self.llamadas.append({
            "payload": payload,
            "conversacion_id": conversacion_id
        })

        contents = payload.get("contents", [])
        ultimo_mensaje = contents[-1]
        parts = ultimo_mensaje.get("parts", [])

        # Si el último mensaje es una respuesta de función (functionResponse), responder con texto final
        if any("functionResponse" in p for p in parts):
            return {
                "candidates": [
                    {
                        "content": {
                            "role": "model",
                            "parts": [
                                {
                                    "text": "Actualmente hay 2 clientes registrados en el sistema: Juan Perez y Maria Gomez."
                                }
                            ]
                        }
                    }
                ]
            }

        # Si es la primera llamada del usuario, simular que el modelo pide ejecutar la tool "listar_clientes"
        return {
            "candidates": [
                {
                    "content": {
                        "role": "model",
                        "parts": [
                            {
                                "functionCall": {
                                    "name": "listar_clientes",
                                    "args": {}
                                }
                            }
                        ]
                    }
                }
            ]
        }


def test_gemini_capas_y_tools():
    test_csv = Path(__file__).resolve().parent / "resources" / "test_gemini_clientes.csv"
    if test_csv.exists():
        test_csv.unlink()

    # 1. Preparar capas con datos de prueba
    cliente_repo = ClienteRepository(file_path=test_csv)
    cliente_service = ClienteService(repository=cliente_repo)
    cliente_service.crear_cliente("Juan", "Perez", "juan.perez@example.com", "555-1111", True, "1")
    cliente_service.crear_cliente("Maria", "Gomez", "maria.gomez@example.com", "555-2222", True, "2")

    mock_gemini_repo = MockGeminiRepository()
    gemini_service = GeminiService(
        gemini_repository=mock_gemini_repo,
        cliente_service=cliente_service
    )
    gemini_controller = GeminiController(service=gemini_service)

    # 2. Probar ejecución de Service directamente
    print("\n=== 1. Probando ciclo de Function Calling en GeminiService ===")
    conv_id = "test-conv-001"
    resultado = gemini_service.procesar_consulta("¿Quiénes son los clientes?", conversacion_id=conv_id)

    assert resultado["conversacion_id"] == conv_id
    assert "Juan Perez" in resultado["respuesta"]
    assert len(resultado["herramientas_utilizadas"]) == 1
    assert resultado["herramientas_utilizadas"][0]["nombre"] == "listar_clientes"
    assert len(resultado["herramientas_utilizadas"][0]["resultado"]) == 2
    print("  [OK] GeminiService resolvió la tool 'listar_clientes' y generó la respuesta final.")

    # 3. Probar controlador con test_client de Flask
    print("\n=== 2. Probando endpoint REST POST /api/gemini/consulta ===")
    app = Flask(__name__)
    app.register_blueprint(registrar_rutas_gemini(gemini_controller))
    client = app.test_client()

    peticion = {
        "mensaje": "¿Cuántos clientes tenemos?",
        "conversacion_id": "conv-web-123"
    }
    res = client.post("/api/gemini/consulta", json=peticion)
    assert res.status_code == 200
    json_data = res.get_json()
    assert json_data["code"] == 200
    assert json_data["data"]["conversacion_id"] == "conv-web-123"
    assert "respuesta" in json_data["data"]
    print("  [OK] Endpoint REST respondió 200 con ResponseDTO válido.")

    # 4. Probar validación de mensaje vacío
    print("\n=== 3. Probando validación de mensaje vacío ===")
    res_vacio = client.post("/api/gemini/consulta", json={"mensaje": "   "})
    assert res_vacio.status_code == 400
    assert res_vacio.get_json()["code"] == 400
    print("  [OK] Validó correctamente el mensaje vacío con HTTP 400.")

    # 5. Probar tool buscar_cliente_por_id
    print("\n=== 4. Probando tool directa buscar_cliente_por_id ===")
    res_tool = gemini_service.ejecutar_tool("buscar_cliente_por_id", {"cliente_id": "1"}, conversacion_id="conv-tool")
    assert res_tool["id"] == "1"
    assert res_tool["nombre"] == "Juan"
    print("  [OK] Tool 'buscar_cliente_por_id' ejecutada correctamente.")

    # 6. Probar tool filtrar_clientes
    print("\n=== 5. Probando tool directa filtrar_clientes ===")
    res_filtro = gemini_service.ejecutar_tool("filtrar_clientes", {"termino": "maria"}, conversacion_id="conv-tool")
    assert len(res_filtro) == 1
    assert res_filtro[0]["nombre"] == "Maria"
    print("  [OK] Tool 'filtrar_clientes' ejecutada correctamente.")

    # Limpieza
    if test_csv.exists():
        test_csv.unlink()

    print("\n>>> TODAS LAS PRUEBAS DE GEMINI Y TOOLS PASARON EXITOSAMENTE. <<<\n")


if __name__ == "__main__":
    test_gemini_capas_y_tools()
