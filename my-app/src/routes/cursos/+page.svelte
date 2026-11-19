<script>
	import PaginaCrud from '$lib/components/PaginaCrud.svelte';
	import { crearCurso, actualizarCurso, eliminarCurso } from '$lib/api/cursosApi.js';
	import { cargarCatalogos, matriculaVigente } from '$lib/catalogos.js';
	import { permisosDe } from '$lib/sesion.js';
	import { soloActivos, escaparHtml } from '$lib/utilidades.js';

	const permisos = permisosDe('/cursos');
	const niveles = ['Preescolar', 'Básica primaria', 'Básica secundaria', 'Media'];

	const columnas = [
		{ titulo: 'Curso', campo: 'nombre_curso', render: (v) => `<strong>${escaparHtml(v)}</strong>` },
		{ titulo: 'Nivel educativo', campo: 'nivel_educativo' },
		{ titulo: 'Estudiantes matriculados', campo: 'matriculados', clase: 'text-center' },
		{ titulo: 'Asignaturas asignadas', campo: 'asignaturas', clase: 'text-center' }
	];

	const campos = [
		{ nombre: 'nombre_curso', etiqueta: 'Nombre del curso', tipo: 'texto', requerido: true, marcador: 'Ej: 10-A', maximo: 50 },
		{ nombre: 'nivel_educativo', etiqueta: 'Nivel educativo', tipo: 'select', requerido: true, opciones: niveles.map((n) => ({ valor: n, etiqueta: n })) }
	];

	async function cargar() {
		const c = await cargarCatalogos(['cursos', 'matriculas', 'cargas']);
		const vigente = [...matriculaVigente(c.matriculas).values()];
		return soloActivos(c.cursos).map((cu) => ({
			...cu,
			matriculados: vigente.filter((m) => m.cursoid === cu.cursoid).length,
			asignaturas: soloActivos(c.cargas).filter((ca) => ca.cursoid === cu.cursoid).length
		}));
	}

	const aDatos = (v) => ({ nombre_curso: v.nombre_curso?.trim(), nivel_educativo: v.nivel_educativo, esta_activo: true });
</script>

<svelte:head><title>Cursos | Aula Presente</title></svelte:head>

<PaginaCrud
	titulo="Cursos"
	descripcion="Grupos de la institución y su nivel educativo."
	icono="bi-building"
	recurso="curso"
	{columnas}
	{campos}
	{cargar}
	valoresIniciales={() => ({ nombre_curso: '', nivel_educativo: null })}
	crear={(v) => crearCurso(aDatos(v))}
	actualizar={(f, v) => actualizarCurso(f, aDatos(v))}
	eliminar={eliminarCurso}
	describir={(f) => `el curso ${f.nombre_curso}`}
	puedeCrear={permisos.crear}
	puedeEditar={permisos.actualizar}
	puedeEliminar={permisos.eliminar}
/>
