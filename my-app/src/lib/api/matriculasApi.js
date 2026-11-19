/**
 * Llamadas a la API para matrículas de estudiantes en cursos (tabla matriculas).
 * Rutas: GET /matriculas/ · GET /matriculas/{id} · POST /matriculas/ · PUT /matriculas/{id} · DELETE /matriculas/{id} (borrado lógico) · PATCH {id}/estado
 */
import { obtenerLista, obtenerJson, enviarJson, actualizarJson, eliminarJson, modificarJson } from './http.js';

const RUTA = '/matriculas';
/** Nombre de la llave primaria que devuelve la API. Solo se usa internamente, nunca se muestra. */
export const ID_MATRICULA = 'matriculaid';

const idDe = (filaOId) => (typeof filaOId === 'object' ? filaOId[ID_MATRICULA] : filaOId);

export const listarMatriculas = () => obtenerLista(`${RUTA}/`);
export const obtenerMatricula = (filaOId) => obtenerJson(`${RUTA}/${idDe(filaOId)}`);
export const crearMatricula = (datos) => enviarJson(`${RUTA}/`, datos);
export const actualizarMatricula = (filaOId, datos) => actualizarJson(`${RUTA}/${idDe(filaOId)}`, datos);
export const eliminarMatricula = (filaOId) => eliminarJson(`${RUTA}/${idDe(filaOId)}`);

/** Reactiva o desactiva el registro (esta_activo). */
export const cambiarEstadoMatricula = (filaOId, estaActivo) => modificarJson(`${RUTA}/${idDe(filaOId)}/estado`, { esta_activo: estaActivo });

/** Lista filtrada por columnas, ej: { estudianteid: 3 } → GET /matriculas/?estudianteid=3 */
export const filtrarMatriculas = (filtros) => obtenerLista(`${RUTA}/?${new URLSearchParams(filtros)}`);
