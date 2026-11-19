<script>
	/**
	 * Tabla con la librería DataTables (búsqueda, orden, paginación y exportación responsive).
	 * columnas: [{ titulo, campo, render?(valor, fila) → HTML }]
	 * acciones: [{ titulo, icono, clase?, mostrar?(fila), alHacerClic(fila) }]
	 * Nunca se muestran IDs: solo se renderizan las columnas declaradas.
	 */
	import { onDestroy, onMount } from 'svelte';
	import { escaparHtml } from '$lib/utilidades.js';

	let { columnas = [], filas = [], acciones = [], ordenInicial = [[0, 'asc']], porPagina = 10 } = $props();

	let elemento;
	let tabla = null;
	let columnasActuales = null;
	let listo = $state(false);

	const idioma = {
		decimal: ',',
		emptyTable: 'No hay registros para mostrar',
		info: 'Mostrando _START_ a _END_ de _TOTAL_ registros',
		infoEmpty: 'Mostrando 0 registros',
		infoFiltered: '(filtrado de _MAX_ registros)',
		lengthMenu: 'Mostrar _MENU_ registros',
		loadingRecords: 'Cargando…',
		search: 'Buscar:',
		zeroRecords: 'No se encontraron coincidencias',
		paginate: { first: 'Primero', last: 'Último', next: 'Siguiente', previous: 'Anterior' },
		aria: { orderable: 'Ordenar por esta columna', orderableReverse: 'Invertir orden' }
	};

	function definirColumnas() {
		const definidas = columnas.map((c) => ({
			title: c.titulo,
			data: null,
			className: c.clase ?? 'dt-left',
			orderable: c.ordenable ?? true,
			render: (_dato, tipo, fila) => {
				const valor = c.campo ? fila[c.campo] : undefined;
				if (c.render) return c.render(valor, fila, tipo);
				return escaparHtml(valor ?? '');
			}
		}));
		if (acciones.length) {
			definidas.push({
				title: 'Acciones',
				data: null,
				orderable: false,
				searchable: false,
				className: 'text-end text-nowrap all',
				render: (_dato, _tipo, fila, meta) =>
					acciones
						.map((a, i) =>
							a.mostrar && !a.mostrar(fila)
								? ''
								: `<button type="button" class="btn btn-sm ${a.clase ?? 'btn-outline-primary'} ms-1" data-accion="${i}" data-fila="${meta.row}" title="${escaparHtml(a.titulo)}"><i class="bi ${a.icono}"></i><span class="d-none d-xxl-inline ms-1">${escaparHtml(a.titulo)}</span></button>`
						)
						.join('')
			});
		}
		return definidas;
	}

	function crearTabla(datos) {
		const DataTable = window.DataTable;
		tabla = new DataTable(elemento, {
			data: datos,
			columns: definirColumnas(),
			language: idioma,
			order: ordenInicial,
			pageLength: porPagina,
			lengthMenu: [5, 10, 25, 50, 100],
			responsive: true,
			autoWidth: false
		});
		columnasActuales = columnas;
	}

	function alHacerClic(evento) {
		const boton = evento.target.closest('button[data-accion]');
		if (!boton || !tabla) return;
		const fila = tabla.row(Number(boton.dataset.fila)).data();
		acciones[Number(boton.dataset.accion)]?.alHacerClic?.(fila);
	}

	onMount(() => {
		// Espera a que el script de DataTables (CDN) esté disponible.
		const revisar = setInterval(() => {
			if (window.DataTable) {
				clearInterval(revisar);
				listo = true;
			}
		}, 50);
		return () => clearInterval(revisar);
	});

	$effect(() => {
		const datos = $state.snapshot(filas);
		const cols = columnas;
		if (!listo || !elemento) return;
		if (tabla && cols !== columnasActuales) {
			tabla.destroy();
			elemento.innerHTML = '';
			tabla = null;
		}
		if (!tabla) crearTabla(datos);
		else tabla.clear().rows.add(datos).draw(false);
	});

	onDestroy(() => {
		tabla?.destroy();
		tabla = null;
	});
</script>

<div class="tabla-datos">
	{#if !listo}<p class="text-secondary small mb-2">Preparando tabla…</p>{/if}
	<!-- svelte-ignore a11y_click_events_have_key_events, a11y_no_noninteractive_element_interactions -->
	<table bind:this={elemento} class="table table-hover table-striped align-middle w-100" onclick={alHacerClic}></table>
</div>
