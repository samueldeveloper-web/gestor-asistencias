<script>
	import { tonoDe, capitalizar } from '$lib/utilidades.js';
	/** Insignia de color según el estado (presente, ausente, pendiente, activo…). */
	let { texto = '', tono = '' } = $props();
</script>

<span class="badge rounded-pill text-bg-{tono || tonoDe(texto)}">{capitalizar(texto)}</span>
