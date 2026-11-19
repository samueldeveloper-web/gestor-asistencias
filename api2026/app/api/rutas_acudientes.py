from fastapi import APIRouter, Depends, Query, Request

from app.core.security import usuario_actual
from app.models.acudiente import Acudiente, AcudienteActualizar
from app.models.comunes import CambioEstado
from app.repositories.acudiente_repo import AcudienteRepository

router = APIRouter(prefix="/acudientes", tags=["Acudientes"], dependencies=[Depends(usuario_actual)])
repo = AcudienteRepository()

@router.get("/{id_registro}/estudiantes")
def estudiantes_del_acudiente(id_registro: int):
    """Estudiantes (hijos) vinculados al acudiente."""
    return repo.estudiantes_de(id_registro)


@router.get("/")
def listar_acudiente(request: Request, incluir_inactivos: bool = Query(False)):
    """Lista los registros activos. Acepta filtros por columna: ?columna=valor"""
    filtros = {k: v for k, v in request.query_params.items() if k != "incluir_inactivos"}
    return repo.obtener_todos(solo_activos=not incluir_inactivos, filtros=filtros)


@router.get("/{id_registro}")
def obtener_acudiente(id_registro: int):
    return repo.obtener_por_id(id_registro)


@router.post("/", status_code=201)
def crear_acudiente(datos: Acudiente):
    nuevo = repo.crear(datos.model_dump(exclude_unset=True))
    return {"mensaje": "Acudiente registrado exitosamente", "id": nuevo[repo.esquema()["pk"]], "data": nuevo}


@router.put("/{id_registro}")
def actualizar_acudiente(id_registro: int, datos: AcudienteActualizar):
    actualizado = repo.actualizar(id_registro, datos.model_dump(exclude_unset=True))
    return {"mensaje": "Acudiente actualizado correctamente", "data": actualizado}


@router.delete("/{id_registro}")
def eliminar_acudiente(id_registro: int):
    """Borrado lógico: cambia el estado a inactivo, no borra la fila."""
    repo.eliminar(id_registro)
    return {"mensaje": "Acudiente desactivado correctamente"}


@router.patch("/{id_registro}/estado")
def cambiar_estado_acudiente(id_registro: int, datos: CambioEstado):
    """Activa o desactiva el registro (reactivar lo eliminado)."""
    fila = repo.cambiar_estado(id_registro, datos.esta_activo)
    return {"mensaje": "Estado actualizado", "data": fila}
