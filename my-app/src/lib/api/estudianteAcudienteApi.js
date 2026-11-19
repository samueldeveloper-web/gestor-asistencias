/**
 * Llamadas a la API para vínculos estudiante-acudiente (tabla estudiante_acudiente).
 * Rutas: GET /estudiante-acudiente/ · GET /estudiante-acudiente/{id} · POST /estudiante-acudiente/ · PUT /estudiante-acudiente/{id} · DELETE /estudiante-acudiente/{id} (borrado lógico) · PATCH {id}/estado
 */
import { obtenerLista, obtenerJson, enviarJson, actualizarJson, eliminarJson, modificarJson } from './http.js';

const RUTA = '/estudiante-acudiente';
/** Nombre de la llave primaria que devuelve la API. Solo se usa internamente, nunca se muestra. */
export const ID_VINCULO = 'estudiante_acudienteid';

const idDe = (filaOId) => (typeof filaOId === 'object' ? filaOId[ID_VINCULO] : filaOId);

export const listarVinculos = () => obtenerLista(`${RUTA}/`);
export const obtenerVinculo = (filaOId) => obtenerJson(`${RUTA}/${idDe(filaOId)}`);
export const crearVinculo = (datos) => enviarJson(`${RUTA}/`, datos);
export const actualizarVinculo = (filaOId, datos) => actualizarJson(`${RUTA}/${idDe(filaOId)}`, datos);
export const eliminarVinculo = (filaOId) => eliminarJson(`${RUTA}/${idDe(filaOId)}`);

/** Reactiva o desactiva el registro (esta_activo). */
export const cambiarEstadoVinculo = (filaOId, estaActivo) => modificarJson(`${RUTA}/${idDe(filaOId)}/estado`, { esta_activo: estaActivo });

/** Lista filtrada por columnas, ej: { estudianteid: 3 } → GET /estudiante-acudiente/?estudianteid=3 */
export const filtrarVinculos = (filtros) => obtenerLista(`${RUTA}/?${new URLSearchParams(filtros)}`);
