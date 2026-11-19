<script>
	import PaginaCrud from '$lib/components/PaginaCrud.svelte';
	import { crearEstudiante, actualizarEstudiante, eliminarEstudiante } from '$lib/api/estudiantesApi.js';
	import { cargarCatalogos, matriculaVigente, estudiantesPermitidos } from '$lib/catalogos.js';
	import { permisosDe } from '$lib/sesion.js';
	import { nombreCompleto, formatearFecha, soloActivos, escaparHtml } from '$lib/utilidades.js';

	const permisos = permisosDe('/estudiantes');

	const columnas = [
		{ titulo: 'Estudiante', render: (_v, f) => `<strong>${escaparHtml(nombreCompleto(f))}</strong>` },
		{ titulo: 'Documento', campo: 'documento_identidad' },
		{ titulo: 'Nacimiento', campo: 'fecha_nacimiento', render: (v, _f, tipo) => (tipo === 'display' ? formatearFecha(v) : v) },
		{ titulo: 'Curso actual', campo: 'curso' },
		{ titulo: 'Acudiente principal', campo: 'acudiente' }
	];

	const campos = [
		{ nombre: 'nombres', etiqueta: 'Nombres', tipo: 'texto', requerido: true, maximo: 100 },
		{ nombre: 'apellidos', etiqueta: 'Apellidos', tipo: 'texto', requerido: true, maximo: 100 },
		{ nombre: 'documento_identidad', etiqueta: 'Documento de identidad', tipo: 'texto', requerido: true, maximo: 20, patron: '[0-9A-Za-z\\-]+' },
		{ nombre: 'fecha_nacimiento', etiqueta: 'Fecha de nacimiento', tipo: 'fecha', requerido: true },
		{ nombre: 'direccion', etiqueta: 'Dirección', tipo: 'texto', ancho: 'col-12' }
	];

	async function cargar() {
		const c = await cargarCatalogos(['estudiantes', 'matriculas', 'cursos', 'vinculos', 'acudientes', 'cargas']);
		const vigente = matriculaVigente(c.matriculas);
		const permitidos = estudiantesPermitidos(c);
		return soloActivos(c.estudiantes)
			.filter((e) => !permitidos || permitidos.has(e.estudiante_id))
			.map((e) => {
				const m = vigente.get(e.estudiante_id);
				const principal = c.vinculos.find((v) => v.estudianteid === e.estudiante_id && v.contacto_principal && (v.esta_activo ?? true));
				return {
					...e,
					curso: c.cursos.find((cu) => cu.cursoid === m?.cursoid)?.nombre_curso ?? 'Sin matrícula',
					acudiente: principal ? nombreCompleto(c.acudientes.find((a) => a.acudiente_id === principal.acudienteid)) : 'Sin acudiente'
				};
			});
	}

	const aDatos = (v) => ({
		nombres: v.nombres?.trim(),
		apellidos: v.apellidos?.trim(),
		documento_identidad: v.documento_identidad?.trim(),
		fecha_nacimiento: v.fecha_nacimiento,
		direccion: v.direccion?.trim() || null,
		esta_activo: true
	});
</script>

<svelte:head><title>Estudiantes | Aula Presente</title></svelte:head>

<PaginaCrud
	titulo="Estudiantes"
	descripcion="Registro de estudiantes de la institución."
	icono="bi-mortarboard"
	recurso="estudiante"
	{columnas}
	{campos}
	{cargar}
	valoresIniciales={() => ({ nombres: '', apellidos: '', documento_identidad: '', fecha_nacimiento: '', direccion: '' })}
	aFormulario={(f) => ({ ...f, fecha_nacimiento: f.fecha_nacimiento?.slice(0, 10) })}
	crear={(v) => crearEstudiante(aDatos(v))}
	actualizar={(f, v) => actualizarEstudiante(f, aDatos(v))}
	eliminar={eliminarEstudiante}
	describir={(f) => `al estudiante ${nombreCompleto(f)}`}
	puedeCrear={permisos.crear}
	puedeEditar={permisos.actualizar}
	puedeEliminar={permisos.eliminar}
/>
