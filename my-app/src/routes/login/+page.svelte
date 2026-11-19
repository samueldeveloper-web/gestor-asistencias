<script>
	import { onMount } from 'svelte';
	import { goto } from '$app/navigation';
	import { page } from '$app/state';
	import Alerta from '$lib/components/Alerta.svelte';
	import CampoFormulario from '$lib/components/CampoFormulario.svelte';
	import { iniciarSesion, listarRolesLogin } from '$lib/api/authApi.js';
	import { guardarSesion, haySesion, obtenerModulos } from '$lib/sesion.js';
	import { opciones, soloActivos } from '$lib/utilidades.js';

	let roles = $state([]);
	let valores = $state({ identifier: '', password: '', rolid: null });
	let error = $state('');
	let ocupado = $state(false);

	const campos = $derived([
		{ nombre: 'rolid', etiqueta: 'Rol', tipo: 'select', requerido: true, marcador: 'Selecciona tu rol', opciones: opciones(roles, 'rolid', 'nombre') },
		{ nombre: 'identifier', etiqueta: 'Correo o usuario', tipo: 'texto', requerido: true, marcador: 'correo@colegio.edu.co' },
		{ nombre: 'password', etiqueta: 'Contraseña', tipo: 'clave', requerido: true, marcador: '••••••••' }
	]);

	onMount(async () => {
		if (haySesion() && obtenerModulos().length) {
			goto(obtenerModulos()[0].ruta, { replaceState: true });
			return;
		}
		if (page.url.searchParams.get('expirada')) error = 'Tu sesión expiró. Vuelve a iniciar sesión.';
		try {
			roles = soloActivos(await listarRolesLogin());
		} catch (e) {
			error = e.message;
		}
	});

	async function ingresar(evento) {
		evento.preventDefault();
		error = '';
		if (!valores.rolid) {
			error = 'Selecciona el rol con el que vas a ingresar.';
			return;
		}
		ocupado = true;
		try {
			const sesion = await iniciarSesion(valores.identifier.trim(), valores.password, valores.rolid);
			if (!sesion.modulos.length) throw new Error('Tu rol no tiene módulos asignados en la base de datos.');
			guardarSesion(sesion);
			goto(sesion.modulos[0].ruta, { replaceState: true });
		} catch (e) {
			error = e.estado === 401 ? 'Usuario, contraseña o rol incorrectos.' : e.message;
		} finally {
			ocupado = false;
		}
	}
</script>

<svelte:head><title>Iniciar sesión | Aula Presente</title></svelte:head>

<div class="row justify-content-center py-4">
	<div class="col-sm-10 col-md-7 col-lg-5 col-xl-4">
		<div class="card border-0 p-2">
			<div class="card-body p-4">
				<div class="text-center mb-4">
					<span class="d-inline-grid rounded-4 bg-primary text-white fs-3 mb-3" style="width:56px;height:56px;place-items:center"><i class="bi bi-calendar-check"></i></span>
					<h1 class="h4 fw-bold mb-1">Iniciar sesión</h1>
					<p class="text-secondary small mb-0">Ingresa con tu rol para ver tus módulos.</p>
				</div>
				<Alerta mensaje={error} tipo="danger" />
				<form onsubmit={ingresar}>
					{#each campos as campo (campo.nombre)}
						<div class="mb-3">
							<CampoFormulario {campo} bind:valor={valores[campo.nombre]} />
						</div>
					{/each}
					<button type="submit" class="btn btn-primary w-100 py-2" disabled={ocupado}>
						{#if ocupado}<span class="spinner-border spinner-border-sm me-1"></span>Validando…{:else}<i class="bi bi-box-arrow-in-right me-1"></i>Ingresar{/if}
					</button>
				</form>
			</div>
		</div>
	</div>
</div>
