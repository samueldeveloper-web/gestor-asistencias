<script>
	import PaginaCrud from '$lib/components/PaginaCrud.svelte';
	import VentanaModal from '$lib/components/VentanaModal.svelte';
	import CampoFormulario from '$lib/components/CampoFormulario.svelte';
	import Alerta from '$lib/components/Alerta.svelte';
	import { crearAsistencia, actualizarAsistencia, eliminarAsistencia } from '$lib/api/asistenciaApi.js';
	import { cargarCatalogos, cargasDelDocente, estudiantesPermitidos, filtrarPorEstudiante, etiquetaCarga, perfilSesion } from '$lib/catalogos.js';
	import { permisosDe, esDocente, esAdministrador } from '$lib/sesion.js';
	import { nombreCompleto, soloActivos, formatearFecha, insignia, hoy, escaparHtml } from '$lib/utilidades.js';

	const permisos = permisosDe('/asistencia');
	const docente = esDocente();
	const ESTADOS = [
		{ valor: 'presente', etiqueta: 'Presente', clase: 'success' },
		{ valor: 'ausente', etiqueta: 'Ausente', clase: 'danger' },
		{ valor: 'tarde', etiqueta: 'Tarde', clase: 'warning' },
		{ valor: 'excusado', etiqueta: 'Excusado', clase: 'info' }
	];

	let cat = $state({ cargas: [], cursos: [], asignaturas: [], docentes: [], estudiantes: [], matriculas: [], asistencias: [] });
	let recargar = $state();

	// Cargas que puede usar el usuario para registrar: el docente solo las suyas.
	const cargasDisponibles = $derived(soloActivos(docente ? cargasDelDocente(cat.cargas) : cat.cargas));
	const opcionesCarga = $derived(cargasDisponibles.map((c) => ({ valor: c.cargaid, etiqueta: etiquetaCarga(c, cat, !docente) })));

	function estudiantesDeCarga(cargaid) {
		const carga = cat.cargas.find((c) => c.cargaid === cargaid);
		if (!carga) return [];
		const ids = new Set(
			soloActivos(cat.matriculas)
				.filter((m) => m.cursoid === carga.cursoid && m.anio_lectivo === carga.anio_lectivo && m.estado === 'activo')
				.map((m) => m.estudianteid)
		);
		return soloActivos(cat.estudiantes)
			.filter((e) => ids.has(e.estudiante_id))
			.sort((a, b) => a.apellidos.localeCompare(b.apellidos, 'es'));
	}

	const columnas = [
		{ titulo: 'Fecha', campo: 'fecha', render: (v, _f, t) => (t === 'display' ? formatearFecha(v) : v) },
		{ titulo: 'Estudiante', campo: 'estudiante', render: (v) => `<strong>${escaparHtml(v)}</strong>` },
		{ titulo: 'Curso', campo: 'curso' },
		{ titulo: 'Asignatura', campo: 'asignatura' },
		{ titulo: 'Docente', campo: 'docente' },
		{ titulo: 'Estado', campo: 'estado', render: (v, _f, t) => (t === 'display' ? insignia(v) : v) }
	];

	function campos(_modo, _fila, valores) {
		return [
			{ nombre: 'cargaid', etiqueta: docente ? 'Curso y asignatura' : 'Curso, asignatura y docente', tipo: 'select', requerido: true, ancho: 'col-12', opciones: opcionesCarga },
			{
				nombre: 'estudianteid', etiqueta: 'Estudiante', tipo: 'select', requerido: true,
				marcador: valores?.cargaid ? 'Selecciona un estudiante' : 'Primero elige el curso',
				opciones: estudiantesDeCarga(valores?.cargaid).map((e) => ({ valor: e.estudiante_id, etiqueta: nombreCompleto(e) }))
			},
			{ nombre: 'fecha', etiqueta: 'Fecha', tipo: 'fecha', requerido: true },
			{ nombre: 'estado', etiqueta: 'Estado', tipo: 'select', requerido: true, ancho: 'col-12', opciones: ESTADOS, ayuda: 'Si marcas “Ausente”, el acudiente recibe una notificación de la falla.' }
		];
	}

	async function cargar() {
		const c = await cargarCatalogos(['asistencias', 'cargas', 'cursos', 'asignaturas', 'docentes', 'estudiantes', 'matriculas', 'vinculos']);
		cat = c;
		const { docenteId } = perfilSesion();
		let filas = soloActivos(c.asistencias);
		if (docente) filas = filas.filter((a) => a.personal_institucionalid === docenteId);
		else if (!esAdministrador()) filas = filtrarPorEstudiante(filas, estudiantesPermitidos(c));
		return filas.map((a) => ({
			...a,
			fecha: a.fecha?.slice(0, 10),
			estudiante: nombreCompleto(c.estudiantes.find((e) => e.estudiante_id === a.estudianteid)),
			curso: c.cursos.find((x) => x.cursoid === a.cursoid)?.nombre_curso ?? '',
			asignatura: c.asignaturas.find((x) => x.materiaid === a.materiaid)?.nombre_materia ?? '',
			docente: nombreCompleto(c.docentes.find((d) => d.personalid === a.personal_institucionalid)) || 'Sin docente'
		}));
	}

	function aDatos(v) {
		const carga = cat.cargas.find((c) => c.cargaid === v.cargaid);
		if (!carga) throw new Error('Selecciona el curso y la asignatura.');
		return {
			estudianteid: v.estudianteid,
			cursoid: carga.cursoid,
			materiaid: carga.materiaid,
			personal_institucionalid: carga.personal_institucionalid,
			estado: v.estado,
			fecha: v.fecha,
			esta_activo: true
		};
	}

	function aFormulario(f) {
		const carga = cat.cargas.find((c) => c.cursoid === f.cursoid && c.materiaid === f.materiaid && c.personal_institucionalid === f.personal_institucionalid)
			?? cat.cargas.find((c) => c.cursoid === f.cursoid && c.materiaid === f.materiaid);
		return { cargaid: carga?.cargaid ?? null, estudianteid: f.estudianteid, fecha: f.fecha, estado: f.estado };
	}

	// ---------- Tomar lista completa de un curso ----------
	let listaAbierta = $state(false);
	let lista = $state({ cargaid: null, fecha: hoy() });
	let marcas = $state({});
	let guardandoLista = $state(false);
	let mensajeLista = $state('');
	let errorLista = $state('');
	const alumnosLista = $derived(estudiantesDeCarga(lista.cargaid));

	function abrirLista() {
		lista = { cargaid: opcionesCarga[0]?.valor ?? null, fecha: hoy() };
		marcas = {};
		mensajeLista = '';
		errorLista = '';
		listaAbierta = true;
	}

	function existente(carga, estudianteid, fecha) {
		return soloActivos(cat.asistencias).find(
			(a) => a.estudianteid === estudianteid && a.cursoid === carga.cursoid && a.materiaid === carga.materiaid && a.fecha?.slice(0, 10) === fecha
		);
	}

	$effect(() => {
		// Precarga lo que ya está registrado ese día para no duplicar.
		const carga = cat.cargas.find((c) => c.cargaid === lista.cargaid);
		const nuevas = {};
		for (const e of alumnosLista) nuevas[e.estudiante_id] = (carga && existente(carga, e.estudiante_id, lista.fecha)?.estado) || 'presente';
		marcas = nuevas;
	});

	async function guardarLista() {
		const carga = cat.cargas.find((c) => c.cargaid === lista.cargaid);
		if (!carga || !lista.fecha) return;
		guardandoLista = true;
		errorLista = '';
		let guardados = 0;
		try {
			for (const e of alumnosLista) {
				const datos = { estudianteid: e.estudiante_id, cursoid: carga.cursoid, materiaid: carga.materiaid, personal_institucionalid: carga.personal_institucionalid, estado: marcas[e.estudiante_id], fecha: lista.fecha, esta_activo: true };
				const previa = existente(carga, e.estudiante_id, lista.fecha);
				if (previa && previa.estado === datos.estado) continue;
				if (previa) await actualizarAsistencia(previa, datos);
				else await crearAsistencia(datos);
				guardados++;
			}
			const ausentes = alumnosLista.filter((e) => marcas[e.estudiante_id] === 'ausente').length;
			mensajeLista = `Se guardaron ${guardados} registros. ${ausentes ? `${ausentes} acudiente(s) recibirán la notificación de falla.` : 'No hubo fallas.'}`;
			await recargar?.();
		} catch (e) {
			errorLista = e.message;
		} finally {
			guardandoLista = false;
		}
	}
</script>

<svelte:head><title>Asistencia | Aula Presente</title></svelte:head>

<PaginaCrud
	titulo="Asistencia"
	descripcion={docente ? 'Registra la asistencia de tus cursos. Cada falla genera una notificación al acudiente.' : 'Registros de asistencia por estudiante, curso y asignatura.'}
	icono="bi-clipboard-check"
	recurso="registro de asistencia"
	textoCrear="Registro individual"
	bind:recargar
	{columnas}
	{campos}
	{cargar}
	ordenInicial={[[0, 'desc']]}
	valoresIniciales={() => ({ cargaid: opcionesCarga.length === 1 ? opcionesCarga[0].valor : null, estudianteid: null, fecha: hoy(), estado: 'ausente' })}
	{aFormulario}
	crear={(v) => crearAsistencia(aDatos(v))}
	actualizar={(f, v) => actualizarAsistencia(f, aDatos(v))}
	eliminar={eliminarAsistencia}
	describir={(f) => `la asistencia de ${f.estudiante} del ${formatearFecha(f.fecha)}`}
	puedeCrear={permisos.crear}
	puedeEditar={permisos.actualizar}
	puedeEliminar={permisos.eliminar}
>
	{#snippet superior()}
		{#if permisos.crear}
			<div class="card border-0 bg-primary-subtle mb-3">
				<div class="card-body d-flex flex-wrap align-items-center justify-content-between gap-2">
					<span><i class="bi bi-list-check me-2 text-primary"></i>Toma la asistencia de todo un curso en un solo paso.</span>
					<button type="button" class="btn btn-primary" onclick={abrirLista} disabled={!opcionesCarga.length}>
						<i class="bi bi-clipboard-plus me-1"></i>Tomar lista
					</button>
				</div>
			</div>
		{/if}
	{/snippet}
</PaginaCrud>

<VentanaModal bind:abierto={listaAbierta} titulo="Tomar lista" tamano="lg">
	<Alerta mensaje={errorLista} tipo="danger" />
	<Alerta mensaje={mensajeLista} tipo="success" />
	<div class="row g-3 mb-3">
		<div class="col-md-8">
			<CampoFormulario campo={{ nombre: 'lista-carga', etiqueta: 'Curso y asignatura', tipo: 'select', requerido: true, opciones: opcionesCarga }} bind:valor={lista.cargaid} />
		</div>
		<div class="col-md-4">
			<CampoFormulario campo={{ nombre: 'lista-fecha', etiqueta: 'Fecha', tipo: 'fecha', requerido: true }} bind:valor={lista.fecha} />
		</div>
	</div>
	{#if alumnosLista.length === 0}
		<p class="text-secondary">No hay estudiantes matriculados en este curso.</p>
	{:else}
		<ul class="list-group">
			{#each alumnosLista as alumno (alumno.estudiante_id)}
				<li class="list-group-item d-flex flex-wrap justify-content-between align-items-center gap-2">
					<span class="fw-semibold">{nombreCompleto(alumno)}</span>
					<div class="btn-group btn-group-sm" role="group" aria-label="Estado de {nombreCompleto(alumno)}">
						{#each ESTADOS as est (est.valor)}
							<input type="radio" class="btn-check" name="estado-{alumno.estudiante_id}" id="est-{alumno.estudiante_id}-{est.valor}" value={est.valor} bind:group={marcas[alumno.estudiante_id]} />
							<label class="btn btn-outline-{est.clase}" for="est-{alumno.estudiante_id}-{est.valor}">{est.etiqueta}</label>
						{/each}
					</div>
				</li>
			{/each}
		</ul>
	{/if}
	{#snippet pie()}
		<button type="button" class="btn btn-light" onclick={() => (listaAbierta = false)}>Cerrar</button>
		<button type="button" class="btn btn-primary" onclick={guardarLista} disabled={guardandoLista || !alumnosLista.length}>
			{#if guardandoLista}<span class="spinner-border spinner-border-sm me-1"></span>{/if}Guardar lista
		</button>
	{/snippet}
</VentanaModal>
