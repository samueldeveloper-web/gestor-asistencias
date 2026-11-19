<script>
	import PaginaCrud from '$lib/components/PaginaCrud.svelte';
	import VentanaModal from '$lib/components/VentanaModal.svelte';
	import EtiquetaEstado from '$lib/components/EtiquetaEstado.svelte';
	import { crearNotificacion, actualizarNotificacion, eliminarNotificacion, marcarNotificacionLeida, enviarNotificacionesPendientes } from '$lib/api/notificacionesApi.js';
	import Alerta from '$lib/components/Alerta.svelte';
	import { cargarCatalogos, estudiantesPermitidos, perfilSesion } from '$lib/catalogos.js';
	import { permisosDe, esAcudiente, esAdministrador } from '$lib/sesion.js';
	import { nombreCompleto, soloActivos, formatearFechaHora, insignia, opciones, escaparHtml } from '$lib/utilidades.js';

	const permisos = permisosDe('/notificaciones');
	const acudiente = esAcudiente();
	let cat = $state({ acudientes: [], estudiantes: [], vinculos: [] });
	let recargar = $state();
	let leyendo = $state(null);
	let lecturaAbierta = $state(false);

	const TIPOS = [
		{ valor: 'asistencia', etiqueta: 'Asistencia' },
		{ valor: 'excusa', etiqueta: 'Excusa' },
		{ valor: 'general', etiqueta: 'General' }
	];

	const columnas = [
		{ titulo: 'Fecha', campo: 'fecha_envio', render: (v, _f, t) => (t === 'display' ? formatearFechaHora(v) : v) },
		...(acudiente ? [] : [{ titulo: 'Acudiente', campo: 'acudiente' }]),
		{ titulo: 'Estudiante', campo: 'estudiante' },
		{ titulo: 'Título', campo: 'titulo', render: (v, f) => (f.leido ? escaparHtml(v) : `<strong>${escaparHtml(v)}</strong>`) },
		{ titulo: 'Tipo', campo: 'tipo', render: (v, _f, t) => (t === 'display' ? insignia(v) : v) },
		...(acudiente ? [] : [{ titulo: 'Correo', campo: 'enviado_correo', render: (v, _f, t) => (t === 'display' ? (v ? insignia('enviada') : insignia('pendiente')) : v) }]),
		{ titulo: 'Lectura', campo: 'leido', render: (v, _f, t) => (t === 'display' ? insignia(v ? 'leida' : 'no leida').replace('Leida', 'Leída').replace('No leida', 'No leída') : v) }
	];

	function campos(_modo, _fila, valores) {
		const permitidos = estudiantesPermitidos(cat);
		const hijos = new Set(cat.vinculos.filter((v) => v.acudienteid === valores?.acudienteid).map((v) => v.estudianteid));
		const acudientesVisibles = soloActivos(cat.acudientes).filter(
			(a) => !permitidos || cat.vinculos.some((v) => v.acudienteid === a.acudiente_id && permitidos.has(v.estudianteid))
		);
		return [
			{ nombre: 'acudienteid', etiqueta: 'Acudiente', tipo: 'select', requerido: true, opciones: opciones(acudientesVisibles, 'acudiente_id', nombreCompleto) },
			{ nombre: 'estudianteid', etiqueta: 'Estudiante', tipo: 'select', marcador: 'Sin estudiante específico', opciones: opciones(soloActivos(cat.estudiantes).filter((e) => hijos.has(e.estudiante_id)), 'estudiante_id', nombreCompleto) },
			{ nombre: 'tipo', etiqueta: 'Tipo', tipo: 'select', requerido: true, opciones: TIPOS },
			{ nombre: 'titulo', etiqueta: 'Título', tipo: 'texto', requerido: true, maximo: 150 },
			{ nombre: 'mensaje', etiqueta: 'Mensaje', tipo: 'textarea', requerido: true, ancho: 'col-12' },
			{ nombre: 'leido', etiqueta: 'Marcar como leída', tipo: 'casilla', ancho: 'col-12' }
		];
	}

	async function cargar() {
		const c = await cargarCatalogos(['notificaciones', 'acudientes', 'estudiantes', 'vinculos', 'cargas', 'matriculas']);
		cat = c;
		const { acudienteId } = perfilSesion();
		let filas = soloActivos(c.notificaciones);
		if (acudiente) filas = filas.filter((n) => n.acudienteid === acudienteId);
		else if (!esAdministrador()) {
			const permitidos = estudiantesPermitidos(c);
			filas = filas.filter((n) => !permitidos || permitidos.has(n.estudianteid));
		}
		return filas.map((n) => ({
			...n,
			acudiente: nombreCompleto(c.acudientes.find((a) => a.acudiente_id === n.acudienteid)),
			estudiante: nombreCompleto(c.estudiantes.find((e) => e.estudiante_id === n.estudianteid)) || '—'
		}));
	}

	const aDatos = (v, fila = {}) => ({
		acudienteid: v.acudienteid,
		estudianteid: v.estudianteid ?? null,
		tipo: v.tipo,
		titulo: v.titulo?.trim(),
		mensaje: v.mensaje?.trim(),
		leido: !!v.leido
	});

	let envio = $state('');
	let enviando = $state(false);
	async function enviarPendientes() {
		enviando = true;
		envio = '';
		try {
			const r = await enviarNotificacionesPendientes();
			envio = `Correos enviados: ${r.enviadas ?? 0} de ${r.pendientes ?? 0} pendientes${r.sin_correo ? ` (${r.sin_correo} acudientes sin correo)` : ''}.`;
			await recargar?.();
		} catch (e) {
			envio = e.message;
		} finally {
			enviando = false;
		}
	}

	async function abrirLectura(fila) {
		leyendo = fila;
		lecturaAbierta = true;
		if (!fila.leido && acudiente) {
			await marcarNotificacionLeida(fila);
			await recargar?.();
		}
	}
</script>

<svelte:head><title>Notificaciones | Aula Presente</title></svelte:head>

<PaginaCrud
	titulo="Notificaciones"
	descripcion={acudiente ? 'Avisos de fallas y novedades de tus hijos.' : 'Avisos enviados a los acudientes. Las fallas generan una notificación automática.'}
	icono="bi-bell"
	recurso="notificación"
	textoCrear="Nueva notificación"
	bind:recargar
	{columnas}
	{campos}
	{cargar}
	ordenInicial={[[0, 'desc']]}
	valoresIniciales={() => ({ acudienteid: null, estudianteid: null, tipo: 'general', titulo: '', mensaje: '', leido: false })}
	aFormulario={(f) => ({ acudienteid: f.acudienteid, estudianteid: f.estudianteid, tipo: f.tipo, titulo: f.titulo, mensaje: f.mensaje, leido: f.leido })}
	crear={(v) => crearNotificacion(aDatos(v))}
	actualizar={(f, v) => actualizarNotificacion(f, aDatos(v, f))}
	eliminar={eliminarNotificacion}
	describir={(f) => `la notificación “${f.titulo}”`}
	puedeCrear={permisos.crear}
	puedeEditar={permisos.actualizar && !acudiente}
	puedeEliminar={permisos.eliminar}
	accionesExtra={[{ titulo: 'Leer', icono: 'bi-envelope-open', clase: 'btn-outline-secondary', alHacerClic: abrirLectura }]}
>
	{#snippet superior()}
		{#if esAdministrador()}
			<div class="d-flex flex-wrap align-items-center gap-2 mb-3">
				<button type="button" class="btn btn-outline-primary" onclick={enviarPendientes} disabled={enviando}>
					{#if enviando}<span class="spinner-border spinner-border-sm me-1"></span>{:else}<i class="bi bi-send me-1"></i>{/if}Enviar correos pendientes
				</button>
				<Alerta mensaje={envio} tipo="info" alCerrar={() => (envio = '')} />
			</div>
		{/if}
	{/snippet}
</PaginaCrud>

<VentanaModal bind:abierto={lecturaAbierta} titulo={leyendo?.titulo ?? ''}>
	{#if leyendo}
		<p class="small text-secondary mb-2">
			{formatearFechaHora(leyendo.fecha_envio)} · <EtiquetaEstado texto={leyendo.tipo} />
			{#if leyendo.estudiante !== '—'}· {leyendo.estudiante}{/if}
		</p>
		<p class="mb-0" style="white-space: pre-line">{leyendo.mensaje}</p>
	{/if}
</VentanaModal>
