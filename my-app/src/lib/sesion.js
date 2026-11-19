/** Manejo de la sesión del usuario en el navegador (token, usuario y módulos). */

const enNavegador = () => typeof window !== 'undefined';

export function guardarSesion({ token, usuario, modulos }) {
	window.localStorage.setItem('token', token);
	window.localStorage.setItem('usuario', JSON.stringify(usuario));
	window.localStorage.setItem('modulos', JSON.stringify(modulos ?? []));
}

export function cerrarSesion() {
	if (!enNavegador()) return;
	window.localStorage.removeItem('token');
	window.localStorage.removeItem('usuario');
	window.localStorage.removeItem('modulos');
	window.location.href = '/login';
}

export function obtenerUsuario() {
	if (!enNavegador()) return null;
	try {
		return JSON.parse(window.localStorage.getItem('usuario') ?? 'null');
	} catch {
		return null;
	}
}

export function obtenerModulos() {
	if (!enNavegador()) return [];
	try {
		return JSON.parse(window.localStorage.getItem('modulos') ?? '[]');
	} catch {
		return [];
	}
}

export function haySesion() {
	return enNavegador() && Boolean(window.localStorage.getItem('token'));
}

/** Nombre del rol en minúsculas y sin tildes: administrador, docente, acudiente, estudiante. */
export function rolActual() {
	const usuario = obtenerUsuario();
	return (usuario?.rol ?? usuario?.rol_nombre ?? '')
		.toString()
		.normalize('NFD')
		.replace(/[̀-ͯ]/g, '')
		.toLowerCase();
}

export const esAdministrador = () => rolActual().startsWith('admin');
export const esDocente = () => rolActual().startsWith('docente');
export const esAcudiente = () => rolActual().startsWith('acudiente');
export const esEstudiante = () => rolActual().startsWith('estudiante');

/** Permisos del módulo actual según modulo_por_rol. Si la API no los envía, se permite leer. */
export function permisosDe(ruta) {
	const modulo = obtenerModulos().find((m) => m.ruta === ruta);
	if (!modulo) return { crear: false, leer: false, actualizar: false, eliminar: false };
	const p = (campo) => modulo[`permiso_${campo}`] ?? modulo[campo] ?? modulo.permisos?.[campo];
	const definido = ['crear', 'leer', 'actualizar', 'eliminar'].some((c) => p(c) !== undefined);
	if (!definido) return { crear: true, leer: true, actualizar: true, eliminar: true };
	return { crear: !!p('crear'), leer: !!p('leer'), actualizar: !!p('actualizar'), eliminar: !!p('eliminar') };
}
