<script>
	import { onMount } from 'svelte';
	import EncabezadoPagina from '$lib/components/EncabezadoPagina.svelte';
	import TarjetaIndicador from '$lib/components/TarjetaIndicador.svelte';
	import TablaDatos from '$lib/components/TablaDatos.svelte';
	import Alerta from '$lib/components/Alerta.svelte';
	import Cargando from '$lib/components/Cargando.svelte';
	import { cargarCatalogos, cargasDelDocente, estudiantesPermitidos, filtrarPorEstudiante, perfilSesion } from '$lib/catalogos.js';
	import { obtenerUsuario, obtenerModulos, esAdministrador, esDocente, esAcudiente } from '$lib/sesion.js';
	import { nombreCompleto, soloActivos, formatearFecha, insignia, hoy, escaparHtml } from '$lib/utilidades.js';

	const usuario = obtenerUsuario();
	const tiene = (ruta) => obtenerModulos().some((m) => m.ruta === ruta);
	let cargando = $state(true);
	let error = $state('');
	let indicadores = $state([]);
	let recientes = $state([]);

	const columnas = [
		{ titulo: 'Fecha', campo: 'fecha', render: (v, _f, t) => (t === 'display' ? formatearFecha(v) : v) },
		{ titulo: 'Estudiante', campo: 'estudiante', render: (v) => `<strong>${escaparHtml(v)}</strong>` },
		{ titulo: 'Asignatura', campo: 'asignatura' },
		{ titulo: 'Curso', campo: 'curso' },
		{ titulo: 'Estado', campo: 'estado', render: (v, _f, t) => (t === 'display' ? insignia(v) : v) }
	];

	onMount(async () => {
		try {
			const c = await cargarCatalogos(['asistencias', 'estudiantes', 'cursos', 'asignaturas', 'cargas', 'matriculas', 'vinculos', 'excusas', 'notificaciones', 'docentes']);
			const { docenteId, acudienteId } = perfilSesion();
			const permitidos = estudiantesPermitidos(c);
			let asis = soloActivos(c.asistencias);
			if (esDocente()) asis = asis.filter((a) => a.personal_institucionalid === docenteId);
			else asis = filtrarPorEstudiante(asis, permitidos);
			const fallas = asis.filter((a) => a.estado === 'ausente');
			const fallasHoy = fallas.filter((a) => a.fecha?.slice(0, 10) === hoy());
			const idsAsis = new Set(asis.map((a) => a.asistenciaid));
			const excusasPend = soloActivos(c.excusas).filter((x) => x.estado === 'pendiente' && (esAdministrador() || idsAsis.has(x.asistenciaid)));
			const notifs = soloActivos(c.notificaciones).filter((n) => (esAcudiente() ? n.acudienteid === acudienteId : true));
			const noLeidas = notifs.filter((n) => !n.leido);

			if (esAdministrador()) {
				indicadores = [
					{ titulo: 'Estudiantes activos', valor: soloActivos(c.estudiantes).length, icono: 'bi-mortarboard', color: 'primary', enlace: tiene('/estudiantes') ? '/estudiantes' : '' },
					{ titulo: 'Docentes', valor: soloActivos(c.docentes).length, icono: 'bi-person-badge', color: 'info', enlace: tiene('/docentes') ? '/docentes' : '' },
					{ titulo: 'Fallas hoy', valor: fallasHoy.length, icono: 'bi-calendar-x', color: 'danger', detalle: `${fallas.length} en total`, enlace: '/asistencia' },
					{ titulo: 'Excusas por revisar', valor: excusasPend.length, icono: 'bi-envelope-paper', color: 'warning', enlace: tiene('/excusas') ? '/excusas' : '' }
				];
			} else if (esDocente()) {
				const mias = soloActivos(cargasDelDocente(c.cargas));
				indicadores = [
					{ titulo: 'Mis cursos', valor: mias.length, icono: 'bi-easel', color: 'primary', enlace: tiene('/mis-cursos') ? '/mis-cursos' : '' },
					{ titulo: 'Mis estudiantes', valor: permitidos?.size ?? 0, icono: 'bi-people', color: 'info' },
					{ titulo: 'Fallas registradas', valor: fallas.length, icono: 'bi-calendar-x', color: 'danger', detalle: `${fallasHoy.length} hoy`, enlace: '/asistencia' },
					{ titulo: 'Excusas por revisar', valor: excusasPend.length, icono: 'bi-envelope-paper', color: 'warning', enlace: tiene('/excusas') ? '/excusas' : '' }
				];
			} else if (esAcudiente()) {
				indicadores = [
					{ titulo: 'Hijos a cargo', valor: permitidos?.size ?? 0, icono: 'bi-heart', color: 'primary', enlace: tiene('/mis-hijos') ? '/mis-hijos' : '' },
					{ titulo: 'Fallas', valor: fallas.length, icono: 'bi-calendar-x', color: 'danger', enlace: '/asistencia' },
					{ titulo: 'Notificaciones sin leer', valor: noLeidas.length, icono: 'bi-bell', color: 'warning', enlace: tiene('/notificaciones') ? '/notificaciones' : '' },
					{ titulo: 'Excusas pendientes', valor: excusasPend.length, icono: 'bi-envelope-paper', color: 'info', enlace: tiene('/excusas') ? '/excusas' : '' }
				];
			} else {
				indicadores = [
					{ titulo: 'Mis fallas', valor: fallas.length, icono: 'bi-calendar-x', color: 'danger', enlace: tiene('/asistencia') ? '/asistencia' : '' },
					{ titulo: 'Llegadas tarde', valor: asis.filter((a) => a.estado === 'tarde').length, icono: 'bi-clock-history', color: 'warning' },
					{ titulo: 'Fallas excusadas', valor: asis.filter((a) => a.estado === 'excusado').length, icono: 'bi-check2-circle', color: 'success' }
				];
			}

			recientes = asis
				.filter((a) => a.estado !== 'presente')
				.sort((a, b) => String(b.fecha).localeCompare(String(a.fecha)))
				.slice(0, 50)
				.map((a) => ({
					...a,
					fecha: a.fecha?.slice(0, 10),
					estudiante: nombreCompleto(c.estudiantes.find((e) => e.estudiante_id === a.estudianteid)),
					asignatura: c.asignaturas.find((m) => m.materiaid === a.materiaid)?.nombre_materia ?? '',
					curso: c.cursos.find((x) => x.cursoid === a.cursoid)?.nombre_curso ?? ''
				}));
		} catch (e) {
			error = e.message;
		} finally {
			cargando = false;
		}
	});
</script>

<svelte:head><title>Inicio | Aula Presente</title></svelte:head>

<EncabezadoPagina titulo="Hola, {usuario?.nombre ?? usuario?.username ?? ''}" descripcion="Resumen de asistencia para el rol {usuario?.rol ?? ''}." icono="bi-house" />

<Alerta mensaje={error} tipo="danger" />

{#if cargando}
	<Cargando mensaje="Calculando indicadores…" />
{:else}
	<div class="row g-3 mb-4">
		{#each indicadores as ind (ind.titulo)}
			<div class="col-sm-6 col-xl-3">
				<TarjetaIndicador {...ind} />
			</div>
		{/each}
	</div>

	<div class="card border-0">
		<div class="card-body">
			<h2 class="h5 fw-bold mb-3"><i class="bi bi-exclamation-diamond text-danger me-2"></i>Fallas y novedades recientes</h2>
			<TablaDatos {columnas} filas={recientes} ordenInicial={[[0, 'desc']]} porPagina={5} />
		</div>
	</div>
{/if}
