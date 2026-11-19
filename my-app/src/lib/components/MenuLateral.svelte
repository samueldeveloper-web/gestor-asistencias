<script>
	/** Lista de módulos del rol (desde modulo_por_rol). Se usa en la barra lateral y en el menú móvil. */
	import { page } from '$app/state';
	let { modulos = [], alNavegar = () => {} } = $props();
</script>

<nav aria-label="Módulos">
	<ul class="nav nav-pills flex-column gap-1 menu-lateral">
		{#each modulos as modulo (modulo.ruta)}
			<li class="nav-item">
				<a
					class="nav-link d-flex align-items-center gap-2"
					class:active={page.url.pathname === modulo.ruta}
					aria-current={page.url.pathname === modulo.ruta ? 'page' : undefined}
					href={modulo.ruta}
					onclick={alNavegar}
				>
					<i class="bi {modulo.icono || 'bi-grid'}"></i><span>{modulo.nombre}</span>
				</a>
			</li>
		{/each}
	</ul>
</nav>
