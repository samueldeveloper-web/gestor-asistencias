/**
 * Llamadas a la API para cuentas de acceso (tabla usuario).
 * Rutas: GET /usuarios/ · GET /usuarios/{id} · POST /usuarios/ · PUT /usuarios/{id} · DELETE /usuarios/{id} (borrado lógico) · PATCH {id}/estado
 */
import { obtenerLista, obtenerJson, enviarJson, actualizarJson, eliminarJson, modificarJson } from './http.js';

const RUTA = '/usuarios';
/** Nombre de la llave primaria que devuelve la API. Solo se usa internamente, nunca se muestra. */
export const ID_USUARIO = 'usuarioid';

const idDe = (filaOId) => (typeof filaOId === 'object' ? filaOId[ID_USUARIO] : filaOId);

export const listarUsuarios = () => obtenerLista(`${RUTA}/`);
export const obtenerUsuario = (filaOId) => obtenerJson(`${RUTA}/${idDe(filaOId)}`);
export const crearUsuario = (datos) => enviarJson(`${RUTA}/`, datos);
export const actualizarUsuario = (filaOId, datos) => actualizarJson(`${RUTA}/${idDe(filaOId)}`, datos);
export const eliminarUsuario = (filaOId) => eliminarJson(`${RUTA}/${idDe(filaOId)}`);

/** Reactiva o desactiva el registro (esta_activo). */
export const cambiarEstadoUsuario = (filaOId, estaActivo) => modificarJson(`${RUTA}/${idDe(filaOId)}/estado`, { esta_activo: estaActivo });

/** Lista filtrada por columnas, ej: { estudianteid: 3 } → GET /usuarios/?estudianteid=3 */
export const filtrarUsuarios = (filtros) => obtenerLista(`${RUTA}/?${new URLSearchParams(filtros)}`);
