from fastapi import APIRouter, Depends, Query, Request

from app.core.security import usuario_actual
from app.models.notificacion import Notificacion, NotificacionActualizar
from app.models.comunes import CambioEstado, MarcarLeida
from app.repositories.notificacion_repo import NotificacionRepository

router = APIRouter(prefix="/notificaciones", tags=["Notificaciones"], dependencies=[Depends(usuario_actual)])
repo = NotificacionRepository()

@router.get("/pendientes")
def notificaciones_pendientes():
    """Notificaciones que aún no se han enviado por correo."""
    return repo.pendientes()


@router.post("/enviar-pendientes")
def enviar_notificaciones_pendientes():
    """Envía por correo a los acudientes todas las notificaciones pendientes."""
    return repo.enviar_pendientes()


@router.patch("/{id_registro}/leida")
def marcar_notificacion_leida(id_registro: int, datos: MarcarLeida):
    return {"mensaje": "Notificación actualizada", "data": repo.marcar_leida(id_registro, datos.leida)}


@router.get("/")
def listar_notificacion(request: Request, incluir_inactivos: bool = Query(False)):
    """Lista los registros activos. Acepta filtros por columna: ?columna=valor"""
    filtros = {k: v for k, v in request.query_params.items() if k != "incluir_inactivos"}
    return repo.obtener_todos(solo_activos=not incluir_inactivos, filtros=filtros)


@router.get("/{id_registro}")
def obtener_notificacion(id_registro: int):
    return repo.obtener_por_id(id_registro)


@router.post("/", status_code=201)
def crear_notificacion(datos: Notificacion):
    nuevo = repo.crear(datos.model_dump(exclude_unset=True))
    return {"mensaje": "Notificación registrado exitosamente", "id": nuevo[repo.esquema()["pk"]], "data": nuevo}


@router.put("/{id_registro}")
def actualizar_notificacion(id_registro: int, datos: NotificacionActualizar):
    actualizado = repo.actualizar(id_registro, datos.model_dump(exclude_unset=True))
    return {"mensaje": "Notificación actualizado correctamente", "data": actualizado}


@router.delete("/{id_registro}")
def eliminar_notificacion(id_registro: int):
    """Borrado lógico: cambia el estado a inactivo, no borra la fila."""
    repo.eliminar(id_registro)
    return {"mensaje": "Notificación desactivado correctamente"}


@router.patch("/{id_registro}/estado")
def cambiar_estado_notificacion(id_registro: int, datos: CambioEstado):
    """Activa o desactiva el registro (reactivar lo eliminado)."""
    fila = repo.cambiar_estado(id_registro, datos.esta_activo)
    return {"mensaje": "Estado actualizado", "data": fila}
