<script>
	import PaginaCrud from '$lib/components/PaginaCrud.svelte';
	import { crearCarga, actualizarCarga, eliminarCarga } from '$lib/api/cargaAcademicaApi.js';
	import { cargarCatalogos } from '$lib/catalogos.js';
	import { permisosDe } from '$lib/sesion.js';
	import { nombreCompleto, opciones, soloActivos, escaparHtml } from '$lib/utilidades.js';

	const permisos = permisosDe('/carga-academica');
	let cat = $state({ cursos: [], asignaturas: [], docentes: [] });

	const columnas = [
		{ titulo: 'Curso', campo: 'curso', render: (v) => `<strong>${escaparHtml(v)}</strong>` },
		{ titulo: 'Asignatura', campo: 'asignatura' },
		{ titulo: 'Docente', campo: 'docente' },
		{ titulo: 'Año lectivo', campo: 'anio_lectivo', clase: 'text-center' }
	];

	const campos = () => [
		{ nombre: 'cursoid', etiqueta: 'Curso', tipo: 'select', requerido: true, opciones: opciones(soloActivos(cat.cursos), 'cursoid', 'nombre_curso') },
		{ nombre: 'materiaid', etiqueta: 'Asignatura', tipo: 'select', requerido: true, opciones: opciones(soloActivos(cat.asignaturas), 'materiaid', 'nombre_materia') },
		{ nombre: 'personal_institucionalid', etiqueta: 'Docente', tipo: 'select', requerido: true, opciones: opciones(soloActivos(cat.docentes), 'personalid', nombreCompleto) },
		{ nombre: 'anio_lectivo', etiqueta: 'Año lectivo', tipo: 'numero', requerido: true, min: 2020, max: 2100 }
	];

	async function cargar() {
		const c = await cargarCatalogos(['cargas', 'cursos', 'asignaturas', 'docentes']);
		cat = c;
		return soloActivos(c.cargas).map((ca) => ({
			...ca,
			curso: c.cursos.find((x) => x.cursoid === ca.cursoid)?.nombre_curso ?? '',
			asignatura: c.asignaturas.find((x) => x.materiaid === ca.materiaid)?.nombre_materia ?? '',
			docente: nombreCompleto(c.docentes.find((x) => x.personalid === ca.personal_institucionalid)) || 'Sin docente'
		}));
	}

	const aDatos = (v) => ({
		cursoid: v.cursoid,
		materiaid: v.materiaid,
		personal_institucionalid: v.personal_institucionalid,
		anio_lectivo: Number(v.anio_lectivo),
		esta_activo: true
	});
</script>

<svelte:head><title>Carga académica | Aula Presente</title></svelte:head>

<PaginaCrud
	titulo="Carga académica"
	descripcion="Qué docente dicta cada asignatura en cada curso."
	icono="bi-diagram-3"
	recurso="asignación"
	textoCrear="Nueva asignación"
	{columnas}
	{campos}
	{cargar}
	valoresIniciales={() => ({ cursoid: null, materiaid: null, personal_institucionalid: null, anio_lectivo: new Date().getFullYear() })}
	crear={(v) => crearCarga(aDatos(v))}
	actualizar={(f, v) => actualizarCarga(f, aDatos(v))}
	eliminar={eliminarCarga}
	describir={(f) => `la asignación ${f.asignatura} en ${f.curso}`}
	puedeCrear={permisos.crear}
	puedeEditar={permisos.actualizar}
	puedeEliminar={permisos.eliminar}
/>
