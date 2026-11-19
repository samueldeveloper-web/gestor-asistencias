<script>
	import PaginaCrud from '$lib/components/PaginaCrud.svelte';
	import { crearMatricula, actualizarMatricula, eliminarMatricula } from '$lib/api/matriculasApi.js';
	import { cargarCatalogos } from '$lib/catalogos.js';
	import { permisosDe } from '$lib/sesion.js';
	import { nombreCompleto, opciones, soloActivos, formatearFecha, insignia, hoy, escaparHtml } from '$lib/utilidades.js';

	const permisos = permisosDe('/matriculas');
	let cat = $state({ estudiantes: [], cursos: [] });
	const estados = ['activo', 'retirado', 'graduado', 'promovido'];

	const columnas = [
		{ titulo: 'Estudiante', campo: 'estudiante', render: (v) => `<strong>${escaparHtml(v)}</strong>` },
		{ titulo: 'Curso', campo: 'curso' },
		{ titulo: 'Año lectivo', campo: 'anio_lectivo', clase: 'text-center' },
		{ titulo: 'Fecha de matrícula', campo: 'fecha_matricula', render: (v, _f, t) => (t === 'display' ? formatearFecha(v) : v) },
		{ titulo: 'Estado', campo: 'estado', render: (v, _f, t) => (t === 'display' ? insignia(v) : v) }
	];

	const campos = () => [
		{ nombre: 'estudianteid', etiqueta: 'Estudiante', tipo: 'select', requerido: true, opciones: opciones(soloActivos(cat.estudiantes), 'estudiante_id', nombreCompleto) },
		{ nombre: 'cursoid', etiqueta: 'Curso', tipo: 'select', requerido: true, opciones: opciones(soloActivos(cat.cursos), 'cursoid', 'nombre_curso') },
		{ nombre: 'anio_lectivo', etiqueta: 'Año lectivo', tipo: 'numero', requerido: true, min: 2020, max: 2100 },
		{ nombre: 'fecha_matricula', etiqueta: 'Fecha de matrícula', tipo: 'fecha', requerido: true },
		{ nombre: 'estado', etiqueta: 'Estado', tipo: 'select', requerido: true, opciones: estados.map((e) => ({ valor: e, etiqueta: e[0].toUpperCase() + e.slice(1) })) }
	];

	async function cargar() {
		const c = await cargarCatalogos(['matriculas', 'estudiantes', 'cursos']);
		cat = c;
		return soloActivos(c.matriculas).map((m) => ({
			...m,
			estudiante: nombreCompleto(c.estudiantes.find((e) => e.estudiante_id === m.estudianteid)),
			curso: c.cursos.find((x) => x.cursoid === m.cursoid)?.nombre_curso ?? ''
		}));
	}

	const aDatos = (v) => ({
		estudianteid: v.estudianteid,
		cursoid: v.cursoid,
		anio_lectivo: Number(v.anio_lectivo),
		fecha_matricula: v.fecha_matricula,
		estado: v.estado,
		esta_activo: true
	});
</script>

<svelte:head><title>Matrículas | Aula Presente</title></svelte:head>

<PaginaCrud
	titulo="Matrículas"
	descripcion="Curso en el que está cada estudiante por año lectivo."
	icono="bi-journal-check"
	recurso="matrícula"
	textoCrear="Nueva matrícula"
	{columnas}
	{campos}
	{cargar}
	ordenInicial={[[2, 'desc']]}
	valoresIniciales={() => ({ estudianteid: null, cursoid: null, anio_lectivo: new Date().getFullYear(), fecha_matricula: hoy(), estado: 'activo' })}
	aFormulario={(f) => ({ ...f, fecha_matricula: f.fecha_matricula?.slice(0, 10) ?? '' })}
	crear={(v) => crearMatricula(aDatos(v))}
	actualizar={(f, v) => actualizarMatricula(f, aDatos(v))}
	eliminar={eliminarMatricula}
	describir={(f) => `la matrícula de ${f.estudiante} en ${f.curso}`}
	puedeCrear={permisos.crear}
	puedeEditar={permisos.actualizar}
	puedeEliminar={permisos.eliminar}
/>
