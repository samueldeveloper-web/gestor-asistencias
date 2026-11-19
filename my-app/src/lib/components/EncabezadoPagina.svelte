<script>
	/** Título de cada página con descripción y zona de botones a la derecha. */
	let { titulo, descripcion = '', icono = '', seccion = '', children } = $props();
</script>

<div class="encabezado-pagina d-flex flex-wrap justify-content-between align-items-end gap-3 mb-4">
	<div>
		{#if seccion}<p class="text-uppercase small fw-semibold text-primary mb-1">{seccion}</p>{/if}
		<h1 class="h3 fw-bold mb-1">
			{#if icono}<i class="bi {icono} me-2 text-primary"></i>{/if}{titulo}
		</h1>
		{#if descripcion}<p class="text-secondary mb-0">{descripcion}</p>{/if}
	</div>
	{#if children}
		<div class="d-flex flex-wrap gap-2">{@render children()}</div>
	{/if}
</div>
