/**
 * Llamadas a la API para los parámetros institucionales (tabla configuracion_institucional).
 * La llave es el texto "clave" (por ejemplo: tablero_powerbi_url).
 * Rutas: GET /configuracion/ · GET /configuracion/{clave} · POST /configuracion/ · PUT /configuracion/{clave}
 */
import { obtenerLista, obtenerJson, enviarJson, actualizarJson } from './http.js';

const RUTA = '/configuracion';

export const listarParametros = () => obtenerLista(`${RUTA}/`);

/** Devuelve el valor del parámetro o null si no existe. */
export async function obtenerParametro(clave) {
	try {
		const fila = await obtenerJson(`${RUTA}/${encodeURIComponent(clave)}`);
		return fila?.esta_activo === false ? null : (fila?.valor ?? null);
	} catch (error) {
		if (error.estado === 404) return null;
		throw error;
	}
}

/** Actualiza el parámetro y, si todavía no existe, lo crea. */
export async function guardarParametro(clave, valor) {
	try {
		return await actualizarJson(`${RUTA}/${encodeURIComponent(clave)}`, { valor });
	} catch (error) {
		if (error.estado !== 404) throw error;
		return enviarJson(`${RUTA}/`, { clave, valor });
	}
}
