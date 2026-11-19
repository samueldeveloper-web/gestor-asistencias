<script>
	/** Tarjeta con un número clave (KPI) para el tablero de inicio. */
	let { titulo, valor = 0, icono = 'bi-bar-chart', color = 'primary', detalle = '', enlace = '' } = $props();
</script>

<div class="card tarjeta-indicador h-100 border-0">
	<div class="card-body d-flex align-items-center gap-3">
		<span class="icono-indicador bg-{color}-subtle text-{color}"><i class="bi {icono}"></i></span>
		<div class="flex-grow-1">
			<p class="text-secondary small mb-1">{titulo}</p>
			<p class="h4 fw-bold mb-0">{valor}</p>
			{#if detalle}<p class="small text-secondary mb-0">{detalle}</p>{/if}
		</div>
		{#if enlace}<a href={enlace} class="stretched-link" aria-label="Ver {titulo}"></a>{/if}
	</div>
</div>

<style>
	.icono-indicador {
		width: 48px;
		height: 48px;
		border-radius: 14px;
		display: grid;
		place-items: center;
		font-size: 1.35rem;
	}
</style>
