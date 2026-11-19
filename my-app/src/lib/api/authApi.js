/**
 * Autenticación: inicio de sesión con usuario, contraseña y rol (JWT).
 */
import { enviarJson, obtenerLista, obtenerJson, actualizarJson } from './http.js';

/** Roles disponibles para el selector del login (no requiere token). */
export const listarRolesLogin = () => obtenerLista('/roles/');

/** Ordena los módulos: Inicio primero y luego por el orden que traiga la BD. */
function normalizarModulos(modulos) {
	return (modulos ?? [])
		.filter((m) => (m.esta_activo ?? true) !== false && m.ruta)
		.map((m) => ({ ...m, nombre: m.nombre ?? m.modulo ?? m.ruta, icono: m.icono ?? '' }))
		.sort((a, b) => (a.ruta === '/dashboard' ? -1 : b.ruta === '/dashboard' ? 1 : (a.orden ?? 0) - (b.orden ?? 0)));
}

export async function iniciarSesion(identifier, password, rolid) {
	const respuesta = await enviarJson('/auth/login', { identifier, password, rolid });
	const token = respuesta.access_token ?? respuesta.token;
	const usuario = respuesta.usuario ?? respuesta.user ?? {};
	let modulos = respuesta.modulos ?? usuario.modulos;
	if (!modulos) {
		// Si el login no trae los módulos, se piden a modulo_por_rol con el token recién recibido.
		window.localStorage.setItem('token', token);
		const { listarModulosDeRol } = await import('./rolesApi.js');
		modulos = await listarModulosDeRol(usuario.rolid);
	}
	return { token, usuario, modulos: normalizarModulos(modulos) };
}

/** Vuelve a pedir los datos de la sesión con el token actual. */
export const obtenerSesionActual = () => obtenerJson('/auth/me');

/** Cambio de contraseña del usuario que inició sesión. */
export const cambiarPassword = (passwordActual, passwordNueva) => actualizarJson('/auth/password', { password_actual: passwordActual, password_nueva: passwordNueva });
