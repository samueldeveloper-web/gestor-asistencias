<script>
	import '$lib/estilos.css';
	import favicon from '$lib/assets/favicon.svg';
	import { page } from '$app/state';
	import { goto } from '$app/navigation';
	import Encabezado from '$lib/components/Encabezado.svelte';
	import PiePagina from '$lib/components/PiePagina.svelte';
	import Cargando from '$lib/components/Cargando.svelte';
	import MenuLateral from '$lib/components/MenuLateral.svelte';
	import { haySesion, obtenerModulos, obtenerUsuario } from '$lib/sesion.js';

	let { children } = $props();

	const rutasPublicas = ['/', '/login'];
	let usuario = $state(null);
	let modulos = $state([]);
	let permitido = $state(false);

	// Guardia de rutas: solo se puede entrar a los módulos que el rol tiene en modulo_por_rol.
	$effect(() => {
		const ruta = page.url.pathname;
		const permitidos = obtenerModulos();
		usuario = obtenerUsuario();
		modulos = permitidos;
		if (rutasPublicas.includes(ruta)) {
			permitido = true;
			return;
		}
		permitido = false;
		if (!haySesion()) {
			goto('/login', { replaceState: true });
			return;
		}
		if (!permitidos.some((m) => m.ruta === ruta)) {
			goto(permitidos[0]?.ruta ?? '/login', { replaceState: true });
			return;
		}
		permitido = true;
	});
</script>

<svelte:head>
	<link rel="icon" href={favicon} />
	<title>Aula Presente</title>
</svelte:head>

<div class="app">
	<Encabezado {usuario} {modulos} />
	<div class="d-flex flex-grow-1">
		{#if usuario && modulos.length && !rutasPublicas.includes(page.url.pathname)}
			<aside class="barra-lateral d-none d-lg-block">
				<p class="text-uppercase small fw-semibold text-secondary px-3 mb-2">Módulos</p>
				<MenuLateral {modulos} />
			</aside>
		{/if}
		<main class="app-contenido">
			{#if permitido}
				<div class="container-xl py-4 px-3 px-lg-4">
					{@render children()}
				</div>
			{:else}
				<Cargando mensaje="Verificando permisos…" />
			{/if}
		</main>
	</div>
	<PiePagina />
</div>
