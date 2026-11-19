<script>
	/**
	 * Módulo tablero (Corte 3): dashboard de Power BI conectado a Neon, publicado
	 * en la web y embebido con <iframe>. El enlace se guarda en la BD
	 * (configuracion_institucional, clave tablero_powerbi_url) y el administrador lo cambia aquí.
	 */
	import { onMount } from 'svelte';
	import EncabezadoPagina from '$lib/components/EncabezadoPagina.svelte';
	import Alerta from '$lib/components/Alerta.svelte';
	import Cargando from '$lib/components/Cargando.svelte';
	import VentanaModal from '$lib/components/VentanaModal.svelte';
	import CampoFormulario from '$lib/components/CampoFormulario.svelte';
	import { obtenerParametro, guardarParametro } from '$lib/api/configuracionApi.js';
	import { esAdministrador } from '$lib/sesion.js';

	const CLAVE = 'tablero_powerbi_url';
	const admin = esAdministrador();

	let url = $state('');
	let cargando = $state(true);
	let error = $state('');
	let exito = $state('');
	let editorAbierto = $state(false);
	let nuevaUrl = $state('');
	let guardando = $state(false);

	/** Acepta el enlace "Publicar en la web" o el código <iframe> completo que entrega Power BI. */
	function extraerUrl(texto) {
		const limpio = String(texto ?? '').trim();
		const enIframe = /src\s*=\s*"([^"]+)"/i.exec(limpio)?.[1];
		return (enIframe ?? limpio).trim();
	}

	const esValida = (u) => /^https:\/\/app\.powerbi\.com\//i.test(u);

	async function guardar(evento) {
		evento.preventDefault();
		const valor = extraerUrl(nuevaUrl);
		if (!esValida(valor)) {
			error = 'El enlace debe empezar por https://app.powerbi.com/ (Archivo → Insertar informe → Publicar en la web).';
			editorAbierto = false;
			return;
		}
		guardando = true;
		try {
			await guardarParametro(CLAVE, valor);
			url = valor;
			exito = 'Tablero actualizado.';
			error = '';
			editorAbierto = false;
		} catch (e) {
			error = e.message;
		} finally {
			guardando = false;
		}
	}

	onMount(async () => {
		try {
			url = (await obtenerParametro(CLAVE)) || import.meta.env.VITE_POWERBI_URL || '';
		} catch (e) {
			error = e.message;
		} finally {
			cargando = false;
		}
	});
</script>

<EncabezadoPagina titulo="Tablero de indicadores" icono="bi-bar-chart" seccion="Corte 3" descripcion="Indicadores de asistencia, fallas y notificaciones en Power BI.">
	{#if url}
		<a class="btn btn-outline-primary" href={url} target="_blank" rel="noopener"><i class="bi bi-arrows-fullscreen me-1"></i>Pantalla completa</a>
	{/if}
	{#if admin}
		<button class="btn btn-primary" onclick={() => { nuevaUrl = url; editorAbierto = true; }}>
			<i class="bi bi-link-45deg me-1"></i>{url ? 'Cambiar enlace' : 'Configurar tablero'}
		</button>
	{/if}
</EncabezadoPagina>

<Alerta mensaje={error} tipo="danger" alCerrar={() => (error = '')} />
<Alerta mensaje={exito} tipo="success" alCerrar={() => (exito = '')} />

{#if cargando}
	<Cargando mensaje="Cargando tablero…" />
{:else if url}
	<div class="card border-0 overflow-hidden">
		<div class="marco-tablero">
			<iframe title="Tablero de asistencia en Power BI" src={url} allowfullscreen loading="lazy"></iframe>
		</div>
	</div>
	<p class="small text-secondary mt-2 mb-0"><i class="bi bi-info-circle me-1"></i>Los datos se actualizan según la programación del conjunto de datos en Power BI.</p>
{:else}
	<div class="card border-0">
		<div class="card-body text-center py-5">
			<i class="bi bi-bar-chart-line display-5 text-primary"></i>
			<h2 class="h5 fw-bold mt-3">El tablero aún no está publicado</h2>
			<p class="text-secondary mb-0">
				{admin
					? 'Publica el informe en Power BI (Archivo → Insertar informe → Publicar en la web) y pega aquí el enlace.'
					: 'El administrador todavía no ha configurado el tablero.'}
			</p>
		</div>
	</div>
{/if}

<VentanaModal bind:abierto={editorAbierto} titulo="Enlace del tablero de Power BI">
	<form id="form-tablero" onsubmit={guardar}>
		<CampoFormulario
			campo={{ nombre: 'url', etiqueta: 'Enlace o código <iframe> de Power BI', tipo: 'textarea', requerido: true, marcador: 'https://app.powerbi.com/view?r=...', ayuda: 'Puedes pegar el enlace o el código <iframe> completo; se toma el enlace automáticamente.' }}
			bind:valor={nuevaUrl}
		/>
	</form>
	{#snippet pie()}
		<button type="button" class="btn btn-light" onclick={() => (editorAbierto = false)}>Cancelar</button>
		<button type="submit" form="form-tablero" class="btn btn-primary" disabled={guardando}>{guardando ? 'Guardando…' : 'Guardar'}</button>
	{/snippet}
</VentanaModal>

<style>
	.marco-tablero {
		position: relative;
		width: 100%;
		aspect-ratio: 16 / 10;
		min-height: 420px;
	}
	.marco-tablero iframe {
		position: absolute;
		inset: 0;
		width: 100%;
		height: 100%;
		border: 0;
	}
	@media (max-width: 576px) {
		.marco-tablero { aspect-ratio: 9 / 16; min-height: 520px; }
	}
</style>
