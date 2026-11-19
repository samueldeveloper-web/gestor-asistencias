<script>
	import PaginaCrud from '$lib/components/PaginaCrud.svelte';
	import { listarDocentes, crearDocente, actualizarDocente, eliminarDocente } from '$lib/api/docentesApi.js';
	import { permisosDe } from '$lib/sesion.js';
	import { nombreCompleto, soloActivos, escaparHtml } from '$lib/utilidades.js';

	const permisos = permisosDe('/docentes');

	const columnas = [
		{ titulo: 'Nombre', render: (_v, f) => `<strong>${escaparHtml(nombreCompleto(f))}</strong>` },
		{ titulo: 'Cargo', campo: 'cargo' },
		{ titulo: 'Documento', campo: 'documento_identidad' },
		{ titulo: 'Teléfono', campo: 'telefono' },
		{ titulo: 'Correo', campo: 'email' }
	];

	const campos = [
		{ nombre: 'nombres', etiqueta: 'Nombres', tipo: 'texto', requerido: true },
		{ nombre: 'apellidos', etiqueta: 'Apellidos', tipo: 'texto', requerido: true },
		{ nombre: 'documento_identidad', etiqueta: 'Documento de identidad', tipo: 'texto', requerido: true, maximo: 20 },
		{
			nombre: 'cargo', etiqueta: 'Cargo', tipo: 'select', requerido: true,
			opciones: ['Docente', 'Director de grupo', 'Coordinador', 'Rector', 'Orientador', 'Secretaria'].map((c) => ({ valor: c, etiqueta: c }))
		},
		{ nombre: 'telefono', etiqueta: 'Teléfono', tipo: 'telefono', requerido: true },
		{ nombre: 'email', etiqueta: 'Correo electrónico', tipo: 'email', requerido: true },
		{ nombre: 'direccion', etiqueta: 'Dirección', tipo: 'texto', ancho: 'col-12' }
	];

	const aDatos = (v) => ({
		nombres: v.nombres?.trim(),
		apellidos: v.apellidos?.trim(),
		documento_identidad: v.documento_identidad?.trim(),
		cargo: v.cargo,
		telefono: v.telefono?.trim(),
		email: v.email?.trim(),
		direccion: v.direccion?.trim() || null,
		esta_activo: true
	});
</script>

<svelte:head><title>Docentes | Aula Presente</title></svelte:head>

<PaginaCrud
	titulo="Docentes y personal"
	descripcion="Personal de la institución que dicta clases o atiende a los acudientes."
	icono="bi-person-badge"
	recurso="docente"
	{columnas}
	{campos}
	cargar={async () => soloActivos(await listarDocentes())}
	valoresIniciales={() => ({ nombres: '', apellidos: '', documento_identidad: '', cargo: 'Docente', telefono: '', email: '', direccion: '' })}
	crear={(v) => crearDocente(aDatos(v))}
	actualizar={(f, v) => actualizarDocente(f, aDatos(v))}
	eliminar={eliminarDocente}
	describir={(f) => `a ${nombreCompleto(f)}`}
	puedeCrear={permisos.crear}
	puedeEditar={permisos.actualizar}
	puedeEliminar={permisos.eliminar}
/>
