import logging
import json
from typing import Dict, Any, List, Optional
from app.repositories.gemini_repository import GeminiRepository, GeminiRepositoryError
from app.services.cliente_service import ClienteService, ClienteNoEncontradoError, ClienteValidacionError

logger = logging.getLogger("gemini.ia")


class GeminiServiceError(Exception):
    """Excepción para errores de lógica de negocio en la capa de Gemini."""
    pass


class GeminiService:
    """
    Capa de Servicio para la orquestación de consultas con la IA y ejecución de Tools locales.
    """

    def __init__(
        self,
        gemini_repository: Optional[GeminiRepository] = None,
        cliente_service: Optional[ClienteService] = None
    ):
        self.gemini_repository = gemini_repository or GeminiRepository()
        self.cliente_service = cliente_service or ClienteService()

    def obtener_declaracion_tools(self) -> List[Dict[str, Any]]:
        """Retorna las declaraciones de herramientas compatibles con el API de Gemini."""
        return [
            {
                "function_declarations": [
                    {
                        "name": "listar_clientes",
                        "description": "Obtiene la lista completa de todos los clientes registrados en la base de datos CSV, incluyendo su ID, nombre, apellido, email, teléfono y estado activo.",
                        "parameters": {
                            "type": "OBJECT",
                            "properties": {}
                        }
                    },
                    {
                        "name": "buscar_cliente_por_id",
                        "description": "Busca un cliente específico mediante su identificador numérico o alfanumérico (ID).",
                        "parameters": {
                            "type": "OBJECT",
                            "properties": {
                                "cliente_id": {
                                    "type": "STRING",
                                    "description": "El ID del cliente a consultar (ej: '1', '2')."
                                }
                            },
                            "required": ["cliente_id"]
                        }
                    },
                    {
                        "name": "filtrar_clientes",
                        "description": "Busca y filtra clientes que contengan una palabra o término clave en su nombre, apellido o dirección de correo electrónico.",
                        "parameters": {
                            "type": "OBJECT",
                            "properties": {
                                "termino": {
                                    "type": "STRING",
                                    "description": "Texto o término de búsqueda a filtrar (ej: 'Maria', 'gmail.com', 'Perez')."
                                }
                            },
                            "required": ["termino"]
                        }
                    }
                ]
            }
        ]

    def ejecutar_tool(self, nombre: str, args: Dict[str, Any], conversacion_id: str) -> Any:
        """
        Ejecuta una herramienta local usando la capa ClienteService y registra logs detallados.
        """
        logger.info(
            f"\n-------------------- [TOOL EXECUTION | CONV: {conversacion_id}] --------------------\n"
            f"Herramienta: {nombre}\n"
            f"Argumentos: {json.dumps(args, ensure_ascii=False)}\n"
            f"----------------------------------------------------------------------------------"
        )

        try:
            if nombre == "listar_clientes":
                clientes = self.cliente_service.listar_clientes()
                resultado = [c.to_dict() for c in clientes]

            elif nombre == "buscar_cliente_por_id":
                cliente_id = str(args.get("cliente_id", "")).strip()
                cliente = self.cliente_service.buscar_por_id(cliente_id)
                resultado = cliente.to_dict()

            elif nombre == "filtrar_clientes":
                termino = str(args.get("termino", "")).strip()
                clientes = self.cliente_service.filtrar_clientes(termino)
                resultado = [c.to_dict() for c in clientes]

            else:
                resultado = {"error": f"Herramienta desconocida: {nombre}"}

        except ClienteNoEncontradoError as e:
            resultado = {"error": str(e), "encontrado": False}
        except ClienteValidacionError as e:
            resultado = {"error": str(e), "valido": False}
        except Exception as e:
            logger.error(f"[{conversacion_id}] Error al ejecutar tool '{nombre}': {str(e)}")
            resultado = {"error": f"Excepción en herramienta: {str(e)}"}

        logger.info(
            f"\n-------------------- [TOOL RESULT | CONV: {conversacion_id}] --------------------\n"
            f"Herramienta: {nombre}\n"
            f"Resultado: {json.dumps(resultado, indent=2, ensure_ascii=False)}\n"
            f"----------------------------------------------------------------------------------"
        )
        return resultado

    def procesar_consulta(self, mensaje: str, conversacion_id: str) -> Dict[str, Any]:
        """
        Orquesta el ciclo conversacional de Function Calling con la API de Gemini:
        1. Envía el mensaje con las herramientas declaradas.
        2. Si Gemini solicita llamada a tool, la ejecuta localmente y envía la respuesta.
        3. Retorna la respuesta final en lenguaje natural junto con el registro de herramientas usadas.
        """
        if not mensaje or not mensaje.strip():
            raise GeminiServiceError("El mensaje de consulta no puede estar vacío.")

        tools = self.obtener_declaracion_tools()
        contents: List[Dict[str, Any]] = [
            {
                "role": "user",
                "parts": [{"text": mensaje.strip()}]
            }
        ]

        herramientas_utilizadas: List[Dict[str, Any]] = []
        max_iteraciones = 5
        iteracion = 0

        while iteracion < max_iteraciones:
            iteracion += 1

            payload = {
                "contents": contents,
                "tools": tools,
                "systemInstruction": {
                    "parts": [
                        {
                            "text": (
                                "Eres un asistente virtual especializado en responder consultas sobre los datos de los clientes "
                                "almacenados en el archivo CSV del sistema. Utiliza siempre las herramientas proporcionadas "
                                "para consultar la información verídica y responde de manera amable, clara y en español."
                            )
                        }
                    ]
                }
            }

            try:
                response_gemini = self.gemini_repository.generar_contenido(payload, conversacion_id=conversacion_id)
            except GeminiRepositoryError as e:
                raise GeminiServiceError(str(e))

            candidates = response_gemini.get("candidates", [])
            if not candidates:
                raise GeminiServiceError("La API de Gemini no devolvió ningún candidato de respuesta.")

            candidate = candidates[0]
            content = candidate.get("content", {})
            parts = content.get("parts", [])

            # Agregar la respuesta del modelo al historial de contents
            contents.append(content)

            # Verificar si el modelo solicitó invocar alguna función (tool)
            tool_calls = [p.get("functionCall") for p in parts if "functionCall" in p]

            if not tool_calls:
                # El modelo ya generó su respuesta final en texto
                textos = [p.get("text", "") for p in parts if "text" in p]
                respuesta_final = "\n".join(textos).strip()
                return {
                    "conversacion_id": conversacion_id,
                    "mensaje": mensaje,
                    "respuesta": respuesta_final,
                    "herramientas_utilizadas": herramientas_utilizadas,
                    "total_herramientas": len(herramientas_utilizadas)
                }

            # Procesar las llamadas a funciones solicitadas por Gemini
            function_response_parts = []
            for tc in tool_calls:
                fn_name = tc.get("name")
                fn_args = tc.get("args", {})

                # Ejecutar la tool en nuestra capa de servicios
                resultado = self.ejecutar_tool(fn_name, fn_args, conversacion_id=conversacion_id)
                herramientas_utilizadas.append({
                    "nombre": fn_name,
                    "argumentos": fn_args,
                    "resultado": resultado
                })

                function_response_parts.append({
                    "functionResponse": {
                        "name": fn_name,
                        "response": {
                            "name": fn_name,
                            "content": resultado
                        }
                    }
                })

            # Añadir la respuesta de la función como rol "user" para Gemini
            contents.append({
                "role": "user",
                "parts": function_response_parts
            })

        raise GeminiServiceError("Se excedió el número máximo de ciclos de llamadas a herramientas (tools).")
