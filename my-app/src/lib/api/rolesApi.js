/**
 * Llamadas a la API para roles del sistema (tabla rol).
 * Rutas: GET /roles/ · GET /roles/{id} · POST /roles/ · PUT /roles/{id} · DELETE /roles/{id} (borrado lógico) · PATCH {id}/estado
 */
import { obtenerLista, obtenerJson, enviarJson, actualizarJson, eliminarJson, modificarJson } from './http.js';

const RUTA = '/roles';
/** Nombre de la llave primaria que devuelve la API. Solo se usa internamente, nunca se muestra. */
export const ID_ROL = 'rolid';

const idDe = (filaOId) => (typeof filaOId === 'object' ? filaOId[ID_ROL] : filaOId);

export const listarRoles = () => obtenerLista(`${RUTA}/`);
export const obtenerRol = (filaOId) => obtenerJson(`${RUTA}/${idDe(filaOId)}`);
export const crearRol = (datos) => enviarJson(`${RUTA}/`, datos);
export const actualizarRol = (filaOId, datos) => actualizarJson(`${RUTA}/${idDe(filaOId)}`, datos);
export const eliminarRol = (filaOId) => eliminarJson(`${RUTA}/${idDe(filaOId)}`);

/** Módulos permitidos para un rol (tabla modulo_por_rol). */
export const listarModulosDeRol = (rolid) => obtenerLista(`${RUTA}/${rolid}/modulos`);

/** Reactiva o desactiva el registro (esta_activo). */
export const cambiarEstadoRol = (filaOId, estaActivo) => modificarJson(`${RUTA}/${idDe(filaOId)}/estado`, { esta_activo: estaActivo });

/** Lista filtrada por columnas, ej: { estudianteid: 3 } → GET /roles/?estudianteid=3 */
export const filtrarRoles = (filtros) => obtenerLista(`${RUTA}/?${new URLSearchParams(filtros)}`);
