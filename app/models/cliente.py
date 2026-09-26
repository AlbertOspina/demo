from dataclasses import dataclass
from typing import Dict, Any


@dataclass
class Cliente:
    id: str
    nombre: str
    apellido: str
    email: str
    telefono: str
    activo: bool = True

    def to_dict(self) -> Dict[str, Any]:
        """Convierte la entidad a un diccionario serializable para CSV."""
        return {
            "id": self.id,
            "nombre": self.nombre,
            "apellido": self.apellido,
            "email": self.email,
            "telefono": self.telefono,
            "activo": str(self.activo),
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Cliente":
        """Crea una instancia de Cliente a partir de un diccionario."""
        activo_raw = str(data.get("activo", "True")).strip().lower()
        activo = activo_raw in ("true", "1", "t", "yes", "si")
        return cls(
            id=str(data.get("id", "")).strip(),
            nombre=str(data.get("nombre", "")).strip(),
            apellido=str(data.get("apellido", "")).strip(),
            email=str(data.get("email", "")).strip(),
            telefono=str(data.get("telefono", "")).strip(),
            activo=activo,
        )
