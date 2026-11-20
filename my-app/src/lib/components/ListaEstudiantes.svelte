<script>
	/**
	 * Lista editable de estudiantes a cargo dentro de un formulario.
	 * valor: [{ estudianteid, parentesco, contacto_principal }]
	 * opciones: [{ valor, etiqueta }] con los estudiantes disponibles (por nombre, nunca por ID).
	 */
	let { valor = $bindable([]), opciones = [], parentescos = [], deshabilitado = false } = $props();

	let elegido = $state(null);

	const disponibles = $derived(opciones.filter((o) => !(valor ?? []).some((f) => f.estudianteid === o.valor)));
	const nombre = (id) => opciones.find((o) => o.valor === id)?.etiqueta ?? 'Estudiante';

	function agregar() {
		if (!elegido) return;
		valor = [...(valor ?? []), { estudianteid: elegido, parentesco: parentescos[0] ?? '', contacto_principal: true }];
		elegido = null;
	}

	function quitar(indice) {
		valor = valor.filter((_f, i) => i !== indice);
	}
</script>

<div class="border rounded-3 p-3 bg-light-subtle">
	{#if (valor ?? []).length === 0}
		<p class="small text-secondary mb-2">Aún no tiene estudiantes a cargo.</p>
	{:else}
		<ul class="list-group mb-3">
			{#each valor as fila, i (fila.estudianteid)}
				<li class="list-group-item d-flex flex-wrap align-items-center gap-2">
					<span class="fw-semibold flex-grow-1"><i class="bi bi-person me-1 text-primary"></i>{nombre(fila.estudianteid)}</span>
					<select class="form-select form-select-sm w-auto" aria-label="Parentesco con {nombre(fila.estudianteid)}" bind:value={fila.parentesco} disabled={deshabilitado} required>
						{#each parentescos as p (p)}<option value={p}>{p}</option>{/each}
					</select>
					<div class="form-check form-switch mb-0">
						<input class="form-check-input" type="checkbox" role="switch" id="principal-{fila.estudianteid}" bind:checked={fila.contacto_principal} disabled={deshabilitado} />
						<label class="form-check-label small" for="principal-{fila.estudianteid}">Contacto principal</label>
					</div>
					<button type="button" class="btn btn-sm btn-outline-danger" title="Quitar" onclick={() => quitar(i)} disabled={deshabilitado}>
						<i class="bi bi-x-lg"></i>
					</button>
				</li>
			{/each}
		</ul>
	{/if}
	<div class="input-group">
		<select class="form-select" aria-label="Estudiante para agregar" bind:value={elegido} disabled={deshabilitado || disponibles.length === 0}>
			<option value={null}>{disponibles.length ? 'Selecciona un estudiante' : 'No hay más estudiantes'}</option>
			{#each disponibles as o (o.valor)}<option value={o.valor}>{o.etiqueta}</option>{/each}
		</select>
		<button type="button" class="btn btn-outline-primary" onclick={agregar} disabled={!elegido}>
			<i class="bi bi-plus-lg me-1"></i>Agregar
		</button>
	</div>
</div>
