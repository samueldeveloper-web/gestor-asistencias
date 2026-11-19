from fastapi import APIRouter, Depends, Query, Request

from app.core.security import usuario_actual
from app.models.personal_institucion import PersonalInstitucion, PersonalInstitucionActualizar
from app.models.comunes import CambioEstado
from app.repositories.personal_institucion_repo import PersonalInstitucionRepository

router = APIRouter(prefix="/personal-institucion", tags=["Personal de la institución"], dependencies=[Depends(usuario_actual)])
repo = PersonalInstitucionRepository()


@router.get("/")
def listar_personal_institucion(request: Request, incluir_inactivos: bool = Query(False)):
    """Lista los registros activos. Acepta filtros por columna: ?columna=valor"""
    filtros = {k: v for k, v in request.query_params.items() if k != "incluir_inactivos"}
    return repo.obtener_todos(solo_activos=not incluir_inactivos, filtros=filtros)


@router.get("/{id_registro}")
def obtener_personal_institucion(id_registro: int):
    return repo.obtener_por_id(id_registro)


@router.post("/", status_code=201)
def crear_personal_institucion(datos: PersonalInstitucion):
    nuevo = repo.crear(datos.model_dump(exclude_unset=True))
    return {"mensaje": "Personal de la institución registrado exitosamente", "id": nuevo[repo.esquema()["pk"]], "data": nuevo}


@router.put("/{id_registro}")
def actualizar_personal_institucion(id_registro: int, datos: PersonalInstitucionActualizar):
    actualizado = repo.actualizar(id_registro, datos.model_dump(exclude_unset=True))
    return {"mensaje": "Personal de la institución actualizado correctamente", "data": actualizado}


@router.delete("/{id_registro}")
def eliminar_personal_institucion(id_registro: int):
    """Borrado lógico: cambia el estado a inactivo, no borra la fila."""
    repo.eliminar(id_registro)
    return {"mensaje": "Personal de la institución desactivado correctamente"}


@router.patch("/{id_registro}/estado")
def cambiar_estado_personal_institucion(id_registro: int, datos: CambioEstado):
    """Activa o desactiva el registro (reactivar lo eliminado)."""
    fila = repo.cambiar_estado(id_registro, datos.esta_activo)
    return {"mensaje": "Estado actualizado", "data": fila}
