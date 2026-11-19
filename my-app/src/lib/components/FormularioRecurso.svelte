<script>
	import CampoFormulario from './CampoFormulario.svelte';
	/** Formulario genérico para crear y editar cualquier recurso. */
	let { campos = [], valores = $bindable({}), ocupado = false, textoBoton = 'Guardar', alEnviar, alCancelar = null } = $props();

	function enviar(evento) {
		evento.preventDefault();
		alEnviar?.(valores);
	}
</script>

<form onsubmit={enviar} novalidate={false}>
	<div class="row g-3">
		{#each campos as campo (campo.nombre)}
			<div class={campo.ancho ?? 'col-md-6'}>
				<CampoFormulario {campo} bind:valor={valores[campo.nombre]} deshabilitado={campo.deshabilitado} />
			</div>
		{/each}
	</div>
	<div class="d-flex justify-content-end gap-2 mt-4">
		{#if alCancelar}<button type="button" class="btn btn-light" onclick={alCancelar}>Cancelar</button>{/if}
		<button type="submit" class="btn btn-primary" disabled={ocupado}>
			{#if ocupado}<span class="spinner-border spinner-border-sm me-1"></span>{/if}{textoBoton}
		</button>
	</div>
</form>
