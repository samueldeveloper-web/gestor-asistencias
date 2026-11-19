<script>
	let { mensaje = 'Cargando…' } = $props();
</script>

<div class="d-flex align-items-center justify-content-center gap-2 text-secondary py-4" role="status" aria-live="polite">
	<span class="spinner-border spinner-border-sm text-primary" aria-hidden="true"></span>
	<span>{mensaje}</span>
</div>
