import re
from typing import List, Optional, Dict, Any
from app.models.cliente import Cliente
from app.repositories.cliente_repository import ClienteRepository


class ClienteServiceError(Exception):
    """Excepción base para errores en la capa de servicio de clientes."""
    pass


class ClienteNoEncontradoError(ClienteServiceError):
    """Excepción lanzada cuando el cliente solicitado no existe."""
    pass


class ClienteValidacionError(ClienteServiceError):
    """Excepción lanzada cuando los datos del cliente no cumplen las validaciones."""
    pass


class ClienteService:
    """
    Capa de Lógica de Negocio (Servicio).
    Aplica reglas de negocio, validaciones y orquesta las operaciones con el repositorio.
    """

    def __init__(self, repository: Optional[ClienteRepository] = None):
        self.repository = repository or ClienteRepository()

    def listar_clientes(self) -> List[Cliente]:
        """Obtiene el listado de todos los clientes."""
        return self.repository.obtener_todos()

    def buscar_por_id(self, cliente_id: str) -> Cliente:
        """
        Busca un cliente por su ID.
        Lanza ClienteNoEncontradoError si no existe.
        """
        if not cliente_id or not str(cliente_id).strip():
            raise ClienteValidacionError("El ID de cliente es obligatorio.")

        cliente = self.repository.obtener_por_id(str(cliente_id).strip())
        if not cliente:
            raise ClienteNoEncontradoError(f"No se encontró ningún cliente con el ID '{cliente_id}'.")
        return cliente

    def crear_cliente(
        self,
        nombre: str,
        apellido: str,
        email: str,
        telefono: str,
        activo: bool = True,
        cliente_id: Optional[str] = None
    ) -> Cliente:
        """
        Crea y persiste un nuevo cliente realizando las validaciones de negocio.
        """
        self._validar_datos_basicos(nombre, apellido, email, telefono)

        # Verificar si el email ya se encuentra registrado
        cliente_existente_email = self.repository.obtener_por_email(email)
        if cliente_existente_email:
            raise ClienteValidacionError(f"Ya existe un cliente registrado con el email '{email}'.")

        # Asignar o generar ID
        if cliente_id and str(cliente_id).strip():
            id_final = str(cliente_id).strip()
            if self.repository.obtener_por_id(id_final):
                raise ClienteValidacionError(f"Ya existe un cliente con el ID '{id_final}'.")
        else:
            id_final = self.repository.generar_siguiente_id()

        nuevo_cliente = Cliente(
            id=id_final,
            nombre=nombre.strip(),
            apellido=apellido.strip(),
            email=email.strip().lower(),
            telefono=telefono.strip(),
            activo=activo
        )

        return self.repository.guardar(nuevo_cliente)

    def modificar_cliente(self, cliente_id: str, cambios: Dict[str, Any]) -> Cliente:
        """
        Modifica la información de un cliente existente.
        Permite actualización parcial o total.
        """
        cliente = self.buscar_por_id(cliente_id)

        nombre = cambios.get("nombre", cliente.nombre)
        apellido = cambios.get("apellido", cliente.apellido)
        email = cambios.get("email", cliente.email)
        telefono = cambios.get("telefono", cliente.telefono)
        activo = cambios.get("activo", cliente.activo)

        self._validar_datos_basicos(nombre, apellido, email, telefono)

        # Si el email cambió, verificar que no esté en uso por otro cliente
        if email.strip().lower() != cliente.email.lower():
            cliente_con_email = self.repository.obtener_por_email(email)
            if cliente_con_email and cliente_con_email.id != cliente.id:
                raise ClienteValidacionError(f"El email '{email}' ya está en uso por otro cliente.")

        # Convertir campo activo si viene en texto
        if isinstance(activo, str):
            activo = activo.strip().lower() in ("true", "1", "t", "yes", "si")

        cliente.nombre = nombre.strip()
        cliente.apellido = apellido.strip()
        cliente.email = email.strip().lower()
        cliente.telefono = telefono.strip()
        cliente.activo = bool(activo)

        resultado = self.repository.actualizar(cliente)
        if not resultado:
            raise ClienteServiceError("Ocurrió un error inesperado al actualizar el cliente en el repositorio.")

        return resultado

    def _validar_datos_basicos(self, nombre: str, apellido: str, email: str, telefono: str) -> None:
        """Valida que los campos obligatorios cumplan con los formatos esperados."""
        if not nombre or not nombre.strip():
            raise ClienteValidacionError("El nombre del cliente no puede estar vacío.")

        if not apellido or not apellido.strip():
            raise ClienteValidacionError("El apellido del cliente no puede estar vacío.")

        if not email or not email.strip():
            raise ClienteValidacionError("El email del cliente no puede estar vacío.")

        patron_email = r"^[\w\.-]+@[\w\.-]+\.\w+$"
        if not re.match(patron_email, email.strip()):
            raise ClienteValidacionError(f"El formato del correo electrónico '{email}' es inválido.")

        if not telefono or not telefono.strip():
            raise ClienteValidacionError("El teléfono del cliente no puede estar vacío.")

    def filtrar_clientes(self, termino: str) -> List[Cliente]:
        """
        Busca clientes por coincidencia parcial en nombre, apellido o email.
        """
        if not termino or not termino.strip():
            return self.listar_clientes()

        termino_norm = termino.strip().lower()
        todos = self.listar_clientes()
        return [
            c for c in todos
            if termino_norm in c.nombre.lower()
            or termino_norm in c.apellido.lower()
            or termino_norm in c.email.lower()
        ]
