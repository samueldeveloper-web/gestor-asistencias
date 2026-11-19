/**
 * Llamadas a la API para notificaciones a acudientes (tabla notificaciones).
 * Rutas: GET /notificaciones/ · GET /notificaciones/{id} · POST /notificaciones/ · PUT /notificaciones/{id} · DELETE /notificaciones/{id} (borrado lógico) · PATCH {id}/estado
 */
import { obtenerLista, obtenerJson, enviarJson, actualizarJson, eliminarJson, modificarJson } from './http.js';

const RUTA = '/notificaciones';
/** Nombre de la llave primaria que devuelve la API. Solo se usa internamente, nunca se muestra. */
export const ID_NOTIFICACION = 'notificacionid';

const idDe = (filaOId) => (typeof filaOId === 'object' ? filaOId[ID_NOTIFICACION] : filaOId);

export const listarNotificaciones = () => obtenerLista(`${RUTA}/`);
export const obtenerNotificacion = (filaOId) => obtenerJson(`${RUTA}/${idDe(filaOId)}`);
export const crearNotificacion = (datos) => enviarJson(`${RUTA}/`, datos);
export const actualizarNotificacion = (filaOId, datos) => actualizarJson(`${RUTA}/${idDe(filaOId)}`, datos);
export const eliminarNotificacion = (filaOId) => eliminarJson(`${RUTA}/${idDe(filaOId)}`);

/** Reactiva o desactiva el registro (esta_activo). */
export const cambiarEstadoNotificacion = (filaOId, estaActivo) => modificarJson(`${RUTA}/${idDe(filaOId)}/estado`, { esta_activo: estaActivo });

/** Lista filtrada por columnas, ej: { estudianteid: 3 } → GET /notificaciones/?estudianteid=3 */
export const filtrarNotificaciones = (filtros) => obtenerLista(`${RUTA}/?${new URLSearchParams(filtros)}`);

/** El acudiente marca la notificación como leída. */
export const marcarNotificacionLeida = (filaOId, leida = true) => modificarJson(`${RUTA}/${idDe(filaOId)}/leida`, { leida });

/** Envía por correo las notificaciones pendientes. Devuelve { pendientes, enviadas, fallidas, sin_correo }. */
export const enviarNotificacionesPendientes = () => enviarJson(`${RUTA}/enviar-pendientes`, {});
