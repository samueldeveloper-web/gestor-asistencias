from fastapi import APIRouter, Depends, Query, Request

from app.core.security import usuario_actual
from app.models.modulo_por_rol import ModuloPorRol, ModuloPorRolActualizar
from app.models.comunes import CambioEstado
from app.repositories.modulo_por_rol_repo import ModuloPorRolRepository

router = APIRouter(prefix="/modulo-por-rol", tags=["Módulos por rol"], dependencies=[Depends(usuario_actual)])
repo = ModuloPorRolRepository()


@router.get("/")
def listar_modulo_por_rol(request: Request, incluir_inactivos: bool = Query(False)):
    """Lista los registros activos. Acepta filtros por columna: ?columna=valor"""
    filtros = {k: v for k, v in request.query_params.items() if k != "incluir_inactivos"}
    return repo.obtener_todos(solo_activos=not incluir_inactivos, filtros=filtros)


@router.get("/{id_registro}")
def obtener_modulo_por_rol(id_registro: int):
    return repo.obtener_por_id(id_registro)


@router.post("/", status_code=201)
def crear_modulo_por_rol(datos: ModuloPorRol):
    nuevo = repo.crear(datos.model_dump(exclude_unset=True))
    return {"mensaje": "Permiso de módulo registrado exitosamente", "id": nuevo[repo.esquema()["pk"]], "data": nuevo}


@router.put("/{id_registro}")
def actualizar_modulo_por_rol(id_registro: int, datos: ModuloPorRolActualizar):
    actualizado = repo.actualizar(id_registro, datos.model_dump(exclude_unset=True))
    return {"mensaje": "Permiso de módulo actualizado correctamente", "data": actualizado}


@router.delete("/{id_registro}")
def eliminar_modulo_por_rol(id_registro: int):
    """Borrado lógico: cambia el estado a inactivo, no borra la fila."""
    repo.eliminar(id_registro)
    return {"mensaje": "Permiso de módulo desactivado correctamente"}


@router.patch("/{id_registro}/estado")
def cambiar_estado_modulo_por_rol(id_registro: int, datos: CambioEstado):
    """Activa o desactiva el registro (reactivar lo eliminado)."""
    fila = repo.cambiar_estado(id_registro, datos.esta_activo)
    return {"mensaje": "Estado actualizado", "data": fila}
