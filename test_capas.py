"""
Pruebas automatizadas de los endpoints REST y de la arquitectura por capas.
"""
from pathlib import Path
from main import create_app
from app.repositories.cliente_repository import ClienteRepository
from app.services.cliente_service import ClienteService
from app.controllers.cliente_controller import ClienteController, registrar_rutas
from flask import Flask


def test_api_rest():
    test_csv = Path(__file__).resolve().parent / "resources" / "test_api_clientes.csv"
    if test_csv.exists():
        test_csv.unlink()

    # Inyección de dependencias con repositorio apuntando al CSV de prueba
    repo = ClienteRepository(file_path=test_csv)
    service = ClienteService(repository=repo)
    controller = ClienteController(service=service)

    # Crear app de test
    app = Flask(__name__)
    app.register_blueprint(registrar_rutas(controller))
    client = app.test_client()

    print("\n=== 1. Probando GET /api/clientes (Lista vacía inicialmente) ===")
    res = client.get("/api/clientes")
    assert res.status_code == 200
    json_data = res.get_json()
    assert json_data["code"] == 200
    assert json_data["total"] == 0
    print("  [OK] Retornó lista vacía con status 200.")

    print("\n=== 2. Probando POST /api/clientes (Crear cliente) ===")
    nuevo_cliente = {
        "nombre": "Carlos",
        "apellido": "Santana",
        "email": "carlos.santana@example.com",
        "telefono": "555-1122",
        "activo": True
    }
    res = client.post("/api/clientes", json=nuevo_cliente)
    assert res.status_code == 201
    json_data = res.get_json()
    assert json_data["code"] == 201
    cliente_id = json_data["data"]["id"]
    print(f"  [OK] Cliente creado exitosamente con ID {cliente_id} (Status 201).")

    print("\n=== 3. Probando validación en POST /api/clientes (Email inválido) ===")
    res_invalido = client.post("/api/clientes", json={
        "nombre": "Error",
        "apellido": "Test",
        "email": "correo-no-valido",
        "telefono": "123"
    })
    assert res_invalido.status_code == 400
    assert res_invalido.get_json()["code"] == 400
    print("  [OK] Rechazó email inválido con status 400.")

    print("\n=== 4. Probando GET /api/clientes/<id> (Consultar por ID) ===")
    res = client.get(f"/api/clientes/{cliente_id}")
    assert res.status_code == 200
    json_data = res.get_json()
    assert json_data["code"] == 200
    assert json_data["data"]["nombre"] == "Carlos"
    print("  [OK] Cliente consultado correctamente por ID (Status 200).")

    print("\n=== 5. Probando PUT /api/clientes/<id> (Modificar cliente) ===")
    cambios = {
        "telefono": "555-9999",
        "apellido": "Santana Modificado"
    }
    res = client.put(f"/api/clientes/{cliente_id}", json=cambios)
    assert res.status_code == 200
    json_data = res.get_json()
    assert json_data["code"] == 200
    assert json_data["data"]["telefono"] == "555-9999"
    assert json_data["data"]["apellido"] == "Santana Modificado"
    assert json_data["data"]["nombre"] == "Carlos" # Conserva nombre
    print("  [OK] Cliente modificado exitosamente (Status 200).")

    print("\n=== 6. Probando GET /api/clientes/<id> inexistente ===")
    res = client.get("/api/clientes/99999")
    assert res.status_code == 404
    assert res.get_json()["code"] == 404
    print("  [OK] Retorna 404 para ID inexistente.")

    print("\n=== 7. Probando endpoints de main.py (create_app: raíz y 404) ===")
    full_app = create_app()
    full_client = full_app.test_client()

    res_root = full_client.get("/")
    assert res_root.status_code == 200
    assert res_root.get_json()["code"] == 200
    assert "aplicacion" in res_root.get_json()["data"]

    res_not_found = full_client.get("/endpoint-no-existente")
    assert res_not_found.status_code == 404
    assert res_not_found.get_json()["code"] == 404
    print("  [OK] Rutas de main.py devuelven ResponseDTO correctamente.")

    # Limpieza
    if test_csv.exists():
        test_csv.unlink()

    print("\n>>> TODAS LAS PRUEBAS DE LA API REST PASARON SATISFACTORIAMENTE. <<<\n")


if __name__ == "__main__":
    test_api_rest()
