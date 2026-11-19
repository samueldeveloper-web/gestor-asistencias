<script>
	import PaginaCrud from '$lib/components/PaginaCrud.svelte';
	import { crearAcudiente, actualizarAcudiente, eliminarAcudiente } from '$lib/api/acudientesApi.js';
	import { cargarCatalogos } from '$lib/catalogos.js';
	import { permisosDe } from '$lib/sesion.js';
	import { nombreCompleto, soloActivos, escaparHtml } from '$lib/utilidades.js';

	const permisos = permisosDe('/acudientes');

	const columnas = [
		{ titulo: 'Acudiente', render: (_v, f) => `<strong>${escaparHtml(nombreCompleto(f))}</strong>` },
		{ titulo: 'Documento', campo: 'documento_identidad' },
		{ titulo: 'Teléfono', campo: 'telefono' },
		{ titulo: 'Correo', campo: 'email' },
		{ titulo: 'Estudiantes a cargo', campo: 'hijos' }
	];

	const campos = [
		{ nombre: 'nombres', etiqueta: 'Nombres', tipo: 'texto', requerido: true, maximo: 100 },
		{ nombre: 'apellidos', etiqueta: 'Apellidos', tipo: 'texto', requerido: true, maximo: 100 },
		{ nombre: 'documento_identidad', etiqueta: 'Documento de identidad', tipo: 'texto', requerido: true, maximo: 20 },
		{ nombre: 'fecha_nacimiento', etiqueta: 'Fecha de nacimiento', tipo: 'fecha' },
		{ nombre: 'telefono', etiqueta: 'Teléfono', tipo: 'telefono', requerido: true, maximo: 20 },
		{ nombre: 'email', etiqueta: 'Correo electrónico', tipo: 'email', requerido: true, ayuda: 'A este correo llegan las notificaciones de fallas.' },
		{ nombre: 'direccion', etiqueta: 'Dirección', tipo: 'texto', ancho: 'col-12' }
	];

	async function cargar() {
		const c = await cargarCatalogos(['acudientes', 'vinculos', 'estudiantes']);
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
	valoresIniciales={() => ({ nombres: '', apellidos: '', documento_identidad: '', fecha_nacimiento: '', telefono: '', email: '', direccion: '' })}
	aFormulario={(f) => ({ ...f, fecha_nacimiento: f.fecha_nacimiento?.slice(0, 10) ?? '' })}
	crear={(v) => crearAcudiente(aDatos(v))}
	actualizar={(f, v) => actualizarAcudiente(f, aDatos(v))}
	eliminar={eliminarAcudiente}
	describir={(f) => `al acudiente ${nombreCompleto(f)}`}
	puedeCrear={permisos.crear}
	puedeEditar={permisos.actualizar}
	puedeEliminar={permisos.eliminar}
/>
