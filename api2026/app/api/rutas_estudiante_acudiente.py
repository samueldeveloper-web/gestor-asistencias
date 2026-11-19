from fastapi import APIRouter, Depends, Query, Request

from app.core.security import usuario_actual
from app.models.estudiante_acudiente import EstudianteAcudiente, EstudianteAcudienteActualizar
from app.models.comunes import CambioEstado
from app.repositories.estudiante_acudiente_repo import EstudianteAcudienteRepository

router = APIRouter(prefix="/estudiante-acudiente", tags=["Estudiante - Acudiente"], dependencies=[Depends(usuario_actual)])
repo = EstudianteAcudienteRepository()


@router.get("/")
def listar_estudiante_acudiente(request: Request, incluir_inactivos: bool = Query(False)):
    """Lista los registros activos. Acepta filtros por columna: ?columna=valor"""
    filtros = {k: v for k, v in request.query_params.items() if k != "incluir_inactivos"}
    return repo.obtener_todos(solo_activos=not incluir_inactivos, filtros=filtros)


@router.get("/{id_registro}")
def obtener_estudiante_acudiente(id_registro: int):
    return repo.obtener_por_id(id_registro)


@router.post("/", status_code=201)
def crear_estudiante_acudiente(datos: EstudianteAcudiente):
    nuevo = repo.crear(datos.model_dump(exclude_unset=True))
    return {"mensaje": "Vínculo estudiante-acudiente registrado exitosamente", "id": nuevo[repo.esquema()["pk"]], "data": nuevo}


@router.put("/{id_registro}")
def actualizar_estudiante_acudiente(id_registro: int, datos: EstudianteAcudienteActualizar):
    actualizado = repo.actualizar(id_registro, datos.model_dump(exclude_unset=True))
    return {"mensaje": "Vínculo estudiante-acudiente actualizado correctamente", "data": actualizado}


@router.delete("/{id_registro}")
def eliminar_estudiante_acudiente(id_registro: int):
    """Borrado lógico: cambia el estado a inactivo, no borra la fila."""
    repo.eliminar(id_registro)
    return {"mensaje": "Vínculo estudiante-acudiente desactivado correctamente"}


@router.patch("/{id_registro}/estado")
def cambiar_estado_estudiante_acudiente(id_registro: int, datos: CambioEstado):
    """Activa o desactiva el registro (reactivar lo eliminado)."""
    fila = repo.cambiar_estado(id_registro, datos.esta_activo)
    return {"mensaje": "Estado actualizado", "data": fila}
