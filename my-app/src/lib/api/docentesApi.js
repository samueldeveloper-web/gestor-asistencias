/**
 * Llamadas a la API para docentes y personal (tabla personal_institucional).
 * Rutas: GET /personal-institucion/ · GET /personal-institucion/{id} · POST /personal-institucion/ · PUT /personal-institucion/{id} · DELETE /personal-institucion/{id} (borrado lógico) · PATCH {id}/estado
 */
import { obtenerLista, obtenerJson, enviarJson, actualizarJson, eliminarJson, modificarJson } from './http.js';

const RUTA = '/personal-institucion';
/** Nombre de la llave primaria que devuelve la API. Solo se usa internamente, nunca se muestra. */
export const ID_DOCENTE = 'personalid';

const idDe = (filaOId) => (typeof filaOId === 'object' ? filaOId[ID_DOCENTE] : filaOId);

export const listarDocentes = () => obtenerLista(`${RUTA}/`);
export const obtenerDocente = (filaOId) => obtenerJson(`${RUTA}/${idDe(filaOId)}`);
export const crearDocente = (datos) => enviarJson(`${RUTA}/`, datos);
export const actualizarDocente = (filaOId, datos) => actualizarJson(`${RUTA}/${idDe(filaOId)}`, datos);
export const eliminarDocente = (filaOId) => eliminarJson(`${RUTA}/${idDe(filaOId)}`);

/** Reactiva o desactiva el registro (esta_activo). */
export const cambiarEstadoDocente = (filaOId, estaActivo) => modificarJson(`${RUTA}/${idDe(filaOId)}/estado`, { esta_activo: estaActivo });

/** Lista filtrada por columnas, ej: { estudianteid: 3 } → GET /personal-institucion/?estudianteid=3 */
export const filtrarDocentes = (filtros) => obtenerLista(`${RUTA}/?${new URLSearchParams(filtros)}`);
