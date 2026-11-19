/**
 * Llamadas a la API para excusas o justificaciones de fallas (tabla excusas).
 * Rutas: GET /excusas/ · GET /excusas/{id} · POST /excusas/ · PUT /excusas/{id} · DELETE /excusas/{id} (borrado lógico) · PATCH {id}/estado
 */
import { obtenerLista, obtenerJson, enviarJson, actualizarJson, eliminarJson, modificarJson } from './http.js';

const RUTA = '/excusas';
/** Nombre de la llave primaria que devuelve la API. Solo se usa internamente, nunca se muestra. */
export const ID_EXCUSA = 'excusaid';

const idDe = (filaOId) => (typeof filaOId === 'object' ? filaOId[ID_EXCUSA] : filaOId);

export const listarExcusas = () => obtenerLista(`${RUTA}/`);
export const obtenerExcusa = (filaOId) => obtenerJson(`${RUTA}/${idDe(filaOId)}`);
export const crearExcusa = (datos) => enviarJson(`${RUTA}/`, datos);
export const actualizarExcusa = (filaOId, datos) => actualizarJson(`${RUTA}/${idDe(filaOId)}`, datos);
export const eliminarExcusa = (filaOId) => eliminarJson(`${RUTA}/${idDe(filaOId)}`);

/** Reactiva o desactiva el registro (esta_activo). */
export const cambiarEstadoExcusa = (filaOId, estaActivo) => modificarJson(`${RUTA}/${idDe(filaOId)}/estado`, { esta_activo: estaActivo });

/** Lista filtrada por columnas, ej: { estudianteid: 3 } → GET /excusas/?estudianteid=3 */
export const filtrarExcusas = (filtros) => obtenerLista(`${RUTA}/?${new URLSearchParams(filtros)}`);

/** Docente o administrador aprueba/rechaza la excusa. Si se aprueba, la API pasa la asistencia a "excusado". */
export const revisarExcusa = (filaOId, aprobada, observacion = '') => actualizarJson(`${RUTA}/${idDe(filaOId)}/revisar`, { aprobada, observacion });
