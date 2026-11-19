<script>
	import PaginaCrud from '$lib/components/PaginaCrud.svelte';
	import { listarAsignaturas, crearAsignatura, actualizarAsignatura, eliminarAsignatura } from '$lib/api/asignaturasApi.js';
	import { permisosDe } from '$lib/sesion.js';
	import { soloActivos, escaparHtml } from '$lib/utilidades.js';

	const permisos = permisosDe('/asignaturas');

	const columnas = [
		{ titulo: 'Asignatura', campo: 'nombre_materia', render: (v) => `<strong>${escaparHtml(v)}</strong>` },
		{ titulo: 'Descripción', campo: 'descripcion' }
	];

	const campos = [
		{ nombre: 'nombre_materia', etiqueta: 'Nombre de la asignatura', tipo: 'texto', requerido: true, ancho: 'col-12' },
		{ nombre: 'descripcion', etiqueta: 'Descripción', tipo: 'textarea', ancho: 'col-12' }
	];

	const aDatos = (v) => ({ nombre_materia: v.nombre_materia?.trim(), descripcion: v.descripcion?.trim() || null, esta_activo: true });
</script>

<svelte:head><title>Asignaturas | Aula Presente</title></svelte:head>

<PaginaCrud
	titulo="Asignaturas"
	descripcion="Materias que se dictan en la institución."
	icono="bi-book"
	recurso="asignatura"
	{columnas}
	{campos}
	cargar={async () => soloActivos(await listarAsignaturas())}
	valoresIniciales={() => ({ nombre_materia: '', descripcion: '' })}
	crear={(v) => crearAsignatura(aDatos(v))}
	actualizar={(f, v) => actualizarAsignatura(f, aDatos(v))}
	eliminar={eliminarAsignatura}
	describir={(f) => `la asignatura ${f.nombre_materia}`}
	puedeCrear={permisos.crear}
	puedeEditar={permisos.actualizar}
	puedeEliminar={permisos.eliminar}
/>
