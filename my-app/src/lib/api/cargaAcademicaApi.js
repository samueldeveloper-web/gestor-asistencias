/**
 * Llamadas a la API para asignaciones docente-curso-asignatura (tabla carga_academica).
 * Rutas: GET /carga-academica/ · GET /carga-academica/{id} · POST /carga-academica/ · PUT /carga-academica/{id} · DELETE /carga-academica/{id} (borrado lógico) · PATCH {id}/estado
 */
import { obtenerLista, obtenerJson, enviarJson, actualizarJson, eliminarJson, modificarJson } from './http.js';

const RUTA = '/carga-academica';
/** Nombre de la llave primaria que devuelve la API. Solo se usa internamente, nunca se muestra. */
export const ID_CARGA = 'cargaid';

const idDe = (filaOId) => (typeof filaOId === 'object' ? filaOId[ID_CARGA] : filaOId);

export const listarCargas = () => obtenerLista(`${RUTA}/`);
export const obtenerCarga = (filaOId) => obtenerJson(`${RUTA}/${idDe(filaOId)}`);
export const crearCarga = (datos) => enviarJson(`${RUTA}/`, datos);
export const actualizarCarga = (filaOId, datos) => actualizarJson(`${RUTA}/${idDe(filaOId)}`, datos);
export const eliminarCarga = (filaOId) => eliminarJson(`${RUTA}/${idDe(filaOId)}`);

/** Reactiva o desactiva el registro (esta_activo). */
export const cambiarEstadoCarga = (filaOId, estaActivo) => modificarJson(`${RUTA}/${idDe(filaOId)}/estado`, { esta_activo: estaActivo });

/** Lista filtrada por columnas, ej: { estudianteid: 3 } → GET /carga-academica/?estudianteid=3 */
export const filtrarCargas = (filtros) => obtenerLista(`${RUTA}/?${new URLSearchParams(filtros)}`);
