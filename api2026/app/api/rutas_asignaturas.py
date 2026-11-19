from fastapi import APIRouter, Depends, Query, Request

from app.core.security import usuario_actual
from app.models.asignatura import Asignatura, AsignaturaActualizar
from app.models.comunes import CambioEstado
from app.repositories.asignatura_repo import AsignaturaRepository

router = APIRouter(prefix="/asignaturas", tags=["Asignaturas"], dependencies=[Depends(usuario_actual)])
repo = AsignaturaRepository()


@router.get("/")
def listar_asignatura(request: Request, incluir_inactivos: bool = Query(False)):
    """Lista los registros activos. Acepta filtros por columna: ?columna=valor"""
    filtros = {k: v for k, v in request.query_params.items() if k != "incluir_inactivos"}
    return repo.obtener_todos(solo_activos=not incluir_inactivos, filtros=filtros)


@router.get("/{id_registro}")
def obtener_asignatura(id_registro: int):
    return repo.obtener_por_id(id_registro)


@router.post("/", status_code=201)
def crear_asignatura(datos: Asignatura):
    nuevo = repo.crear(datos.model_dump(exclude_unset=True))
    return {"mensaje": "Asignatura registrado exitosamente", "id": nuevo[repo.esquema()["pk"]], "data": nuevo}


@router.put("/{id_registro}")
def actualizar_asignatura(id_registro: int, datos: AsignaturaActualizar):
    actualizado = repo.actualizar(id_registro, datos.model_dump(exclude_unset=True))
    return {"mensaje": "Asignatura actualizado correctamente", "data": actualizado}


@router.delete("/{id_registro}")
def eliminar_asignatura(id_registro: int):
    """Borrado lógico: cambia el estado a inactivo, no borra la fila."""
    repo.eliminar(id_registro)
    return {"mensaje": "Asignatura desactivado correctamente"}


@router.patch("/{id_registro}/estado")
def cambiar_estado_asignatura(id_registro: int, datos: CambioEstado):
    """Activa o desactiva el registro (reactivar lo eliminado)."""
    fila = repo.cambiar_estado(id_registro, datos.esta_activo)
    return {"mensaje": "Estado actualizado", "data": fila}
