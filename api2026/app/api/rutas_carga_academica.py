from fastapi import APIRouter, Depends, Query, Request

from app.core.security import usuario_actual
from app.models.carga_academica import CargaAcademica, CargaAcademicaActualizar
from app.models.comunes import CambioEstado
from app.repositories.carga_academica_repo import CargaAcademicaRepository

router = APIRouter(prefix="/carga-academica", tags=["Carga académica"], dependencies=[Depends(usuario_actual)])
repo = CargaAcademicaRepository()


@router.get("/")
def listar_carga_academica(request: Request, incluir_inactivos: bool = Query(False)):
    """Lista los registros activos. Acepta filtros por columna: ?columna=valor"""
    filtros = {k: v for k, v in request.query_params.items() if k != "incluir_inactivos"}
    return repo.obtener_todos(solo_activos=not incluir_inactivos, filtros=filtros)


@router.get("/{id_registro}")
def obtener_carga_academica(id_registro: int):
    return repo.obtener_por_id(id_registro)


@router.post("/", status_code=201)
def crear_carga_academica(datos: CargaAcademica):
    nuevo = repo.crear(datos.model_dump(exclude_unset=True))
    return {"mensaje": "Carga académica registrado exitosamente", "id": nuevo[repo.esquema()["pk"]], "data": nuevo}


@router.put("/{id_registro}")
def actualizar_carga_academica(id_registro: int, datos: CargaAcademicaActualizar):
    actualizado = repo.actualizar(id_registro, datos.model_dump(exclude_unset=True))
    return {"mensaje": "Carga académica actualizado correctamente", "data": actualizado}


@router.delete("/{id_registro}")
def eliminar_carga_academica(id_registro: int):
    """Borrado lógico: cambia el estado a inactivo, no borra la fila."""
    repo.eliminar(id_registro)
    return {"mensaje": "Carga académica desactivado correctamente"}


@router.patch("/{id_registro}/estado")
def cambiar_estado_carga_academica(id_registro: int, datos: CambioEstado):
    """Activa o desactiva el registro (reactivar lo eliminado)."""
    fila = repo.cambiar_estado(id_registro, datos.esta_activo)
    return {"mensaje": "Estado actualizado", "data": fila}
