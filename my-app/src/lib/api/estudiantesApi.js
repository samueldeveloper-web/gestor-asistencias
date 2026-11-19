/**
 * Llamadas a la API para estudiantes (tabla estudiantes).
 * Rutas: GET /estudiantes/ · GET /estudiantes/{id} · POST /estudiantes/ · PUT /estudiantes/{id} · DELETE /estudiantes/{id} (borrado lógico) · PATCH {id}/estado
 */
import { obtenerLista, obtenerJson, enviarJson, actualizarJson, eliminarJson, modificarJson } from './http.js';

const RUTA = '/estudiantes';
/** Nombre de la llave primaria que devuelve la API. Solo se usa internamente, nunca se muestra. */
export const ID_ESTUDIANTE = 'estudiante_id';

const idDe = (filaOId) => (typeof filaOId === 'object' ? filaOId[ID_ESTUDIANTE] : filaOId);

export const listarEstudiantes = () => obtenerLista(`${RUTA}/`);
export const obtenerEstudiante = (filaOId) => obtenerJson(`${RUTA}/${idDe(filaOId)}`);
export const crearEstudiante = (datos) => enviarJson(`${RUTA}/`, datos);
export const actualizarEstudiante = (filaOId, datos) => actualizarJson(`${RUTA}/${idDe(filaOId)}`, datos);
export const eliminarEstudiante = (filaOId) => eliminarJson(`${RUTA}/${idDe(filaOId)}`);

/** Reactiva o desactiva el registro (esta_activo). */
export const cambiarEstadoEstudiante = (filaOId, estaActivo) => modificarJson(`${RUTA}/${idDe(filaOId)}/estado`, { esta_activo: estaActivo });

/** Lista filtrada por columnas, ej: { estudianteid: 3 } → GET /estudiantes/?estudianteid=3 */
export const filtrarEstudiantes = (filtros) => obtenerLista(`${RUTA}/?${new URLSearchParams(filtros)}`);
