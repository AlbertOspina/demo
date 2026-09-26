import csv
from pathlib import Path
from typing import List, Optional
from app.models.cliente import Cliente


class ClienteRepository:
    """
    Capa de Acceso a Datos (Repositorio).
    Maneja la persistencia y lectura de clientes sobre un archivo CSV.
    """

    CAMPOS = ["id", "nombre", "apellido", "email", "telefono", "activo"]

    def __init__(self, file_path: Optional[Path] = None):
        if file_path is None:
            # Ruta predeterminada: <raiz_proyecto>/resources/clientes.csv
            base_dir = Path(__file__).resolve().parent.parent.parent
            self.file_path = base_dir / "resources" / "clientes.csv"
        else:
            self.file_path = Path(file_path)

        self._asegurar_archivo()

    def _asegurar_archivo(self) -> None:
        """Asegura que el archivo y su directorio existan con sus encabezados."""
        self.file_path.parent.mkdir(parents=True, exist_ok=True)
        if not self.file_path.exists():
            with open(self.file_path, mode="w", newline="", encoding="utf-8") as file:
                writer = csv.DictWriter(file, fieldnames=self.CAMPOS)
                writer.writeheader()

    def obtener_todos(self) -> List[Cliente]:
        """Recupera la lista completa de clientes registrados en el CSV."""
        clientes: List[Cliente] = []
        if not self.file_path.exists():
            return clientes

        with open(self.file_path, mode="r", newline="", encoding="utf-8") as file:
            reader = csv.DictReader(file)
            for row in reader:
                if row:
                    clientes.append(Cliente.from_dict(row))
        return clientes

    def obtener_por_id(self, cliente_id: str) -> Optional[Cliente]:
        """Busca un cliente por su ID."""
        cliente_id_str = str(cliente_id).strip()
        for cliente in self.obtener_todos():
            if cliente.id == cliente_id_str:
                return cliente
        return None

    def obtener_por_email(self, email: str) -> Optional[Cliente]:
        """Busca un cliente por su dirección de email (case-insensitive)."""
        email_clean = email.strip().lower()
        for cliente in self.obtener_todos():
            if cliente.email.lower() == email_clean:
                return cliente
        return None

    def guardar(self, cliente: Cliente) -> Cliente:
        """Agrega un nuevo cliente al final del archivo CSV."""
        with open(self.file_path, mode="a", newline="", encoding="utf-8") as file:
            writer = csv.DictWriter(file, fieldnames=self.CAMPOS)
            writer.writerow(cliente.to_dict())
        return cliente

    def actualizar(self, cliente_actualizado: Cliente) -> Optional[Cliente]:
        """
        Actualiza los datos de un cliente existente.
        Retorna el cliente actualizado o None si no fue encontrado.
        """
        clientes = self.obtener_todos()
        encontrado = False

        for i, c in enumerate(clientes):
            if c.id == cliente_actualizado.id:
                clientes[i] = cliente_actualizado
                encontrado = True
                break

        if not encontrado:
            return None

        # Reescribimos el archivo con la lista actualizada
        with open(self.file_path, mode="w", newline="", encoding="utf-8") as file:
            writer = csv.DictWriter(file, fieldnames=self.CAMPOS)
            writer.writeheader()
            for c in clientes:
                writer.writerow(c.to_dict())

        return cliente_actualizado

    def generar_siguiente_id(self) -> str:
        """Calcula el siguiente identificador incremental."""
        clientes = self.obtener_todos()
        ids_numericos = []
        for c in clientes:
            if c.id.isdigit():
                ids_numericos.append(int(c.id))

        if ids_numericos:
            return str(max(ids_numericos) + 1)
        return "1"
