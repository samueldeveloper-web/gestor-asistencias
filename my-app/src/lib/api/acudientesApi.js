/**
 * Llamadas a la API para acudientes (tabla acudientes).
 * Rutas: GET /acudientes/ · GET /acudientes/{id} · POST /acudientes/ · PUT /acudientes/{id} · DELETE /acudientes/{id} (borrado lógico) · PATCH {id}/estado
 */
import { obtenerLista, obtenerJson, enviarJson, actualizarJson, eliminarJson, modificarJson } from './http.js';

const RUTA = '/acudientes';
/** Nombre de la llave primaria que devuelve la API. Solo se usa internamente, nunca se muestra. */
export const ID_ACUDIENTE = 'acudiente_id';

const idDe = (filaOId) => (typeof filaOId === 'object' ? filaOId[ID_ACUDIENTE] : filaOId);

export const listarAcudientes = () => obtenerLista(`${RUTA}/`);
export const obtenerAcudiente = (filaOId) => obtenerJson(`${RUTA}/${idDe(filaOId)}`);
export const crearAcudiente = (datos) => enviarJson(`${RUTA}/`, datos);
export const actualizarAcudiente = (filaOId, datos) => actualizarJson(`${RUTA}/${idDe(filaOId)}`, datos);
export const eliminarAcudiente = (filaOId) => eliminarJson(`${RUTA}/${idDe(filaOId)}`);

/** Reactiva o desactiva el registro (esta_activo). */
export const cambiarEstadoAcudiente = (filaOId, estaActivo) => modificarJson(`${RUTA}/${idDe(filaOId)}/estado`, { esta_activo: estaActivo });

/** Lista filtrada por columnas, ej: { estudianteid: 3 } → GET /acudientes/?estudianteid=3 */
export const filtrarAcudientes = (filtros) => obtenerLista(`${RUTA}/?${new URLSearchParams(filtros)}`);

/** Hijos del acudiente con parentesco y contacto principal. */
export const listarHijosDeAcudiente = (acudienteId) => obtenerLista(`${RUTA}/${acudienteId}/estudiantes`);
