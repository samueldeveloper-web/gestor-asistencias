<script>
	/** Ventana modal de Bootstrap controlada por Svelte (sin depender de bootstrap.js). */
	let { abierto = $bindable(false), titulo = '', tamano = '', children, pie } = $props();

	function cerrar() {
		abierto = false;
	}

	function teclado(evento) {
		if (abierto && evento.key === 'Escape') cerrar();
	}
</script>

<svelte:window onkeydown={teclado} />

{#if abierto}
	<div class="modal d-block" tabindex="-1" role="dialog" aria-modal="true" aria-label={titulo}>
		<div class="modal-dialog modal-dialog-centered modal-dialog-scrollable {tamano ? `modal-${tamano}` : ''}">
			<div class="modal-content">
				<div class="modal-header">
					<h2 class="modal-title h5 fw-bold">{titulo}</h2>
					<button type="button" class="btn-close" aria-label="Cerrar" onclick={cerrar}></button>
				</div>
				<div class="modal-body">{@render children?.()}</div>
				{#if pie}<div class="modal-footer">{@render pie()}</div>{/if}
			</div>
		</div>
	</div>
	<!-- svelte-ignore a11y_click_events_have_key_events, a11y_no_static_element_interactions -->
	<div class="modal-backdrop fade show" onclick={cerrar}></div>
{/if}
