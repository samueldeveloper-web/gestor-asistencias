/**
 * Llamadas a la API para registros de asistencia (tabla asistencia).
 * Rutas: GET /asistencia/ · GET /asistencia/{id} · POST /asistencia/ · PUT /asistencia/{id} · DELETE /asistencia/{id} (borrado lógico) · PATCH {id}/estado
 */
import { obtenerLista, obtenerJson, enviarJson, actualizarJson, eliminarJson, modificarJson } from './http.js';

const RUTA = '/asistencia';
/** Nombre de la llave primaria que devuelve la API. Solo se usa internamente, nunca se muestra. */
export const ID_ASISTENCIA = 'asistenciaid';

const idDe = (filaOId) => (typeof filaOId === 'object' ? filaOId[ID_ASISTENCIA] : filaOId);

export const listarAsistencias = () => obtenerLista(`${RUTA}/`);
export const obtenerAsistencia = (filaOId) => obtenerJson(`${RUTA}/${idDe(filaOId)}`);
export const crearAsistencia = (datos) => enviarJson(`${RUTA}/`, datos);
export const actualizarAsistencia = (filaOId, datos) => actualizarJson(`${RUTA}/${idDe(filaOId)}`, datos);
export const eliminarAsistencia = (filaOId) => eliminarJson(`${RUTA}/${idDe(filaOId)}`);

/** Reactiva o desactiva el registro (esta_activo). */
export const cambiarEstadoAsistencia = (filaOId, estaActivo) => modificarJson(`${RUTA}/${idDe(filaOId)}/estado`, { esta_activo: estaActivo });

/** Lista filtrada por columnas, ej: { estudianteid: 3 } → GET /asistencia/?estudianteid=3 */
export const filtrarAsistencias = (filtros) => obtenerLista(`${RUTA}/?${new URLSearchParams(filtros)}`);
