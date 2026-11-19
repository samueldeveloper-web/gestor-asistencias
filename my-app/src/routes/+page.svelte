<script>
	import { haySesion, obtenerModulos } from '$lib/sesion.js';
	const destino = haySesion() && obtenerModulos().length ? obtenerModulos()[0].ruta : '/login';
</script>

<svelte:head><title>Aula Presente | Gestor de asistencia</title></svelte:head>

<section class="text-center py-5">
	<span class="badge rounded-pill text-bg-light border mb-3"><i class="bi bi-bell me-1 text-primary"></i>Notificación automática de fallas</span>
	<h1 class="display-5 fw-bold mb-3">Gestor de asistencia estudiantil</h1>
	<p class="lead text-secondary mx-auto mb-4" style="max-width:640px">
		Los docentes registran la asistencia, el sistema avisa a los acudientes cuando su hijo falta y ellos pueden enviar la excusa desde la misma plataforma.
	</p>
	<a href={destino} class="btn btn-primary btn-lg px-4"><i class="bi bi-box-arrow-in-right me-1"></i>{destino === '/login' ? 'Iniciar sesión' : 'Ir a mis módulos'}</a>
</section>

<div class="row g-4 pb-4">
	{#each [
		{ icono: 'bi-clipboard-check', titulo: 'Docente', texto: 'Toma asistencia por curso y asignatura, y revisa las excusas recibidas.' },
		{ icono: 'bi-people', titulo: 'Acudiente', texto: 'Recibe la notificación de cada falla, consulta el historial y justifica.' },
		{ icono: 'bi-gear', titulo: 'Administrador', texto: 'Gestiona estudiantes, cursos, docentes, usuarios y permisos por rol.' }
	] as tarjeta (tarjeta.titulo)}
		<div class="col-md-4">
			<div class="card h-100 border-0">
				<div class="card-body p-4">
					<i class="bi {tarjeta.icono} fs-2 text-primary"></i>
					<h2 class="h5 fw-bold mt-3">{tarjeta.titulo}</h2>
					<p class="text-secondary mb-0">{tarjeta.texto}</p>
				</div>
			</div>
		</div>
	{/each}
</div>
