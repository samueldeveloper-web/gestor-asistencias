<script>
	import PaginaCrud from '$lib/components/PaginaCrud.svelte';
	import { crearExcusa, actualizarExcusa, eliminarExcusa, revisarExcusa } from '$lib/api/excusasApi.js';
	import { cargarCatalogos, estudiantesPermitidos, filtrarPorEstudiante, perfilSesion } from '$lib/catalogos.js';
	import { permisosDe, esAcudiente, esDocente, esAdministrador } from '$lib/sesion.js';
	import { nombreCompleto, soloActivos, formatearFecha, formatearFechaHora, insignia, escaparHtml } from '$lib/utilidades.js';

	const permisos = permisosDe('/excusas');
	const acudiente = esAcudiente();
	const revisor = esDocente() || esAdministrador();
	let cat = $state({ asistencias: [], estudiantes: [], asignaturas: [], excusas: [] });

	const columnas = [
		{ titulo: 'Fecha de la falla', campo: 'fecha_falla', render: (v, _f, t) => (t === 'display' ? formatearFecha(v) : v) },
		{ titulo: 'Estudiante', campo: 'estudiante', render: (v) => `<strong>${escaparHtml(v)}</strong>` },
		{ titulo: 'Asignatura', campo: 'asignatura' },
		{ titulo: 'Motivo', campo: 'motivo' },
		{ titulo: 'Presentada', campo: 'fecha_presentacion', render: (v, _f, t) => (t === 'display' ? formatearFechaHora(v) : v) },
		{ titulo: 'Estado', campo: 'estado', render: (v, _f, t) => (t === 'display' ? insignia(v) : v) }
	];

	function etiquetaFalla(a) {
		const e = nombreCompleto(cat.estudiantes.find((x) => x.estudiante_id === a.estudianteid));
		const m = cat.asignaturas.find((x) => x.materiaid === a.materiaid)?.nombre_materia ?? '';
		return `${e} · ${m} · ${formatearFecha(a.fecha)} (${a.estado})`;
	}

	// Fallas de mis hijos que todavía no tienen una excusa pendiente o aprobada.
	function fallasSinExcusa(incluir) {
		const permitidos = estudiantesPermitidos(cat);
		const conExcusa = new Set(cat.excusas.filter((x) => x.estado !== 'rechazada').map((x) => x.asistenciaid));
		return filtrarPorEstudiante(soloActivos(cat.asistencias), permitidos).filter(
			(a) => (['ausente', 'tarde'].includes(a.estado) && !conExcusa.has(a.asistenciaid)) || a.asistenciaid === incluir
		);
	}

	function campos(modo, fila) {
		if (modo === 'editar' && revisor) {
			return [
				{ nombre: 'motivo', etiqueta: 'Motivo presentado por el acudiente', tipo: 'textarea', ancho: 'col-12', deshabilitado: true },
				{ nombre: 'documento_adjunto', etiqueta: 'Soporte', tipo: 'texto', ancho: 'col-12', deshabilitado: true },
				{
					nombre: 'decision', etiqueta: 'Decisión', tipo: 'select', requerido: true, ancho: 'col-12',
					opciones: [{ valor: 'aprobada', etiqueta: 'Aprobar (la falla pasa a excusada)' }, { valor: 'rechazada', etiqueta: 'Rechazar' }]
				},
				{ nombre: 'observacion', etiqueta: 'Observación para el acudiente', tipo: 'textarea', ancho: 'col-12' }
			];
		}
		return [
			{ nombre: 'asistenciaid', etiqueta: 'Falla a justificar', tipo: 'select', requerido: true, ancho: 'col-12', opciones: fallasSinExcusa(fila?.asistenciaid).map((a) => ({ valor: a.asistenciaid, etiqueta: etiquetaFalla(a) })) },
			{ nombre: 'motivo', etiqueta: 'Motivo', tipo: 'textarea', requerido: true, ancho: 'col-12', marcador: 'Ej: cita médica, calamidad doméstica…' },
			{ nombre: 'documento_adjunto', etiqueta: 'Soporte (enlace o nombre del documento)', tipo: 'texto', ancho: 'col-12', marcador: 'incapacidad_medica.pdf' }
		];
	}

	async function cargar() {
		const c = await cargarCatalogos(['excusas', 'asistencias', 'estudiantes', 'asignaturas', 'vinculos', 'cargas', 'matriculas']);
		cat = c;
		const { docenteId, acudienteId } = perfilSesion();
		let filas = soloActivos(c.excusas);
		if (acudiente) filas = filas.filter((x) => x.acudienteid === acudienteId || estudiantesPermitidos(c).has(x.estudianteid));
		else if (esDocente()) {
			const mias = new Set(c.asistencias.filter((a) => a.personal_institucionalid === docenteId).map((a) => a.asistenciaid));
			filas = filas.filter((x) => mias.has(x.asistenciaid));
		} else if (!esAdministrador()) filas = filtrarPorEstudiante(filas, estudiantesPermitidos(c));
		return filas.map((x) => {
			const a = c.asistencias.find((y) => y.asistenciaid === x.asistenciaid);
			return {
				...x,
				fecha_falla: a?.fecha?.slice(0, 10) ?? '',
				estudiante: nombreCompleto(c.estudiantes.find((e) => e.estudiante_id === x.estudianteid)),
				asignatura: c.asignaturas.find((m) => m.materiaid === a?.materiaid)?.nombre_materia ?? ''
			};
		});
	}

	async function crear(v) {
		const { acudienteId } = perfilSesion();
		await crearExcusa({
			asistenciaid: v.asistenciaid,
			acudienteid: acudienteId,
			motivo: v.motivo.trim(),
			documento_adjunto: v.documento_adjunto?.trim() || null
		});
	}

	async function actualizar(fila, v) {
		// Docente o administrador: la API aprueba/rechaza y actualiza la asistencia a "excusado".
		if (revisor) return revisarExcusa(fila, v.decision === 'aprobada', v.observacion?.trim() ?? '');
		// Acudiente: corrige su excusa mientras siga pendiente.
		return actualizarExcusa(fila, { asistenciaid: v.asistenciaid, motivo: v.motivo.trim(), documento_adjunto: v.documento_adjunto?.trim() || null });
	}
</script>

<svelte:head><title>Excusas | Aula Presente</title></svelte:head>

<PaginaCrud
	titulo="Excusas"
	descripcion={acudiente ? 'Justifica las fallas de tus hijos. El docente revisará cada excusa.' : 'Excusas enviadas por los acudientes. Aprueba o rechaza cada una.'}
	icono="bi-envelope-paper"
	recurso="excusa"
	textoCrear="Nueva excusa"
	{columnas}
	{campos}
	{cargar}
	ordenInicial={[[4, 'desc']]}
	valoresIniciales={() => ({ asistenciaid: null, motivo: '', documento_adjunto: '' })}
	aFormulario={(f) => ({ asistenciaid: f.asistenciaid, motivo: f.motivo, documento_adjunto: f.documento_adjunto ?? '', decision: f.estado === 'pendiente' ? null : f.estado, observacion: '' })}
	crear={acudiente ? crear : null}
	{actualizar}
	eliminar={eliminarExcusa}
	describir={(f) => `la excusa de ${f.estudiante} del ${formatearFecha(f.fecha_falla)}`}
	puedeCrear={permisos.crear}
	puedeEditar={permisos.actualizar}
	puedeEliminar={permisos.eliminar}
	puedeEditarFila={(f) => revisor || f.estado === 'pendiente'}
/>
