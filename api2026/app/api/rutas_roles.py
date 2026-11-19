from fastapi import APIRouter, Depends, Query, Request

from app.core.security import usuario_actual
from app.models.rol import Rol, RolActualizar
from app.models.comunes import CambioEstado
from app.repositories.rol_repo import RolRepository

router = APIRouter(prefix="/roles", tags=["Roles"])
protegido = [Depends(usuario_actual)]
repo = RolRepository()

@router.get("/{id_registro}/modulos", dependencies=protegido)
def modulos_del_rol(id_registro: int):
    """Módulos que el rol puede ver, según la tabla modulo_por_rol (con sus permisos)."""
    return repo.modulos_de_rol(id_registro)


@router.get("/")
def listar_rol(request: Request, incluir_inactivos: bool = Query(False)):
    """Público (sin token): lo usa el select de rol del login. Lista los roles activos. Acepta filtros por columna: ?columna=valor"""
    filtros = {k: v for k, v in request.query_params.items() if k != "incluir_inactivos"}
    return repo.obtener_todos(solo_activos=not incluir_inactivos, filtros=filtros)


@router.get("/{id_registro}", dependencies=protegido)
def obtener_rol(id_registro: int):
    return repo.obtener_por_id(id_registro)


@router.post("/", status_code=201, dependencies=protegido)
def crear_rol(datos: Rol):
    nuevo = repo.crear(datos.model_dump(exclude_unset=True))
    return {"mensaje": "Rol registrado exitosamente", "id": nuevo[repo.esquema()["pk"]], "data": nuevo}


@router.put("/{id_registro}", dependencies=protegido)
def actualizar_rol(id_registro: int, datos: RolActualizar):
    actualizado = repo.actualizar(id_registro, datos.model_dump(exclude_unset=True))
    return {"mensaje": "Rol actualizado correctamente", "data": actualizado}


@router.delete("/{id_registro}", dependencies=protegido)
def eliminar_rol(id_registro: int):
    """Borrado lógico: cambia el estado a inactivo, no borra la fila."""
    repo.eliminar(id_registro)
    return {"mensaje": "Rol desactivado correctamente"}


@router.patch("/{id_registro}/estado", dependencies=protegido)
def cambiar_estado_rol(id_registro: int, datos: CambioEstado):
    """Activa o desactiva el registro (reactivar lo eliminado)."""
    fila = repo.cambiar_estado(id_registro, datos.esta_activo)
    return {"mensaje": "Estado actualizado", "data": fila}
