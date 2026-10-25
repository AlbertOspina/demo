from typing import Any, Dict, Optional


class ResponseDTO:
    def __init__(self, code: int, message: str, data: Any = None, total: Optional[int] = None):
        self.code = code
        self.message = message
        self.data = data
        self.total = total

    def to_dict(self) -> Dict[str, Any]:
        response={
            "code": self.code,
            "message": self.message,
            "data": self.data,
            "total": self.total
        }
        return response