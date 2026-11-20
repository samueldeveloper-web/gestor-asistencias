<script>
	import ListaEstudiantes from './ListaEstudiantes.svelte';
	/**
	 * Un campo de formulario. Tipos: texto, email, clave, numero, fecha, hora, select, textarea, casilla.
	 * Los select reciben opciones [{ valor, etiqueta }] para que el usuario nunca escriba IDs.
	 */
	let { campo, valor = $bindable(), deshabilitado = false } = $props();
	const id = `campo-${campo.nombre}-${Math.random().toString(36).slice(2, 7)}`;
	const tiposHtml = { texto: 'text', email: 'email', clave: 'password', numero: 'number', fecha: 'date', hora: 'time', telefono: 'tel' };
</script>

{#if campo.tipo === 'casilla'}
	<div class="form-check form-switch mt-2">
		<input {id} class="form-check-input" type="checkbox" role="switch" bind:checked={valor} disabled={deshabilitado} />
		<label class="form-check-label" for={id}>{campo.etiqueta}</label>
	</div>
{:else}
	<label class="form-label fw-semibold small" for={id}>
		{campo.etiqueta}{#if campo.requerido}<span class="text-danger"> *</span>{/if}
	</label>
	{#if campo.tipo === 'estudiantes'}
		<ListaEstudiantes bind:valor opciones={campo.opciones ?? []} parentescos={campo.parentescos ?? []} tienePrincipal={campo.tienePrincipal} {deshabilitado} />
	{:else if campo.tipo === 'select'}
		<select {id} class="form-select" bind:value={valor} required={campo.requerido} disabled={deshabilitado}>
			<option value={null} disabled={campo.requerido}>{campo.marcador ?? 'Selecciona una opción'}</option>
			{#each campo.opciones ?? [] as opcion (opcion.valor)}
				<option value={opcion.valor}>{opcion.etiqueta}</option>
			{/each}
		</select>
	{:else if campo.tipo === 'textarea'}
		<textarea {id} class="form-control" rows="3" bind:value={valor} required={campo.requerido} disabled={deshabilitado} placeholder={campo.marcador ?? ''} maxlength={campo.maximo}></textarea>
	{:else if campo.tipo === 'numero'}
		<input {id} class="form-control" type="number" bind:value={valor} required={campo.requerido} disabled={deshabilitado} min={campo.min} max={campo.max} step={campo.paso ?? 1} />
	{:else}
		<input {id} class="form-control" type={tiposHtml[campo.tipo] ?? 'text'} bind:value={valor} required={campo.requerido} disabled={deshabilitado} placeholder={campo.marcador ?? ''} maxlength={campo.maximo} minlength={campo.minimo} pattern={campo.patron} autocomplete={campo.tipo === 'clave' ? 'new-password' : 'off'} />
	{/if}
{/if}
{#if campo.ayuda}<div class="form-text">{campo.ayuda}</div>{/if}
