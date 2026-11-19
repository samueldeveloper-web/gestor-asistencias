<script>
	import PaginaCrud from '$lib/components/PaginaCrud.svelte';
	import { crearUsuario, actualizarUsuario, eliminarUsuario } from '$lib/api/usuariosApi.js';
	import { cargarCatalogos } from '$lib/catalogos.js';
	import { permisosDe } from '$lib/sesion.js';
	import { nombreCompleto, soloActivos, opciones, formatearFechaHora, escaparHtml } from '$lib/utilidades.js';

	const permisos = permisosDe('/usuarios');
	let cat = $state({ roles: [], docentes: [], acudientes: [], estudiantes: [] });

	const sinTildes = (t) => String(t ?? '').normalize('NFD').replace(/[̀-ͯ]/g, '').toLowerCase();
	const nombreRol = (rolid) => cat.roles.find((r) => r.rolid === rolid)?.nombre ?? '';

	/** Según el rol, el usuario se vincula a un docente, un acudiente o un estudiante (tabla usuario). */
	function tipoPerfil(rolid) {
		const n = sinTildes(nombreRol(rolid));
		if (n.startsWith('acudiente')) return 'acudienteid';
		if (n.startsWith('estudiante')) return 'estudianteid';
		return 'personal_institucionalid';
	}

	function perfilDe(u) {
		if (u.acudienteid) return `Acudiente: ${nombreCompleto(cat.acudientes.find((a) => a.acudiente_id === u.acudienteid))}`;
		if (u.estudianteid) return `Estudiante: ${nombreCompleto(cat.estudiantes.find((e) => e.estudiante_id === u.estudianteid))}`;
		if (u.personal_institucionalid) return `Personal: ${nombreCompleto(cat.docentes.find((d) => d.personalid === u.personal_institucionalid))}`;
		return 'Sin vincular';
	}

	const columnas = [
		{ titulo: 'Usuario', campo: 'username', render: (v) => `<strong>${escaparHtml(v)}</strong>` },
		{ titulo: 'Correo', campo: 'email' },
		{ titulo: 'Rol', campo: 'rol' },
		{ titulo: 'Persona vinculada', campo: 'perfil' },
		{ titulo: 'Último ingreso', campo: 'ultimo_ingreso', render: (v, _f, t) => (t === 'display' ? formatearFechaHora(v) || 'Nunca' : v) }
	];

	function campos(modo, _fila, valores) {
		const tipo = tipoPerfil(valores?.rolid);
		const perfiles = {
			personal_institucionalid: { etiqueta: 'Docente o funcionario', opciones: opciones(soloActivos(cat.docentes), 'personalid', nombreCompleto) },
			acudienteid: { etiqueta: 'Acudiente', opciones: opciones(soloActivos(cat.acudientes), 'acudiente_id', nombreCompleto) },
			estudianteid: { etiqueta: 'Estudiante', opciones: opciones(soloActivos(cat.estudiantes), 'estudiante_id', nombreCompleto) }
		};
		return [
			{ nombre: 'username', etiqueta: 'Nombre de usuario', tipo: 'texto', requerido: true, maximo: 50 },
			{ nombre: 'email', etiqueta: 'Correo', tipo: 'email', requerido: true },
			{ nombre: 'password', etiqueta: modo === 'crear' ? 'Contraseña' : 'Nueva contraseña', tipo: 'clave', requerido: modo === 'crear', minimo: 6, ayuda: modo === 'crear' ? 'Mínimo 6 caracteres.' : 'Déjala vacía para conservar la actual.' },
			{ nombre: 'rolid', etiqueta: 'Rol', tipo: 'select', requerido: true, opciones: opciones(soloActivos(cat.roles), 'rolid', 'nombre') },
			{ nombre: 'perfil', etiqueta: perfiles[tipo].etiqueta, tipo: 'select', requerido: true, ancho: 'col-12', opciones: perfiles[tipo].opciones, ayuda: 'Persona a la que pertenece esta cuenta.' }
		];
	}

	async function cargar() {
		const c = await cargarCatalogos(['usuarios', 'roles', 'docentes', 'acudientes', 'estudiantes']);
		cat = c;
		return soloActivos(c.usuarios).map((u) => ({ ...u, rol: nombreRol(u.rolid), perfil: perfilDe(u) }));
	}

	function aDatos(v) {
		const tipo = tipoPerfil(v.rolid);
		const datos = {
			username: v.username?.trim(),
			email: v.email?.trim(),
			rolid: v.rolid,
			personal_institucionalid: tipo === 'personal_institucionalid' ? v.perfil : null,
			acudienteid: tipo === 'acudienteid' ? v.perfil : null,
			estudianteid: tipo === 'estudianteid' ? v.perfil : null,
			esta_activo: true
		};
		if (v.password) datos.password = v.password;
		return datos;
	}
</script>

<svelte:head><title>Usuarios | Aula Presente</title></svelte:head>

<PaginaCrud
	titulo="Usuarios"
	descripcion="Cuentas de acceso. Cada cuenta tiene un rol y pertenece a un docente, acudiente o estudiante."
	icono="bi-person-lock"
	recurso="usuario"
	{columnas}
	{campos}
	{cargar}
	valoresIniciales={() => ({ username: '', email: '', password: '', rolid: null, perfil: null })}
	aFormulario={(f) => ({ username: f.username, email: f.email, password: '', rolid: f.rolid, perfil: f.personal_institucionalid ?? f.acudienteid ?? f.estudianteid ?? null })}
	crear={(v) => crearUsuario(aDatos(v))}
	actualizar={(f, v) => actualizarUsuario(f, aDatos(v))}
	eliminar={eliminarUsuario}
	describir={(f) => `la cuenta ${f.username}`}
	puedeCrear={permisos.crear}
	puedeEditar={permisos.actualizar}
	puedeEliminar={permisos.eliminar}
/>
