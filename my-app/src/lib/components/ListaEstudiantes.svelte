<script>
	/**
	 * Lista editable de estudiantes a cargo dentro de un formulario.
	 * valor: [{ estudianteid, parentesco, contacto_principal }]
	 * opciones: [{ valor, etiqueta }] con los estudiantes disponibles (por nombre, nunca por ID).
	 */
	let { valor = $bindable([]), opciones = [], parentescos = [], deshabilitado = false, tienePrincipal = () => false } = $props();

	const disponibles = $derived(opciones.filter((o) => !(valor ?? []).some((f) => f.estudianteid === o.valor)));
	const nombre = (id) => opciones.find((o) => o.valor === id)?.etiqueta ?? 'Estudiante';

	function elegirYAgregar(evento) {
		const select = evento.currentTarget;
		const elegido = disponibles.find((o) => String(o.valor) === select.value)?.valor;
		select.value = '';
		if (elegido == null) return;
		valor = [...(valor ?? []), { estudianteid: elegido, parentesco: parentescos[0] ?? '', contacto_principal: !tienePrincipal(elegido) }];
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
						{#if fila.parentesco && !parentescos.includes(fila.parentesco)}<option value={fila.parentesco}>{fila.parentesco}</option>{/if}
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
	<!-- Al elegir un estudiante se agrega de inmediato a la lista (no hace falta otro botón). -->
	<select class="form-select" aria-label="Estudiante para agregar" disabled={deshabilitado || disponibles.length === 0} onchange={elegirYAgregar}>
		<option value="" selected>{disponibles.length ? '+ Agregar estudiante a cargo…' : 'No hay más estudiantes'}</option>
		{#each disponibles as o (o.valor)}<option value={String(o.valor)}>{o.etiqueta}</option>{/each}
	</select>
</div>
