/**
 * Llamadas a la API para módulos del menú (tabla modulo).
 * Rutas: GET /modulos/ · GET /modulos/{id} · POST /modulos/ · PUT /modulos/{id} · DELETE /modulos/{id} (borrado lógico) · PATCH {id}/estado
 */
import { obtenerLista, obtenerJson, enviarJson, actualizarJson, eliminarJson, modificarJson } from './http.js';

const RUTA = '/modulos';
/** Nombre de la llave primaria que devuelve la API. Solo se usa internamente, nunca se muestra. */
export const ID_MODULO = 'moduloid';

const idDe = (filaOId) => (typeof filaOId === 'object' ? filaOId[ID_MODULO] : filaOId);

export const listarModulos = () => obtenerLista(`${RUTA}/`);
export const obtenerModulo = (filaOId) => obtenerJson(`${RUTA}/${idDe(filaOId)}`);
export const crearModulo = (datos) => enviarJson(`${RUTA}/`, datos);
export const actualizarModulo = (filaOId, datos) => actualizarJson(`${RUTA}/${idDe(filaOId)}`, datos);
export const eliminarModulo = (filaOId) => eliminarJson(`${RUTA}/${idDe(filaOId)}`);

/** Reactiva o desactiva el registro (esta_activo). */
export const cambiarEstadoModulo = (filaOId, estaActivo) => modificarJson(`${RUTA}/${idDe(filaOId)}/estado`, { esta_activo: estaActivo });

/** Lista filtrada por columnas, ej: { estudianteid: 3 } → GET /modulos/?estudianteid=3 */
export const filtrarModulos = (filtros) => obtenerLista(`${RUTA}/?${new URLSearchParams(filtros)}`);
