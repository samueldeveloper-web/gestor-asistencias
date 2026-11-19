<script>
	import PaginaCrud from '$lib/components/PaginaCrud.svelte';
	import VentanaModal from '$lib/components/VentanaModal.svelte';
	import TablaDatos from '$lib/components/TablaDatos.svelte';
	import TarjetaIndicador from '$lib/components/TarjetaIndicador.svelte';
	import { actualizarVinculo } from '$lib/api/estudianteAcudienteApi.js';
	import { cargarCatalogos, matriculaVigente, perfilSesion } from '$lib/catalogos.js';
	import { permisosDe } from '$lib/sesion.js';
	import { nombreCompleto, soloActivos, formatearFecha, insignia, escaparHtml } from '$lib/utilidades.js';

	const permisos = permisosDe('/mis-hijos');
	let cat = $state(null);
	let filas = $state([]);
	let modalAbierto = $state(false);
	let hijoVisto = $state(null);
	let historial = $state([]);

	const columnas = [
		{ titulo: 'Estudiante', campo: 'estudiante', render: (v) => `<strong>${escaparHtml(v)}</strong>` },
		{ titulo: 'Curso', campo: 'curso' },
		{ titulo: 'Parentesco', campo: 'parentesco' },
		{ titulo: 'Contacto principal', campo: 'contacto_principal', render: (v, _f, t) => (t === 'display' ? (v ? insignia('Sí') : 'No') : v) },
		{ titulo: 'Fallas', campo: 'fallas', clase: 'text-center' },
		{ titulo: 'Tardanzas', campo: 'tardanzas', clase: 'text-center' }
	];

	const columnasHistorial = [
		{ titulo: 'Fecha', campo: 'fecha', render: (v, _f, t) => (t === 'display' ? formatearFecha(v) : v) },
		{ titulo: 'Asignatura', campo: 'asignatura' },
		{ titulo: 'Docente', campo: 'docente' },
		{ titulo: 'Estado', campo: 'estado', render: (v, _f, t) => (t === 'display' ? insignia(v) : v) }
	];

	const campos = [
		{ nombre: 'parentesco', etiqueta: 'Parentesco', tipo: 'select', requerido: true, opciones: ['Madre', 'Padre', 'Abuelo(a)', 'Tío(a)', 'Hermano(a)', 'Tutor legal'].map((p) => ({ valor: p, etiqueta: p })) },
		{ nombre: 'contacto_principal', etiqueta: 'Soy el contacto principal', tipo: 'casilla' }
	];

	async function cargar() {
		const c = await cargarCatalogos(['vinculos', 'estudiantes', 'matriculas', 'cursos', 'asistencias', 'asignaturas', 'docentes']);
		cat = c;
		const { acudienteId } = perfilSesion();
		const vigente = matriculaVigente(c.matriculas);
		return soloActivos(c.vinculos)
			.filter((v) => v.acudienteid === acudienteId)
			.map((v) => {
				const asis = soloActivos(c.asistencias).filter((a) => a.estudianteid === v.estudianteid);
				return {
					...v,
					estudiante: nombreCompleto(c.estudiantes.find((e) => e.estudiante_id === v.estudianteid)),
					curso: c.cursos.find((x) => x.cursoid === vigente.get(v.estudianteid)?.cursoid)?.nombre_curso ?? 'Sin matrícula',
					fallas: asis.filter((a) => a.estado === 'ausente').length,
					tardanzas: asis.filter((a) => a.estado === 'tarde').length
				};
			});
	}

	function verHistorial(fila) {
		hijoVisto = fila;
		historial = soloActivos(cat.asistencias)
			.filter((a) => a.estudianteid === fila.estudianteid)
			.map((a) => ({
				...a,
				asignatura: cat.asignaturas.find((x) => x.materiaid === a.materiaid)?.nombre_materia ?? '',
				docente: nombreCompleto(cat.docentes.find((d) => d.personalid === a.personal_institucionalid))
			}));
		modalAbierto = true;
	}

	const totalFallas = $derived(filas.reduce((s, f) => s + f.fallas, 0));
</script>

<svelte:head><title>Mis hijos | Aula Presente</title></svelte:head>

<PaginaCrud
	titulo="Mis hijos"
	descripcion="Estudiantes a tu cargo y resumen de su asistencia."
	icono="bi-heart"
	recurso="vínculo"
	bind:filas
	{columnas}
	{campos}
	{cargar}
	aFormulario={(f) => ({ parentesco: f.parentesco, contacto_principal: f.contacto_principal })}
	actualizar={(f, v) => actualizarVinculo(f, { estudianteid: f.estudianteid, acudienteid: f.acudienteid, parentesco: v.parentesco, contacto_principal: !!v.contacto_principal, esta_activo: true })}
	describir={(f) => `el vínculo con ${f.estudiante}`}
	puedeCrear={false}
	puedeEditar={permisos.actualizar}
	puedeEliminar={false}
	accionesExtra={[{ titulo: 'Ver asistencia', icono: 'bi-calendar3', clase: 'btn-outline-secondary', alHacerClic: verHistorial }]}
>
	{#snippet superior()}
		<div class="row g-3 mb-4">
			<div class="col-sm-6 col-lg-4"><TarjetaIndicador titulo="Estudiantes a cargo" valor={filas.length} icono="bi-people" /></div>
			<div class="col-sm-6 col-lg-4"><TarjetaIndicador titulo="Fallas acumuladas" valor={totalFallas} icono="bi-calendar-x" color="danger" enlace="/asistencia" /></div>
			<div class="col-sm-6 col-lg-4"><TarjetaIndicador titulo="Justificar una falla" valor="Excusas" icono="bi-envelope-paper" color="success" enlace="/excusas" /></div>
		</div>
	{/snippet}
</PaginaCrud>

<VentanaModal bind:abierto={modalAbierto} titulo={hijoVisto ? `Asistencia de ${hijoVisto.estudiante}` : ''} tamano="lg">
	<TablaDatos columnas={columnasHistorial} filas={historial} ordenInicial={[[0, 'desc']]} />
</VentanaModal>
