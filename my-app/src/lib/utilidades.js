/** Funciones de apoyo para mostrar datos sin exponer IDs. */

export function nombreCompleto(fila) {
	if (!fila) return '';
	return [fila.nombres ?? fila.nombre, fila.apellidos].filter(Boolean).join(' ');
}

/** Crea un Map id → etiqueta para resolver nombres en tablas. */
export function mapaPorId(filas, campoId, etiqueta) {
	return new Map(filas.map((f) => [f[campoId], typeof etiqueta === 'function' ? etiqueta(f) : f[etiqueta]]));
}

/** Opciones para un <select>: [{ valor, etiqueta }]. */
export function opciones(filas, campoId, etiqueta) {
	return filas.map((f) => ({
		valor: f[campoId],
		etiqueta: typeof etiqueta === 'function' ? etiqueta(f) : f[etiqueta]
	}));
}

export function soloActivos(filas) {
	return filas.filter((f) => (f.esta_activo ?? f.estado ?? true) !== false);
}

export function formatearFecha(valor) {
	if (!valor) return '';
	const texto = String(valor);
	const [a, m, d] = texto.slice(0, 10).split('-');
	return d ? `${d}/${m}/${a}` : texto;
}

export function formatearFechaHora(valor) {
	if (!valor) return '';
	const fecha = new Date(valor);
	if (Number.isNaN(fecha.getTime())) return String(valor);
	return fecha.toLocaleString('es-CO', { dateStyle: 'short', timeStyle: 'short' });
}

export function hoy() {
	const f = new Date();
	return `${f.getFullYear()}-${String(f.getMonth() + 1).padStart(2, '0')}-${String(f.getDate()).padStart(2, '0')}`;
}

export function capitalizar(texto) {
	if (!texto) return '';
	const t = String(texto);
	return t.charAt(0).toUpperCase() + t.slice(1);
}

/** Escapa texto antes de pasarlo a DataTables como HTML. */
export function escaparHtml(valor) {
	return String(valor ?? '')
		.replaceAll('&', '&amp;')
		.replaceAll('<', '&lt;')
		.replaceAll('>', '&gt;')
		.replaceAll('"', '&quot;');
}

const TONOS = {
	presente: 'success', ausente: 'danger', falla: 'danger', tarde: 'warning', excusado: 'info',
	pendiente: 'warning', aprobada: 'success', rechazada: 'danger', activo: 'success', inactivo: 'secondary',
	leida: 'secondary', 'no leida': 'primary', enviada: 'success'
};

export function tonoDe(texto) {
	const clave = String(texto ?? '').normalize('NFD').replace(/[̀-ͯ]/g, '').toLowerCase();
	return TONOS[clave] ?? 'secondary';
}

/** HTML de una etiqueta de estado para usar dentro de DataTables. */
export function insignia(texto) {
	return `<span class="badge rounded-pill text-bg-${tonoDe(texto)}">${escaparHtml(capitalizar(texto))}</span>`;
}
