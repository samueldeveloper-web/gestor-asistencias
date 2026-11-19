/**
 * Funciones HTTP centralizadas.
 * Es el único archivo que conoce la URL de la API y usa fetch().
 * Los archivos <recurso>Api.js llaman a estas funciones.
 */
const API_URL = (import.meta.env.VITE_API_BASE_URL ?? 'http://127.0.0.1:8000').replace(/\/$/, '');

export class ErrorApi extends Error {
	constructor(mensaje, estado) {
		super(mensaje);
		this.name = 'ErrorApi';
		this.estado = estado;
	}
}

function leerToken() {
	if (typeof window === 'undefined') return null;
	return window.localStorage.getItem('token');
}

/** Convierte el "detail" de FastAPI en un mensaje legible. */
function mensajeDeError(cuerpo, estado) {
	if (!cuerpo) return `Error de la API (${estado})`;
	const detalle = cuerpo.detail ?? cuerpo.mensaje ?? cuerpo.message;
	if (Array.isArray(detalle)) {
		return detalle.map((d) => `${(d.loc ?? []).slice(-1)[0] ?? 'dato'}: ${d.msg}`).join(' · ');
	}
	return typeof detalle === 'string' ? detalle : `Error de la API (${estado})`;
}

export async function peticion(ruta, metodo = 'GET', datos = undefined) {
	const token = leerToken();
	const opciones = {
		method: metodo,
		headers: {
			Accept: 'application/json',
			...(datos !== undefined ? { 'Content-Type': 'application/json' } : {}),
			...(token ? { Authorization: `Bearer ${token}` } : {})
		},
		...(datos !== undefined ? { body: JSON.stringify(datos) } : {})
	};

	let respuesta;
	try {
		respuesta = await fetch(`${API_URL}${ruta}`, opciones);
	} catch {
		throw new ErrorApi('No hay conexión con la API. Verifica que esté encendida.', 0);
	}

	const texto = await respuesta.text();
	let cuerpo = null;
	try {
		cuerpo = texto ? JSON.parse(texto) : null;
	} catch {
		cuerpo = { detail: texto };
	}

	if (respuesta.status === 401 && typeof window !== 'undefined' && !ruta.startsWith('/auth')) {
		window.localStorage.removeItem('token');
		window.localStorage.removeItem('usuario');
		window.localStorage.removeItem('modulos');
		window.location.href = '/login?expirada=1';
	}
	if (!respuesta.ok) throw new ErrorApi(mensajeDeError(cuerpo, respuesta.status), respuesta.status);
	return cuerpo;
}

export const obtenerJson = (ruta) => peticion(ruta, 'GET');
export const enviarJson = (ruta, datos) => peticion(ruta, 'POST', datos);
export const actualizarJson = (ruta, datos) => peticion(ruta, 'PUT', datos);
export const eliminarJson = (ruta) => peticion(ruta, 'DELETE');
export const modificarJson = (ruta, datos) => peticion(ruta, 'PATCH', datos);

/** Devuelve siempre un arreglo (algunas rutas responden { datos: [...] }). */
export async function obtenerLista(ruta) {
	const cuerpo = await obtenerJson(ruta);
	if (Array.isArray(cuerpo)) return cuerpo;
	return cuerpo?.datos ?? cuerpo?.data ?? cuerpo?.items ?? [];
}

/**
 * Descarga un archivo (PDF o Excel) desde la API con el token de la sesión.
 * Devuelve { blob, nombre } con el nombre que envía la API en Content-Disposition.
 */
export async function descargarArchivo(ruta, nombrePorDefecto = 'archivo') {
	const token = leerToken();
	let respuesta;
	try {
		respuesta = await fetch(`${API_URL}${ruta}`, { headers: token ? { Authorization: `Bearer ${token}` } : {} });
	} catch {
		throw new ErrorApi('No hay conexión con la API. Verifica que esté encendida.', 0);
	}
	if (!respuesta.ok) {
		let cuerpo = null;
		try {
			cuerpo = await respuesta.json();
		} catch {
			/* respuesta sin JSON */
		}
		throw new ErrorApi(mensajeDeError(cuerpo, respuesta.status), respuesta.status);
	}
	const disposicion = respuesta.headers.get('Content-Disposition') ?? '';
	const nombre = /filename="?([^";]+)"?/i.exec(disposicion)?.[1] ?? nombrePorDefecto;
	return { blob: await respuesta.blob(), nombre };
}

/** Guarda en el equipo un archivo descargado con descargarArchivo(). */
export function guardarArchivo({ blob, nombre }) {
	const url = URL.createObjectURL(blob);
	const enlace = document.createElement('a');
	enlace.href = url;
	enlace.download = nombre;
	document.body.appendChild(enlace);
	enlace.click();
	enlace.remove();
	setTimeout(() => URL.revokeObjectURL(url), 2000);
}
