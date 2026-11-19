/**
 * Llamadas a la API para cursos (tabla cursos).
 * Rutas: GET /cursos/ · GET /cursos/{id} · POST /cursos/ · PUT /cursos/{id} · DELETE /cursos/{id} (borrado lógico) · PATCH {id}/estado
 */
import { obtenerLista, obtenerJson, enviarJson, actualizarJson, eliminarJson, modificarJson } from './http.js';

const RUTA = '/cursos';
/** Nombre de la llave primaria que devuelve la API. Solo se usa internamente, nunca se muestra. */
export const ID_CURSO = 'cursoid';

const idDe = (filaOId) => (typeof filaOId === 'object' ? filaOId[ID_CURSO] : filaOId);

export const listarCursos = () => obtenerLista(`${RUTA}/`);
export const obtenerCurso = (filaOId) => obtenerJson(`${RUTA}/${idDe(filaOId)}`);
export const crearCurso = (datos) => enviarJson(`${RUTA}/`, datos);
export const actualizarCurso = (filaOId, datos) => actualizarJson(`${RUTA}/${idDe(filaOId)}`, datos);
export const eliminarCurso = (filaOId) => eliminarJson(`${RUTA}/${idDe(filaOId)}`);

/** Reactiva o desactiva el registro (esta_activo). */
export const cambiarEstadoCurso = (filaOId, estaActivo) => modificarJson(`${RUTA}/${idDe(filaOId)}/estado`, { esta_activo: estaActivo });

/** Lista filtrada por columnas, ej: { estudianteid: 3 } → GET /cursos/?estudianteid=3 */
export const filtrarCursos = (filtros) => obtenerLista(`${RUTA}/?${new URLSearchParams(filtros)}`);
