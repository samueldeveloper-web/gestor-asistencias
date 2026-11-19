<script>
	import PaginaCrud from '$lib/components/PaginaCrud.svelte';
	import { crearRol, actualizarRol, eliminarRol } from '$lib/api/rolesApi.js';
	import { crearModulo, actualizarModulo, eliminarModulo } from '$lib/api/modulosApi.js';
	import { listarModulosRol, crearModuloRol, actualizarModuloRol, eliminarModuloRol } from '$lib/api/moduloRolApi.js';
	import { cargarCatalogos } from '$lib/catalogos.js';
	import { permisosDe } from '$lib/sesion.js';
	import { soloActivos, opciones, escaparHtml } from '$lib/utilidades.js';

	const permisos = permisosDe('/roles-modulos');
	let cat = $state({ roles: [], modulos: [] });
	let recargarPermisos = $state();

	const marca = (v, _f, t) => (t === 'display' ? (v ? '<i class="bi bi-check-circle-fill text-success"></i>' : '<i class="bi bi-dash-circle text-secondary"></i>') : v ? 1 : 0);

	// ----- Permisos (modulo_por_rol) -----
	const columnasPermisos = [
		{ titulo: 'Rol', campo: 'rol', render: (v) => `<strong>${escaparHtml(v)}</strong>` },
		{ titulo: 'Módulo', campo: 'modulo', render: (v, f) => `<i class="bi ${escaparHtml(f.icono || 'bi-grid')} me-1"></i>${escaparHtml(v)}` },
		{ titulo: 'Ruta', campo: 'ruta' },
		{ titulo: 'Crear', campo: 'permiso_crear', render: marca, clase: 'text-center' },
		{ titulo: 'Leer', campo: 'permiso_leer', render: marca, clase: 'text-center' },
		{ titulo: 'Actualizar', campo: 'permiso_actualizar', render: marca, clase: 'text-center' },
		{ titulo: 'Eliminar', campo: 'permiso_eliminar', render: marca, clase: 'text-center' }
	];
	const camposPermisos = () => [
		{ nombre: 'rolid', etiqueta: 'Rol', tipo: 'select', requerido: true, opciones: opciones(soloActivos(cat.roles), 'rolid', 'nombre') },
		{ nombre: 'moduloid', etiqueta: 'Módulo', tipo: 'select', requerido: true, opciones: opciones(soloActivos(cat.modulos), 'moduloid', (m) => `${m.nombre} (${m.ruta})`) },
		{ nombre: 'permiso_leer', etiqueta: 'Puede ver el módulo', tipo: 'casilla', ancho: 'col-sm-6' },
		{ nombre: 'permiso_crear', etiqueta: 'Puede crear', tipo: 'casilla', ancho: 'col-sm-6' },
		{ nombre: 'permiso_actualizar', etiqueta: 'Puede actualizar', tipo: 'casilla', ancho: 'col-sm-6' },
		{ nombre: 'permiso_eliminar', etiqueta: 'Puede eliminar', tipo: 'casilla', ancho: 'col-sm-6' }
	];
	async function cargarPermisos() {
		const [c, filas] = await Promise.all([cargarCatalogos(['roles', 'modulos']), listarModulosRol()]);
		cat = c;
		return soloActivos(filas).map((p) => {
			const m = c.modulos.find((x) => x.moduloid === p.moduloid);
			return { ...p, rol: c.roles.find((r) => r.rolid === p.rolid)?.nombre ?? '', modulo: m?.nombre ?? '', ruta: m?.ruta ?? '', icono: m?.icono };
		});
	}
	const datosPermiso = (v) => ({
		rolid: v.rolid, moduloid: v.moduloid,
		permiso_crear: !!v.permiso_crear, permiso_leer: !!v.permiso_leer,
		permiso_actualizar: !!v.permiso_actualizar, permiso_eliminar: !!v.permiso_eliminar,
		esta_activo: true
	});

	// ----- Roles -----
	const columnasRoles = [
		{ titulo: 'Rol', campo: 'nombre', render: (v) => `<strong>${escaparHtml(v)}</strong>` },
		{ titulo: 'Descripción', campo: 'descripcion' }
	];
	const camposRoles = [
		{ nombre: 'nombre', etiqueta: 'Nombre del rol', tipo: 'texto', requerido: true, ancho: 'col-12' },
		{ nombre: 'descripcion', etiqueta: 'Descripción', tipo: 'textarea', ancho: 'col-12' }
	];
	const datosRol = (v) => ({ nombre: v.nombre?.trim(), descripcion: v.descripcion?.trim() || null, esta_activo: true });

	// ----- Módulos -----
	const columnasModulos = [
		{ titulo: 'Módulo', campo: 'nombre', render: (v, f) => `<i class="bi ${escaparHtml(f.icono || 'bi-grid')} me-1 text-primary"></i><strong>${escaparHtml(v)}</strong>` },
		{ titulo: 'Ruta', campo: 'ruta' },
		{ titulo: 'Descripción', campo: 'descripcion' }
	];
	const camposModulos = [
		{ nombre: 'nombre', etiqueta: 'Nombre visible en el menú', tipo: 'texto', requerido: true },
		{ nombre: 'ruta', etiqueta: 'Ruta', tipo: 'texto', requerido: true, marcador: '/asistencia', patron: '/[a-z0-9\\-]+' },
		{ nombre: 'icono', etiqueta: 'Icono (Bootstrap Icons)', tipo: 'texto', marcador: 'bi-calendar-check' },
		{ nombre: 'descripcion', etiqueta: 'Descripción', tipo: 'texto' }
	];
	const datosModulo = (v) => ({ nombre: v.nombre?.trim(), ruta: v.ruta?.trim(), icono: v.icono?.trim() || null, descripcion: v.descripcion?.trim() || null, esta_activo: true });

	const actualizarTodo = () => recargarPermisos?.();
</script>

<svelte:head><title>Roles y módulos | Aula Presente</title></svelte:head>

<PaginaCrud
	titulo="Permisos por rol"
	descripcion="Define qué módulos ve cada rol en el menú (tabla modulo_por_rol). Los cambios aplican al volver a iniciar sesión."
	icono="bi-shield-lock"
	recurso="permiso"
	bind:recargar={recargarPermisos}
	columnas={columnasPermisos}
	campos={camposPermisos}
	cargar={cargarPermisos}
	valoresIniciales={() => ({ rolid: null, moduloid: null, permiso_leer: true, permiso_crear: false, permiso_actualizar: false, permiso_eliminar: false })}
	crear={(v) => crearModuloRol(datosPermiso(v))}
	actualizar={(f, v) => actualizarModuloRol(f, datosPermiso(v))}
	eliminar={eliminarModuloRol}
	describir={(f) => `el permiso de ${f.rol} sobre ${f.modulo}`}
	puedeCrear={permisos.crear}
	puedeEditar={permisos.actualizar}
	puedeEliminar={permisos.eliminar}
/>

<div class="row g-4 mt-2">
	<div class="col-xl-5">
		<PaginaCrud
			titulo="Roles"
			icono="bi-person-gear"
			recurso="rol"
			columnas={columnasRoles}
			campos={camposRoles}
			cargar={async () => soloActivos(cat.roles.length ? cat.roles : (await cargarCatalogos(['roles'])).roles)}
			valoresIniciales={() => ({ nombre: '', descripcion: '' })}
			crear={async (v) => { await crearRol(datosRol(v)); actualizarTodo(); }}
			actualizar={async (f, v) => { await actualizarRol(f, datosRol(v)); actualizarTodo(); }}
			eliminar={async (f) => { await eliminarRol(f); actualizarTodo(); }}
			describir={(f) => `el rol ${f.nombre}`}
			puedeCrear={permisos.crear}
			puedeEditar={permisos.actualizar}
			puedeEliminar={permisos.eliminar}
		/>
	</div>
	<div class="col-xl-7">
		<PaginaCrud
			titulo="Módulos"
			icono="bi-grid"
			recurso="módulo"
			columnas={columnasModulos}
			campos={camposModulos}
			cargar={async () => soloActivos((await cargarCatalogos(['modulos'])).modulos)}
			valoresIniciales={() => ({ nombre: '', ruta: '/', icono: '', descripcion: '' })}
			crear={async (v) => { await crearModulo(datosModulo(v)); actualizarTodo(); }}
			actualizar={async (f, v) => { await actualizarModulo(f, datosModulo(v)); actualizarTodo(); }}
			eliminar={async (f) => { await eliminarModulo(f); actualizarTodo(); }}
			describir={(f) => `el módulo ${f.nombre}`}
			puedeCrear={permisos.crear}
			puedeEditar={permisos.actualizar}
			puedeEliminar={permisos.eliminar}
		/>
	</div>
</div>
