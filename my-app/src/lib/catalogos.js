/**
 * Carga de catálogos compartidos por varias páginas y cálculo del alcance de cada rol
 * (qué estudiantes, cursos o acudientes puede ver el usuario que inició sesión).
 */
import { listarEstudiantes } from '$lib/api/estudiantesApi.js';
import { listarAcudientes } from '$lib/api/acudientesApi.js';
import { listarDocentes } from '$lib/api/docentesApi.js';
import { listarCursos } from '$lib/api/cursosApi.js';
import { listarAsignaturas } from '$lib/api/asignaturasApi.js';
import { listarCargas } from '$lib/api/cargaAcademicaApi.js';
import { listarMatriculas } from '$lib/api/matriculasApi.js';
import { listarVinculos } from '$lib/api/estudianteAcudienteApi.js';
import { listarAsistencias } from '$lib/api/asistenciaApi.js';
import { listarExcusas } from '$lib/api/excusasApi.js';
import { listarNotificaciones } from '$lib/api/notificacionesApi.js';
import { listarRoles } from '$lib/api/rolesApi.js';
import { listarModulos } from '$lib/api/modulosApi.js';
import { listarUsuarios } from '$lib/api/usuariosApi.js';
import { obtenerUsuario, esAcudiente, esDocente, esEstudiante } from '$lib/sesion.js';
import { nombreCompleto } from '$lib/utilidades.js';

const cargadores = {
	estudiantes: listarEstudiantes,
	acudientes: listarAcudientes,
	docentes: listarDocentes,
	cursos: listarCursos,
	asignaturas: listarAsignaturas,
	cargas: listarCargas,
	matriculas: listarMatriculas,
	vinculos: listarVinculos,
	asistencias: listarAsistencias,
	excusas: listarExcusas,
	notificaciones: listarNotificaciones,
	roles: listarRoles,
	modulos: listarModulos,
	usuarios: listarUsuarios
};

/** Ejemplo: const c = await cargarCatalogos(['estudiantes', 'cursos']) → { estudiantes: [...], cursos: [...] } */
export async function cargarCatalogos(nombres) {
	const listas = await Promise.all(nombres.map((n) => cargadores[n]()));
	return Object.fromEntries(nombres.map((n, i) => [n, listas[i] ?? []]));
}

/** Perfil vinculado al usuario de la sesión (tabla usuario: personal_institucionalid, acudienteid, estudianteid). */
export function perfilSesion() {
	const u = obtenerUsuario() ?? {};
	const p = u.perfil ?? {};
	return {
		docenteId: (p.tipo === 'docente' ? p.id : null) ?? u.personal_institucionalid ?? u.personalid ?? u.docente_id ?? null,
		acudienteId: (p.tipo === 'acudiente' ? p.id : null) ?? u.acudienteid ?? u.acudiente_id ?? null,
		estudianteId: (p.tipo === 'estudiante' ? p.id : null) ?? u.estudianteid ?? u.estudiante_id ?? null
	};
}

/** Matrícula vigente de cada estudiante: Map estudianteid → matrícula (estado activo, año más reciente). */
export function matriculaVigente(matriculas) {
	const mapa = new Map();
	for (const m of matriculas) {
		if ((m.esta_activo ?? true) === false) continue;
		if (String(m.estado ?? 'activo').toLowerCase() !== 'activo') continue;
		const actual = mapa.get(m.estudianteid);
		if (!actual || m.anio_lectivo > actual.anio_lectivo) mapa.set(m.estudianteid, m);
	}
	return mapa;
}

/** Cargas académicas del docente que inició sesión. */
export function cargasDelDocente(cargas) {
	const { docenteId } = perfilSesion();
	return cargas.filter((c) => c.personal_institucionalid === docenteId);
}

/**
 * IDs de estudiantes que el usuario puede ver según su rol.
 * Devuelve null cuando no hay restricción (administrador).
 */
export function estudiantesPermitidos({ vinculos = [], cargas = [], matriculas = [] }) {
	const { acudienteId, estudianteId } = perfilSesion();
	if (esAcudiente()) {
		return new Set(vinculos.filter((v) => v.acudienteid === acudienteId && (v.esta_activo ?? true) !== false).map((v) => v.estudianteid));
	}
	if (esEstudiante()) return new Set(estudianteId ? [estudianteId] : []);
	if (esDocente()) {
		const claves = new Set(cargasDelDocente(cargas).map((c) => `${c.cursoid}-${c.anio_lectivo}`));
		return new Set(matriculas.filter((m) => (m.esta_activo ?? true) !== false && claves.has(`${m.cursoid}-${m.anio_lectivo}`)).map((m) => m.estudianteid));
	}
	return null;
}

export const filtrarPorEstudiante = (filas, permitidos) => (permitidos ? filas.filter((f) => permitidos.has(f.estudianteid)) : filas);

/** Etiqueta legible de una carga académica: "10-A · Matemáticas · Juan Pérez". */
export function etiquetaCarga(carga, { cursos = [], asignaturas = [], docentes = [] }, conDocente = true) {
	const curso = cursos.find((c) => c.cursoid === carga.cursoid)?.nombre_curso ?? 'Curso';
	const materia = asignaturas.find((a) => a.materiaid === carga.materiaid)?.nombre_materia ?? 'Asignatura';
	const docente = nombreCompleto(docentes.find((d) => d.personalid === carga.personal_institucionalid));
	return [curso, materia, conDocente ? docente : '', carga.anio_lectivo].filter(Boolean).join(' · ');
}
