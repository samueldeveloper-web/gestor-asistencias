"""Manejo centralizado de errores: traduce errores de PostgreSQL a respuestas HTTP claras."""
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from psycopg2 import errors as pg


class ErrorApi(Exception):
    def __init__(self, status_code: int, detalle: str):
        self.status_code = status_code
        self.detalle = detalle
        super().__init__(detalle)


class RecursoNoEncontrado(ErrorApi):
    def __init__(self, recurso: str = "Registro"):
        super().__init__(404, f"{recurso} no encontrado")


class ConflictoDatos(ErrorApi):
    def __init__(self, detalle: str):
        super().__init__(409, detalle)


class DatosInvalidos(ErrorApi):
    def __init__(self, detalle: str):
        super().__init__(422, detalle)


class BaseDatosNoDisponible(ErrorApi):
    def __init__(self):
        super().__init__(503, "No hay conexión con la base de datos. Revisa el archivo .env")


def traducir_error_bd(e: Exception) -> ErrorApi:
    """Convierte una excepción de psycopg2 en un ErrorApi con mensaje en español."""
    diag = getattr(e, "diag", None)
    restriccion = getattr(diag, "constraint_name", None) or ""
    columna = getattr(diag, "column_name", None) or ""
    if isinstance(e, pg.UniqueViolation):
        return ConflictoDatos(f"Ya existe un registro con esos datos (restricción {restriccion}).")
    if isinstance(e, pg.ForeignKeyViolation):
        return ConflictoDatos(f"El registro relacionado no existe o está en uso (restricción {restriccion}).")
    if isinstance(e, pg.NotNullViolation):
        return DatosInvalidos(f"El campo '{columna}' es obligatorio.")
    if isinstance(e, pg.CheckViolation):
        return DatosInvalidos(f"Un valor no cumple las reglas de la tabla (restricción {restriccion}).")
    if isinstance(e, (pg.InvalidTextRepresentation, pg.DatetimeFieldOverflow,
                      pg.InvalidDatetimeFormat, pg.NumericValueOutOfRange, pg.StringDataRightTruncation)):
        return DatosInvalidos("Algún valor tiene un formato o tamaño no válido.")
    if isinstance(e, pg.RaiseException):
        # Mensajes lanzados por triggers/funciones de la BD (RAISE EXCEPTION)
        return DatosInvalidos(getattr(diag, "message_primary", None) or str(e))
    return ErrorApi(500, f"Error de base de datos: {getattr(diag, 'message_primary', None) or e}")


def registrar_manejadores(app: FastAPI) -> None:
    @app.exception_handler(ErrorApi)
    async def _error_api(_: Request, exc: ErrorApi):
        return JSONResponse(status_code=exc.status_code, content={"detail": exc.detalle})

    @app.exception_handler(Exception)
    async def _error_general(_: Request, exc: Exception):
        print(f"Error no controlado: {exc!r}")
        return JSONResponse(status_code=500, content={"detail": "Error interno del servidor"})
