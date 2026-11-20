<script>
	import PaginaCrud from '$lib/components/PaginaCrud.svelte';
	import { crearAcudiente, actualizarAcudiente, eliminarAcudiente } from '$lib/api/acudientesApi.js';
	import { crearVinculo, actualizarVinculo, eliminarVinculo, ID_VINCULO } from '$lib/api/estudianteAcudienteApi.js';
	import { cargarCatalogos } from '$lib/catalogos.js';
	import { permisosDe } from '$lib/sesion.js';
	import { nombreCompleto, soloActivos, escaparHtml, opciones } from '$lib/utilidades.js';

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
	}

	async function actualizarConHijos(fila, v) {
		await actualizarAcudiente(fila, aDatos(v));
		await sincronizarHijos(fila.acudiente_id, v.hijos ?? []);
	}

	let cat = $state({ acudientes: [], estudiantes: [], vinculos: [] });

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

	// Un estudiante solo puede tener un contacto principal: se le quita al anterior antes de guardar.
	async function quitarPrincipalAnterior(estudianteid, excepto = null) {
		const anteriores = soloActivos(cat.vinculos).filter((v) => v.estudianteid === estudianteid && v.contacto_principal && v[ID_VINCULO] !== excepto);
		for (const v of anteriores) await actualizarVinculo(v, { contacto_principal: false });
	}

</script>

<svelte:head><title>Acudientes | Aula Presente</title></svelte:head>

<PaginaCrud
	titulo="Acudientes"
	descripcion="Padres, madres o tutores que reciben las notificaciones de asistencia."
	icono="bi-people"
	recurso="acudiente"
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

