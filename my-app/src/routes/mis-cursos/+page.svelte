<script>
	import PaginaCrud from '$lib/components/PaginaCrud.svelte';
	import VentanaModal from '$lib/components/VentanaModal.svelte';
	import TablaDatos from '$lib/components/TablaDatos.svelte';
	import { cargarCatalogos, cargasDelDocente, matriculaVigente } from '$lib/catalogos.js';
	import { esAdministrador } from '$lib/sesion.js';
	import { nombreCompleto, soloActivos, escaparHtml } from '$lib/utilidades.js';

	let cat = $state(null);
	let modalAbierto = $state(false);
	let cargaVista = $state(null);
	let estudiantesCurso = $state([]);

	const columnas = [
		{ titulo: 'Curso', campo: 'curso', render: (v) => `<strong>${escaparHtml(v)}</strong>` },
		{ titulo: 'Asignatura', campo: 'asignatura' },
		{ titulo: 'Año', campo: 'anio_lectivo', clase: 'text-center' },
		{ titulo: 'Estudiantes', campo: 'total', clase: 'text-center' },
		{ titulo: 'Fallas registradas', campo: 'fallas', clase: 'text-center' }
	];

	const columnasEstudiantes = [
		{ titulo: 'Estudiante', campo: 'nombre', render: (v) => `<strong>${escaparHtml(v)}</strong>` },
		{ titulo: 'Documento', campo: 'documento_identidad' },
		{ titulo: 'Fallas', campo: 'fallas', clase: 'text-center' },
		{ titulo: 'Acudiente', campo: 'acudiente' },
		{ titulo: 'Teléfono acudiente', campo: 'telefono' }
	];

	async function cargar() {
		const c = await cargarCatalogos(['cargas', 'cursos', 'asignaturas', 'matriculas', 'estudiantes', 'asistencias', 'vinculos', 'acudientes']);
		cat = c;
		const propias = esAdministrador() ? soloActivos(c.cargas) : soloActivos(cargasDelDocente(c.cargas));
		const vigentes = [...matriculaVigente(c.matriculas).values()];
		return propias.map((ca) => ({
			...ca,
			curso: c.cursos.find((x) => x.cursoid === ca.cursoid)?.nombre_curso ?? '',
			asignatura: c.asignaturas.find((x) => x.materiaid === ca.materiaid)?.nombre_materia ?? '',
			total: vigentes.filter((m) => m.cursoid === ca.cursoid && m.anio_lectivo === ca.anio_lectivo).length,
			fallas: soloActivos(c.asistencias).filter((a) => a.cursoid === ca.cursoid && a.materiaid === ca.materiaid && a.estado === 'ausente').length
		}));
	}

	function verEstudiantes(carga) {
		cargaVista = carga;
		const vigentes = [...matriculaVigente(cat.matriculas).values()].filter((m) => m.cursoid === carga.cursoid && m.anio_lectivo === carga.anio_lectivo);
		estudiantesCurso = vigentes.map((m) => {
			const e = cat.estudiantes.find((x) => x.estudiante_id === m.estudianteid) ?? {};
			const v = cat.vinculos.find((x) => x.estudianteid === m.estudianteid && x.contacto_principal) ?? cat.vinculos.find((x) => x.estudianteid === m.estudianteid);
			const a = cat.acudientes.find((x) => x.acudiente_id === v?.acudienteid);
			return {
				nombre: nombreCompleto(e),
				documento_identidad: e.documento_identidad,
				fallas: soloActivos(cat.asistencias).filter((x) => x.estudianteid === m.estudianteid && x.materiaid === carga.materiaid && x.estado === 'ausente').length,
				acudiente: nombreCompleto(a) || 'Sin acudiente',
				telefono: a?.telefono ?? ''
			};
		});
		modalAbierto = true;
	}
</script>

<svelte:head><title>Mis cursos | Aula Presente</title></svelte:head>

<PaginaCrud
	titulo="Mis cursos"
	descripcion="Cursos y asignaturas que tienes asignados. Para tomar asistencia ve al módulo Asistencia."
	icono="bi-easel"
	{columnas}
	{cargar}
	accionesExtra={[{ titulo: 'Ver estudiantes', icono: 'bi-people', clase: 'btn-outline-primary', alHacerClic: verEstudiantes }]}
>
	{#snippet inferior()}
		{#if !cat}{:else if cat && cargasDelDocente(cat.cargas).length === 0 && !esAdministrador()}
			<div class="alert alert-info mt-3">Aún no tienes carga académica asignada. Pídele al administrador que te asigne cursos.</div>
		{/if}
	{/snippet}
</PaginaCrud>

<VentanaModal bind:abierto={modalAbierto} titulo={cargaVista ? `${cargaVista.curso} · ${cargaVista.asignatura}` : ''} tamano="xl">
	<TablaDatos columnas={columnasEstudiantes} filas={estudiantesCurso} />
</VentanaModal>
