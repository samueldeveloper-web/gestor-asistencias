<script>
	/** Mensaje de éxito, error o información. */
	let { mensaje = '', tipo = 'info', alCerrar = null } = $props();
	const iconos = { success: 'bi-check-circle', danger: 'bi-exclamation-triangle', warning: 'bi-exclamation-circle', info: 'bi-info-circle' };
</script>

{#if mensaje}
	<div class="alert alert-{tipo} d-flex align-items-start gap-2 {alCerrar ? 'alert-dismissible' : ''}" role={tipo === 'danger' ? 'alert' : 'status'}>
		<i class="bi {iconos[tipo] ?? 'bi-info-circle'} mt-1"></i>
		<div class="flex-grow-1">{mensaje}</div>
		{#if alCerrar}
			<button type="button" class="btn-close" aria-label="Cerrar" onclick={alCerrar}></button>
		{/if}
	</div>
{/if}
