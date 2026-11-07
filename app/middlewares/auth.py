import os
from functools import wraps
from flask import request, jsonify
from app.models import ResponseDTO

AUTH_HEADER_NAME = "Demo-Api-Auth"
AUTH_ENV_VAR = "DEMO_API_AUTH"


def autenticar_peticion():
    """
    Verifica que el header 'Demo-Api-Auth' esté presente y coincida con la variable de entorno DEMO_API_AUTH.
    Retorna None si la autenticación es exitosa, o una tupla (Response, status_code) con error 401 si falla.
    """
    token_esperado = os.environ.get(AUTH_ENV_VAR, "").strip()

    # Si no se ha configurado la variable de entorno, denegar por seguridad
    if not token_esperado:
        response_dto = ResponseDTO(
            code=401,
            message="Autenticación no configurada en el servidor (DEMO_API_AUTH no definida).",
            data=None,
            total=None
        )
        return jsonify(response_dto.to_dict()), 401

    token_recibido = request.headers.get(AUTH_HEADER_NAME, "").strip()

    if not token_recibido:
        response_dto = ResponseDTO(
            code=401,
            message=f"Cabecera de autenticación '{AUTH_HEADER_NAME}' no proporcionada.",
            data=None,
            total=None
        )
        return jsonify(response_dto.to_dict()), 401

    if token_recibido != token_esperado:
        response_dto = ResponseDTO(
            code=401,
            message=f"Cabecera de autenticación '{AUTH_HEADER_NAME}' inválida.",
            data=None,
            total=None
        )
        return jsonify(response_dto.to_dict()), 401

    return None


def requiere_autenticacion(f):
    """
    Decorador para endpoints que requieren autenticación mediante el header 'Demo-Api-Auth'.
    """
    @wraps(f)
    def decorador(*args, **kwargs):
        error_auth = autenticar_peticion()
        if error_auth:
            return error_auth
        return f(*args, **kwargs)
    return decorador
