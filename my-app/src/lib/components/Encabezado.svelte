<script>
	/** Barra superior: marca, cuenta del usuario y botón del menú en pantallas pequeñas. */
	import { page } from '$app/state';
	import { cerrarSesion } from '$lib/sesion.js';
	import MenuLateral from './MenuLateral.svelte';

	let { usuario = null, modulos = [] } = $props();
	let menuAbierto = $state(false);

	const iniciales = $derived(
		(usuario?.nombre ?? usuario?.username ?? 'U')
			.split(' ')
			.map((p) => p[0])
			.slice(0, 2)
			.join('')
			.toUpperCase()
	);
</script>

<header class="encabezado sticky-top">
	<div class="container-fluid px-3 px-lg-4 d-flex align-items-center justify-content-between gap-2 py-2">
		<a class="navbar-brand d-flex align-items-center gap-2 fw-bold fs-5" href={modulos[0]?.ruta ?? '/'}>
			<span class="marca"><i class="bi bi-calendar-check"></i></span>
			<span>Aula<span class="fw-normal">Presente</span></span>
		</a>
		{#if usuario}
			<div class="d-flex align-items-center gap-2">
				<span class="avatar">{iniciales}</span>
				<span class="lh-sm d-none d-sm-block">
					<strong class="d-block small">{usuario.nombre ?? usuario.username}</strong>
					<small class="text-secondary">{usuario.rol}</small>
				</span>
				<button type="button" class="btn btn-sm btn-outline-secondary ms-2" onclick={cerrarSesion} title="Cerrar sesión">
					<i class="bi bi-box-arrow-right"></i><span class="d-none d-md-inline ms-1">Salir</span>
				</button>
				<button class="btn btn-sm btn-outline-primary d-lg-none" type="button" aria-label="Abrir menú" aria-expanded={menuAbierto} onclick={() => (menuAbierto = !menuAbierto)}>
					<i class="bi bi-list fs-5"></i>
				</button>
			</div>
		{:else if page.url.pathname !== '/login'}
			<a href="/login" class="btn btn-primary btn-sm">Iniciar sesión</a>
		{/if}
	</div>
	{#if usuario && menuAbierto}
		<div class="d-lg-none border-top px-3 py-2 bg-white">
			<MenuLateral {modulos} alNavegar={() => (menuAbierto = false)} />
		</div>
	{/if}
</header>
