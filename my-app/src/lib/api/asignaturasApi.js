/**
 * Llamadas a la API para asignaturas (tabla asignaturas).
 * Rutas: GET /asignaturas/ · GET /asignaturas/{id} · POST /asignaturas/ · PUT /asignaturas/{id} · DELETE /asignaturas/{id} (borrado lógico) · PATCH {id}/estado
 */
import { obtenerLista, obtenerJson, enviarJson, actualizarJson, eliminarJson, modificarJson } from './http.js';

const RUTA = '/asignaturas';
/** Nombre de la llave primaria que devuelve la API. Solo se usa internamente, nunca se muestra. */
export const ID_ASIGNATURA = 'materiaid';

const idDe = (filaOId) => (typeof filaOId === 'object' ? filaOId[ID_ASIGNATURA] : filaOId);

export const listarAsignaturas = () => obtenerLista(`${RUTA}/`);
export const obtenerAsignatura = (filaOId) => obtenerJson(`${RUTA}/${idDe(filaOId)}`);
export const crearAsignatura = (datos) => enviarJson(`${RUTA}/`, datos);
export const actualizarAsignatura = (filaOId, datos) => actualizarJson(`${RUTA}/${idDe(filaOId)}`, datos);
export const eliminarAsignatura = (filaOId) => eliminarJson(`${RUTA}/${idDe(filaOId)}`);

/** Reactiva o desactiva el registro (esta_activo). */
export const cambiarEstadoAsignatura = (filaOId, estaActivo) => modificarJson(`${RUTA}/${idDe(filaOId)}/estado`, { esta_activo: estaActivo });

/** Lista filtrada por columnas, ej: { estudianteid: 3 } → GET /asignaturas/?estudianteid=3 */
export const filtrarAsignaturas = (filtros) => obtenerLista(`${RUTA}/?${new URLSearchParams(filtros)}`);
