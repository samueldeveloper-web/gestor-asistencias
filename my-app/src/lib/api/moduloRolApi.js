/**
 * Llamadas a la API para permisos de cada rol (tabla modulo_por_rol).
 * Rutas: GET /modulo-por-rol/ · GET /modulo-por-rol/{id} · POST /modulo-por-rol/ · PUT /modulo-por-rol/{id} · DELETE /modulo-por-rol/{id} (borrado lógico) · PATCH {id}/estado
 */
import { obtenerLista, obtenerJson, enviarJson, actualizarJson, eliminarJson, modificarJson } from './http.js';

const RUTA = '/modulo-por-rol';
/** Nombre de la llave primaria que devuelve la API. Solo se usa internamente, nunca se muestra. */
export const ID_MODULOROL = 'modulo_por_rolid';

const idDe = (filaOId) => (typeof filaOId === 'object' ? filaOId[ID_MODULOROL] : filaOId);

export const listarModulosRol = () => obtenerLista(`${RUTA}/`);
export const obtenerModuloRol = (filaOId) => obtenerJson(`${RUTA}/${idDe(filaOId)}`);
export const crearModuloRol = (datos) => enviarJson(`${RUTA}/`, datos);
export const actualizarModuloRol = (filaOId, datos) => actualizarJson(`${RUTA}/${idDe(filaOId)}`, datos);
export const eliminarModuloRol = (filaOId) => eliminarJson(`${RUTA}/${idDe(filaOId)}`);

/** Reactiva o desactiva el registro (esta_activo). */
export const cambiarEstadoModuloRol = (filaOId, estaActivo) => modificarJson(`${RUTA}/${idDe(filaOId)}/estado`, { esta_activo: estaActivo });

/** Lista filtrada por columnas, ej: { estudianteid: 3 } → GET /modulo-por-rol/?estudianteid=3 */
export const filtrarModulosRol = (filtros) => obtenerLista(`${RUTA}/?${new URLSearchParams(filtros)}`);
