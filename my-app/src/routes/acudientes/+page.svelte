<script>
	import PaginaCrud from '$lib/components/PaginaCrud.svelte';
	import { crearAcudiente, actualizarAcudiente, eliminarAcudiente } from '$lib/api/acudientesApi.js';
	import { crearVinculo, actualizarVinculo, eliminarVinculo, ID_VINCULO } from '$lib/api/estudianteAcudienteApi.js';
	import { cargarCatalogos } from '$lib/catalogos.js';
	import { permisosDe } from '$lib/sesion.js';
	import { nombreCompleto, soloActivos, escaparHtml, opciones, insignia } from '$lib/utilidades.js';

	const permisos = permisosDe('/acudientes');
	const PARENTESCOS = ['Madre', 'Padre', 'Abuelo(a)', 'Tío(a)', 'Hermano(a)', 'Tutor legal', 'Otro'];

	const columnas = [
		{ titulo: 'Acudiente', render: (_v, f) => `<strong>${escaparHtml(nombreCompleto(f))}</strong>` },
		{ titulo: 'Documento', campo: 'documento_identidad' },
		{ titulo: 'Teléfono', campo: 'telefono' },
		{ titulo: 'Correo', campo: 'email' },
		{ titulo: 'Estudiantes a cargo', campo: 'hijos' }
	];

	const camposBase = [
		{ nombre: 'nombres', etiqueta: 'Nombres', tipo: 'texto', requerido: true, maximo: 100 },
		{ nombre: 'apellidos', etiqueta: 'Apellidos', tipo: 'texto', requerido: true, maximo: 100 },
		{ nombre: 'documento_identidad', etiqueta: 'Documento de identidad', tipo: 'texto', requerido: true, maximo: 20 },
		{ nombre: 'fecha_nacimiento', etiqueta: 'Fecha de nacimiento', tipo: 'fecha' },
		{ nombre: 'telefono', etiqueta: 'Teléfono', tipo: 'telefono', requerido: true, maximo: 20 },
		{ nombre: 'email', etiqueta: 'Correo electrónico', tipo: 'email', requerido: true, ayuda: 'A este correo llegan las notificaciones de fallas.' },
		{ nombre: 'direccion', etiqueta: 'Dirección', tipo: 'texto', ancho: 'col-12' }
	];

	// El formulario de acudiente incluye la asignación de sus hijos o estudiantes a cargo.
	const campos = () => [
		...camposBase,
		{
			nombre: 'hijos', etiqueta: 'Estudiantes a cargo', tipo: 'estudiantes', ancho: 'col-12',
			opciones: opciones(soloActivos(cat.estudiantes), 'estudiante_id', nombreCompleto),
			parentescos: PARENTESCOS,
			ayuda: 'Agrega los hijos o estudiantes que tiene a cargo, con su parentesco.'
		}
	];

	const hijosDe = (acudienteId) =>
		soloActivos(cat.vinculos)
			.filter((v) => v.acudienteid === acudienteId)
			.map((v) => ({ [ID_VINCULO]: v[ID_VINCULO], estudianteid: v.estudianteid, parentesco: v.parentesco, contacto_principal: !!v.contacto_principal }));

	/** Guarda los cambios de la lista de hijos: crea los nuevos, actualiza los cambiados y quita los eliminados. */
	async function sincronizarHijos(acudienteId, hijos = []) {
		const actuales = hijosDe(acudienteId);
		for (const previo of actuales) {
			if (!hijos.some((h) => h.estudianteid === previo.estudianteid)) await eliminarVinculo(previo);
		}
		for (const h of hijos) {
			const previo = actuales.find((x) => x.estudianteid === h.estudianteid);
			const datos = { estudianteid: h.estudianteid, acudienteid: acudienteId, parentesco: h.parentesco, contacto_principal: !!h.contacto_principal };
			if (previo && previo.parentesco === datos.parentesco && previo.contacto_principal === datos.contacto_principal) continue;
			if (datos.contacto_principal) await quitarPrincipalAnterior(h.estudianteid, previo?.[ID_VINCULO] ?? null);
			if (previo) await actualizarVinculo(previo, datos);
			else await crearVinculo(datos);
		}
	}

	async function crearConHijos(v) {
		const respuesta = await crearAcudiente(aDatos(v));
		const id = respuesta?.id ?? respuesta?.data?.acudiente_id;
		if (v.hijos?.length) {
			if (!id) throw new Error('El acudiente se creó, pero la API no devolvió su identificador para asignar los estudiantes.');
			await sincronizarHijos(id, v.hijos);
		}
		await recargarVinculos?.();
	}

	async function actualizarConHijos(fila, v) {
		await actualizarAcudiente(fila, aDatos(v));
		await sincronizarHijos(fila.acudiente_id, v.hijos ?? []);
		await recargarVinculos?.();
	}

	let cat = $state({ acudientes: [], estudiantes: [], vinculos: [] });
	let recargarAcudientes = $state();
	let recargarVinculos = $state();

	async function cargar() {
		const c = await cargarCatalogos(['acudientes', 'vinculos', 'estudiantes']);
		cat = c;
		return soloActivos(c.acudientes).map((a) => ({
			...a,
			hijos:
				c.vinculos
					.filter((v) => v.acudienteid === a.acudiente_id && (v.esta_activo ?? true))
					.map((v) => nombreCompleto(c.estudiantes.find((e) => e.estudiante_id === v.estudianteid)))
					.join(', ') || 'Ninguno'
		}));
	}

	const aDatos = (v) => ({
		nombres: v.nombres?.trim(),
		apellidos: v.apellidos?.trim(),
		documento_identidad: v.documento_identidad?.trim(),
		fecha_nacimiento: v.fecha_nacimiento || null,
		telefono: v.telefono?.trim(),
		email: v.email?.trim(),
		direccion: v.direccion?.trim() || null,
		esta_activo: true
	});

	// ----- Estudiantes a cargo de cada acudiente (tabla estudiante_acudiente) -----

	const columnasVinculos = [
		{ titulo: 'Acudiente', campo: 'acudiente', render: (v) => `<strong>${escaparHtml(v)}</strong>` },
		{ titulo: 'Estudiante', campo: 'estudiante' },
		{ titulo: 'Parentesco', campo: 'parentesco' },
		{ titulo: 'Contacto principal', campo: 'contacto_principal', render: (v, _f, t) => (t === 'display' ? (v ? insignia('Sí') : 'No') : v) }
	];

	const camposVinculos = () => [
		{ nombre: 'acudienteid', etiqueta: 'Acudiente', tipo: 'select', requerido: true, opciones: opciones(soloActivos(cat.acudientes), 'acudiente_id', nombreCompleto) },
		{ nombre: 'estudianteid', etiqueta: 'Estudiante', tipo: 'select', requerido: true, opciones: opciones(soloActivos(cat.estudiantes), 'estudiante_id', nombreCompleto) },
		{ nombre: 'parentesco', etiqueta: 'Parentesco', tipo: 'select', requerido: true, opciones: PARENTESCOS.map((p) => ({ valor: p, etiqueta: p })) },
		{ nombre: 'contacto_principal', etiqueta: 'Es el contacto principal (recibe primero los avisos)', tipo: 'casilla', ancho: 'col-md-6 d-flex align-items-end' }
	];

	async function cargarVinculos() {
		const c = await cargarCatalogos(['vinculos', 'acudientes', 'estudiantes']);
		cat = c;
		return soloActivos(c.vinculos).map((v) => ({
			...v,
			acudiente: nombreCompleto(c.acudientes.find((a) => a.acudiente_id === v.acudienteid)),
			estudiante: nombreCompleto(c.estudiantes.find((e) => e.estudiante_id === v.estudianteid))
		}));
	}

	// Un estudiante solo puede tener un contacto principal: se le quita al anterior antes de guardar.
	async function quitarPrincipalAnterior(estudianteid, excepto = null) {
		const anteriores = soloActivos(cat.vinculos).filter((v) => v.estudianteid === estudianteid && v.contacto_principal && v[ID_VINCULO] !== excepto);
		for (const v of anteriores) await actualizarVinculo(v, { contacto_principal: false });
	}

	const datosVinculo = (v) => ({ estudianteid: v.estudianteid, acudienteid: v.acudienteid, parentesco: v.parentesco, contacto_principal: !!v.contacto_principal });

	async function crearVinculoNuevo(v) {
		const yaExiste = soloActivos(cat.vinculos).some((x) => x.estudianteid === v.estudianteid && x.acudienteid === v.acudienteid);
		if (yaExiste) throw new Error('Ese estudiante ya está a cargo de ese acudiente.');
		if (v.contacto_principal) await quitarPrincipalAnterior(v.estudianteid);
		await crearVinculo(datosVinculo(v));
		await recargarAcudientes?.();
	}

	async function actualizarVinculoExistente(fila, v) {
		if (v.contacto_principal) await quitarPrincipalAnterior(v.estudianteid, fila[ID_VINCULO]);
		await actualizarVinculo(fila, datosVinculo(v));
		await recargarAcudientes?.();
	}

	async function eliminarVinculoExistente(fila) {
		await eliminarVinculo(fila);
		await recargarAcudientes?.();
	}
</script>

<svelte:head><title>Acudientes | Aula Presente</title></svelte:head>

<PaginaCrud
	titulo="Acudientes"
	descripcion="Padres, madres o tutores que reciben las notificaciones de asistencia."
	icono="bi-people"
	recurso="acudiente"
	bind:recargar={recargarAcudientes}
	{columnas}
	{campos}
	{cargar}
	valoresIniciales={() => ({ nombres: '', apellidos: '', documento_identidad: '', fecha_nacimiento: '', telefono: '', email: '', direccion: '', hijos: [] })}
	aFormulario={(f) => ({ ...f, fecha_nacimiento: f.fecha_nacimiento?.slice(0, 10) ?? '', hijos: hijosDe(f.acudiente_id) })}
	crear={crearConHijos}
	actualizar={actualizarConHijos}
	eliminar={eliminarAcudiente}
	describir={(f) => `al acudiente ${nombreCompleto(f)}`}
	puedeCrear={permisos.crear}
	puedeEditar={permisos.actualizar}
	puedeEliminar={permisos.eliminar}
/>

<div class="mt-5">
	<PaginaCrud
		titulo="Estudiantes a cargo"
		descripcion="Asigna cada estudiante a su acudiente. Un estudiante puede tener varios acudientes, pero solo un contacto principal."
		icono="bi-link-45deg"
		recurso="vínculo"
		textoCrear="Asignar estudiante"
		bind:recargar={recargarVinculos}
		columnas={columnasVinculos}
		campos={camposVinculos}
		cargar={cargarVinculos}
		valoresIniciales={() => ({ acudienteid: null, estudianteid: null, parentesco: null, contacto_principal: true })}
		aFormulario={(f) => ({ acudienteid: f.acudienteid, estudianteid: f.estudianteid, parentesco: f.parentesco, contacto_principal: f.contacto_principal })}
		crear={crearVinculoNuevo}
		actualizar={actualizarVinculoExistente}
		eliminar={eliminarVinculoExistente}
		describir={(f) => `el vínculo de ${f.estudiante} con ${f.acudiente}`}
		puedeCrear={permisos.crear}
		puedeEditar={permisos.actualizar}
		puedeEliminar={permisos.eliminar}
	/>
</div>
