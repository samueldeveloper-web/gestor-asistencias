<script>
	import VentanaModal from './VentanaModal.svelte';
	/** Pide confirmación antes de desactivar un registro (borrado lógico). */
	let { abierto = $bindable(false), descripcion = '', ocupado = false, alConfirmar } = $props();
</script>

<VentanaModal bind:abierto titulo="Confirmar eliminación">
	<p class="mb-2">¿Deseas eliminar <strong>{descripcion}</strong>?</p>
	<p class="small text-secondary mb-0">
		<i class="bi bi-shield-check me-1"></i>El registro no se borra de la base de datos: su estado pasa a inactivo y conserva el historial.
	</p>
	{#snippet pie()}
		<button type="button" class="btn btn-light" onclick={() => (abierto = false)}>Cancelar</button>
		<button type="button" class="btn btn-danger" disabled={ocupado} onclick={alConfirmar}>
			{#if ocupado}<span class="spinner-border spinner-border-sm me-1"></span>{/if}Eliminar
		</button>
	{/snippet}
</VentanaModal>
