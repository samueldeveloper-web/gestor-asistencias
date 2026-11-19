<script>
	/**
	 * Página CRUD reutilizable: encabezado + tabla DataTables + formulario modal + confirmación.
	 * Cada ruta solo define columnas, campos y las funciones de su archivo <recurso>Api.js.
	 */
	import { onMount } from 'svelte';
	import EncabezadoPagina from './EncabezadoPagina.svelte';
	import Alerta from './Alerta.svelte';
	import Cargando from './Cargando.svelte';
	import TablaDatos from './TablaDatos.svelte';
	import VentanaModal from './VentanaModal.svelte';
	import FormularioRecurso from './FormularioRecurso.svelte';
	import ConfirmarEliminacion from './ConfirmarEliminacion.svelte';

	let {
		titulo,
		descripcion = '',
		icono = '',
		recurso = 'registro',
		columnas = [],
		campos = [],
		cargar,
		valoresIniciales = () => ({}),
		aFormulario = (fila) => ({ ...fila }),
		crear = null,
		actualizar = null,
		eliminar = null,
		describir = () => 'este registro',
		puedeCrear = true,
		puedeEditar = true,
		puedeEliminar = true,
		puedeEditarFila = () => true,
		accionesExtra = [],
		ordenInicial = [[0, 'asc']],
		textoCrear = '',
		filas = $bindable([]),
		recargar = $bindable(),
		superior,
		inferior
	} = $props();

	let cargando = $state(true);
	let ocupado = $state(false);
	let error = $state('');
	let exito = $state('');
	let modalAbierto = $state(false);
	let confirmarAbierto = $state(false);
	let filaEditada = $state(null);
	let filaEliminar = $state(null);
	let valores = $state({});

	const camposActuales = $derived(typeof campos === 'function' ? campos(filaEditada ? 'editar' : 'crear', filaEditada, valores) : campos);

	const acciones = $derived([
		...accionesExtra,
		...(puedeEditar && actualizar ? [{ titulo: 'Editar', icono: 'bi-pencil-square', clase: 'btn-outline-primary', mostrar: puedeEditarFila, alHacerClic: abrirEditar }] : []),
		...(puedeEliminar && eliminar ? [{ titulo: 'Eliminar', icono: 'bi-trash', clase: 'btn-outline-danger', mostrar: puedeEditarFila, alHacerClic: abrirEliminar }] : [])
	]);

	async function cargarFilas() {
		cargando = true;
		error = '';
		try {
			filas = await cargar();
		} catch (e) {
			error = e.message ?? 'No se pudo cargar la información.';
		} finally {
			cargando = false;
		}
	}
	recargar = cargarFilas;

	function abrirCrear() {
		filaEditada = null;
		valores = valoresIniciales();
		exito = '';
		modalAbierto = true;
	}

	function abrirEditar(fila) {
		filaEditada = fila;
		valores = aFormulario(fila);
		exito = '';
		modalAbierto = true;
	}

	function abrirEliminar(fila) {
		filaEliminar = fila;
		confirmarAbierto = true;
	}

	async function guardar(datos) {
		ocupado = true;
		error = '';
		try {
			const copia = $state.snapshot(datos);
			if (filaEditada) {
				await actualizar(filaEditada, copia);
				exito = `Se actualizó ${describir(filaEditada)}.`;
			} else {
				await crear(copia);
				exito = `Se registró ${recurso === 'registro' ? 'el registro' : recurso} correctamente.`;
			}
			modalAbierto = false;
			await cargarFilas();
		} catch (e) {
			error = e.message ?? 'No se pudo guardar.';
		} finally {
			ocupado = false;
		}
	}

	async function confirmarEliminar() {
		ocupado = true;
		error = '';
		try {
			await eliminar(filaEliminar);
			exito = `Se eliminó ${describir(filaEliminar)} (estado inactivo).`;
			confirmarAbierto = false;
			await cargarFilas();
		} catch (e) {
			error = e.message ?? 'No se pudo eliminar.';
			confirmarAbierto = false;
		} finally {
			ocupado = false;
		}
	}

	onMount(cargarFilas);
</script>

<EncabezadoPagina {titulo} {descripcion} {icono}>
	<button type="button" class="btn btn-outline-secondary" onclick={cargarFilas} title="Recargar">
		<i class="bi bi-arrow-clockwise"></i>
	</button>
	{#if puedeCrear && crear}
		<button type="button" class="btn btn-primary" onclick={abrirCrear}>
			<i class="bi bi-plus-lg me-1"></i>{textoCrear || `Nuevo ${recurso}`}
		</button>
	{/if}
</EncabezadoPagina>

<Alerta mensaje={error} tipo="danger" alCerrar={() => (error = '')} />
<Alerta mensaje={exito} tipo="success" alCerrar={() => (exito = '')} />

{@render superior?.()}

<div class="card border-0 shadow-sm">
	<div class="card-body">
		{#if cargando && filas.length === 0}
			<Cargando mensaje="Cargando {titulo.toLowerCase()}…" />
		{/if}
		<TablaDatos {columnas} {filas} {acciones} {ordenInicial} />
	</div>
</div>

{@render inferior?.()}

<VentanaModal bind:abierto={modalAbierto} titulo={filaEditada ? `Editar ${recurso}` : `Nuevo ${recurso}`} tamano="lg">
	<Alerta mensaje={modalAbierto ? error : ''} tipo="danger" />
	<FormularioRecurso campos={camposActuales} bind:valores {ocupado} textoBoton={filaEditada ? 'Guardar cambios' : 'Registrar'} alEnviar={guardar} alCancelar={() => (modalAbierto = false)} />
</VentanaModal>

<ConfirmarEliminacion bind:abierto={confirmarAbierto} descripcion={filaEliminar ? describir(filaEliminar) : ''} {ocupado} alConfirmar={confirmarEliminar} />
