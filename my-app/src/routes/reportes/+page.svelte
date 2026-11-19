<script>
	/**
	 * Módulo de reportes (Corte 3).
	 * Filtros: rango de fechas (obligatorio), curso, asignatura, estudiante y estado.
	 * Acciones: visualizar en tabla, exportar a PDF o Excel y enviar por correo.
	 * La API limita los datos al alcance del rol (docente, acudiente, estudiante).
	 */
	import { onMount } from 'svelte';
	import EncabezadoPagina from '$lib/components/EncabezadoPagina.svelte';
	import Alerta from '$lib/components/Alerta.svelte';
	import TablaDatos from '$lib/components/TablaDatos.svelte';
	import TarjetaIndicador from '$lib/components/TarjetaIndicador.svelte';
	import CampoFormulario from '$lib/components/CampoFormulario.svelte';
	import VentanaModal from '$lib/components/VentanaModal.svelte';
	import Cargando from '$lib/components/Cargando.svelte';
	import { TIPOS_REPORTE, verReporte, descargarReporte, enviarReporte } from '$lib/api/reportesApi.js';
	import { guardarArchivo } from '$lib/api/http.js';
	import { cargarCatalogos, estudiantesPermitidos } from '$lib/catalogos.js';
	import { obtenerUsuario } from '$lib/sesion.js';
	import { nombreCompleto, soloActivos, opciones, insignia, escaparHtml, hoy } from '$lib/utilidades.js';

	const ESTADOS = [
		{ valor: 'presente', etiqueta: 'Presente' },
		{ valor: 'ausente', etiqueta: 'Ausente (falla)' },
		{ valor: 'tarde', etiqueta: 'Tarde' },
		{ valor: 'excusado', etiqueta: 'Excusado' }
	];
	const ICONOS = ['bi-list-check', 'bi-check-circle', 'bi-x-circle', 'bi-clock-history', 'bi-file-earmark-check', 'bi-percent'];
	const COLORES = ['primary', 'success', 'danger', 'warning', 'info', 'primary'];

	const primerDiaMes = () => `${hoy().slice(0, 8)}01`;

	let filtros = $state({
		tipo: 'asistencia',
		fecha_inicio: primerDiaMes(),
		fecha_fin: hoy(),
		cursoid: null,
		materiaid: null,
		estudianteid: null,
		estado: null
	});
	let cat = $state({ cursos: [], asignaturas: [], estudiantes: [], vinculos: [], cargas: [], matriculas: [] });
	let reporte = $state(null);
	let cargando = $state(false);
	let descargando = $state('');
	let error = $state('');
	let exito = $state('');

	let envioAbierto = $state(false);
	let envio = $state({ correo: obtenerUsuario()?.email ?? '', formato: 'pdf', mensaje: '' });
	let enviando = $state(false);

	// Campos del formulario de filtros (selects con nombres, nunca IDs)
	let campos = $derived.by(() => {
		const permitidos = estudiantesPermitidos(cat);
		const estudiantes = soloActivos(cat.estudiantes).filter((e) => !permitidos || permitidos.has(e.estudiante_id));
		return [
			{ nombre: 'tipo', etiqueta: 'Tipo de reporte', tipo: 'select', requerido: true, opciones: TIPOS_REPORTE },
			{ nombre: 'fecha_inicio', etiqueta: 'Desde', tipo: 'fecha', requerido: true },
			{ nombre: 'fecha_fin', etiqueta: 'Hasta', tipo: 'fecha', requerido: true },
			{ nombre: 'cursoid', etiqueta: 'Curso', tipo: 'select', marcador: 'Todos los cursos', opciones: opciones(soloActivos(cat.cursos), 'cursoid', 'nombre_curso') },
			{ nombre: 'materiaid', etiqueta: 'Asignatura', tipo: 'select', marcador: 'Todas las asignaturas', opciones: opciones(soloActivos(cat.asignaturas), 'materiaid', 'nombre_materia') },
			{ nombre: 'estudianteid', etiqueta: 'Estudiante', tipo: 'select', marcador: 'Todos los estudiantes', opciones: opciones(estudiantes, 'estudiante_id', nombreCompleto) },
			{ nombre: 'estado', etiqueta: 'Estado de asistencia', tipo: 'select', marcador: 'Todos los estados', opciones: ESTADOS }
		];
	});

	// Columnas para DataTables según el reporte que devolvió la API
	let columnas = $derived(
		(reporte?.columnas ?? []).map((c) => ({
			titulo: c.titulo,
			campo: c.campo,
			render: (v, _f, t) => {
				if (t !== 'display') return v;
				if (c.campo === 'estado' || c.campo === 'correo' || c.campo === 'lectura') return insignia(v);
				if (c.campo === 'porcentaje_asistencia') return `<strong class="text-${v < 80 ? 'danger' : 'success'}">${String(v).replace('.', ',')} %</strong>`;
				if (c.campo === 'estudiante') return `<strong>${escaparHtml(v)}</strong>`;
				return escaparHtml(v ?? '');
			}
		}))
	);

	const filtrosApi = () => {
		const { tipo, ...resto } = $state.snapshot(filtros);
		return resto;
	};

	function validar() {
		if (!filtros.fecha_inicio || !filtros.fecha_fin) return 'Selecciona el rango de fechas.';
		if (filtros.fecha_fin < filtros.fecha_inicio) return 'La fecha final no puede ser anterior a la inicial.';
		return '';
	}

	async function consultar(evento) {
		evento?.preventDefault();
		error = validar();
		exito = '';
		if (error) return;
		cargando = true;
		try {
			reporte = await verReporte(filtros.tipo, filtrosApi());
		} catch (e) {
			error = e.message;
			reporte = null;
		} finally {
			cargando = false;
		}
	}

	async function descargar(formato) {
		error = validar();
		exito = '';
		if (error) return;
		descargando = formato;
		try {
			const archivo = await descargarReporte(filtros.tipo, formato, filtrosApi());
			if (window.Capacitor?.isNativePlatform?.()) {
				exito = 'En la app móvil usa "Enviar por correo" para recibir el archivo.';
			} else {
				guardarArchivo(archivo);
				exito = `Se descargó ${archivo.nombre}.`;
			}
		} catch (e) {
			error = e.message;
		} finally {
			descargando = '';
		}
	}

	async function enviar(evento) {
		evento.preventDefault();
		error = validar();
		if (error) return;
		enviando = true;
		try {
			const r = await enviarReporte(filtros.tipo, { ...filtrosApi(), ...$state.snapshot(envio) });
			exito = `${r.mensaje} (${r.registros} registros).`;
			error = '';
			envioAbierto = false;
		} catch (e) {
			error = e.message;
			envioAbierto = false;
		} finally {
			enviando = false;
		}
	}

	onMount(async () => {
		try {
			cat = await cargarCatalogos(['cursos', 'asignaturas', 'estudiantes', 'vinculos', 'cargas', 'matriculas']);
		} catch (e) {
			error = e.message;
		}
		consultar();
	});
</script>

<EncabezadoPagina titulo="Reportes" icono="bi-file-earmark-bar-graph" seccion="Corte 3" descripcion="Consulta la asistencia, expórtala en PDF o Excel y envíala por correo.">
	<button class="btn btn-outline-danger" onclick={() => descargar('pdf')} disabled={!!descargando}>
		<i class="bi bi-file-earmark-pdf me-1"></i>{descargando === 'pdf' ? 'Generando…' : 'PDF'}
	</button>
	<button class="btn btn-outline-success" onclick={() => descargar('excel')} disabled={!!descargando}>
		<i class="bi bi-file-earmark-excel me-1"></i>{descargando === 'excel' ? 'Generando…' : 'Excel'}
	</button>
	<button class="btn btn-primary" onclick={() => (envioAbierto = true)}>
		<i class="bi bi-envelope me-1"></i>Enviar por correo
	</button>
</EncabezadoPagina>

<Alerta mensaje={error} tipo="danger" alCerrar={() => (error = '')} />
<Alerta mensaje={exito} tipo="success" alCerrar={() => (exito = '')} />

<form class="card border-0 mb-4" onsubmit={consultar}>
	<div class="card-body">
		<div class="row g-3 align-items-end">
			{#each campos as campo (campo.nombre)}
				<div class={campo.nombre === 'tipo' ? 'col-12 col-md-6 col-xl-3' : 'col-6 col-md-3 col-xl'}>
					<CampoFormulario {campo} bind:valor={filtros[campo.nombre]} />
				</div>
			{/each}
		</div>
		<div class="d-flex flex-wrap gap-2 justify-content-end mt-3">
			<button type="button" class="btn btn-light" onclick={() => { filtros = { ...filtros, cursoid: null, materiaid: null, estudianteid: null, estado: null, fecha_inicio: primerDiaMes(), fecha_fin: hoy() }; consultar(); }}>
				<i class="bi bi-arrow-counterclockwise me-1"></i>Limpiar filtros
			</button>
			<button type="submit" class="btn btn-primary" disabled={cargando}>
				<i class="bi bi-search me-1"></i>{cargando ? 'Consultando…' : 'Ver reporte'}
			</button>
		</div>
	</div>
</form>

{#if cargando && !reporte}
	<Cargando mensaje="Generando reporte…" />
{:else if reporte}
	<div class="row g-3 mb-4">
		{#each reporte.resumen as item, i (item.etiqueta)}
			<div class="col-6 col-md-4 col-xl-2">
				<TarjetaIndicador titulo={item.etiqueta} valor={item.valor} icono={ICONOS[i % ICONOS.length]} color={COLORES[i % COLORES.length]} />
			</div>
		{/each}
	</div>

	<div class="card border-0">
		<div class="card-body">
			<h2 class="h5 fw-bold mb-1">{reporte.titulo}</h2>
			<p class="small text-secondary mb-3">
				{#each reporte.filtros as f, i (f.etiqueta)}{i ? ' · ' : ''}<strong>{f.etiqueta}:</strong> {f.valor}{/each}
			</p>
			<TablaDatos {columnas} filas={reporte.filas} ordenInicial={[]} />
		</div>
	</div>
{/if}

<VentanaModal bind:abierto={envioAbierto} titulo="Enviar reporte por correo">
	<form id="form-envio" onsubmit={enviar} class="row g-3">
		<div class="col-12">
			<CampoFormulario campo={{ nombre: 'correo', etiqueta: 'Correo del destinatario', tipo: 'email', requerido: true }} bind:valor={envio.correo} />
		</div>
		<div class="col-12">
			<CampoFormulario campo={{ nombre: 'formato', etiqueta: 'Formato del archivo', tipo: 'select', requerido: true, opciones: [{ valor: 'pdf', etiqueta: 'PDF' }, { valor: 'excel', etiqueta: 'Excel' }] }} bind:valor={envio.formato} />
		</div>
		<div class="col-12">
			<CampoFormulario campo={{ nombre: 'mensaje', etiqueta: 'Mensaje (opcional)', tipo: 'textarea', maximo: 500 }} bind:valor={envio.mensaje} />
		</div>
		<p class="small text-secondary mb-0">Se enviará el reporte "{TIPOS_REPORTE.find((t) => t.valor === filtros.tipo)?.etiqueta}" con los filtros actuales.</p>
	</form>
	{#snippet pie()}
		<button type="button" class="btn btn-light" onclick={() => (envioAbierto = false)}>Cancelar</button>
		<button type="submit" form="form-envio" class="btn btn-primary" disabled={enviando}>
			<i class="bi bi-send me-1"></i>{enviando ? 'Enviando…' : 'Enviar'}
		</button>
	{/snippet}
</VentanaModal>
