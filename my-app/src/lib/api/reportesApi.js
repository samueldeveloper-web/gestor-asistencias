/**
 * Llamadas a la API para el módulo de reportes (Corte 3).
 * Tipos: asistencia (detalle) · consolidado (por estudiante) · notificaciones (enviadas a acudientes)
 * Rutas: GET /reportes/{tipo} · GET /reportes/{tipo}/pdf · GET /reportes/{tipo}/excel · POST /reportes/{tipo}/enviar
 * Filtros: fecha_inicio y fecha_fin (obligatorios), cursoid, materiaid, estudianteid, estado.
 */
import { obtenerJson, enviarJson, descargarArchivo } from './http.js';

const RUTA = '/reportes';

/** Quita los filtros vacíos y arma el query string. */
function consulta(filtros) {
	const limpios = Object.fromEntries(Object.entries(filtros).filter(([, v]) => v !== null && v !== undefined && v !== ''));
	return new URLSearchParams(limpios).toString();
}

export const TIPOS_REPORTE = [
	{ valor: 'asistencia', etiqueta: 'Detalle de asistencia' },
	{ valor: 'consolidado', etiqueta: 'Consolidado por estudiante' },
	{ valor: 'notificaciones', etiqueta: 'Notificaciones a acudientes' }
];

/** Datos del reporte para verlos en pantalla: { titulo, columnas, filas, filtros, resumen }. */
export const verReporte = (tipo, filtros) => obtenerJson(`${RUTA}/${tipo}?${consulta(filtros)}`);

/** Descarga el reporte en 'pdf' o 'excel'. Devuelve { blob, nombre }. */
export const descargarReporte = (tipo, formato, filtros) =>
	descargarArchivo(`${RUTA}/${tipo}/${formato}?${consulta(filtros)}`, `reporte_${tipo}.${formato === 'pdf' ? 'pdf' : 'xlsx'}`);

/** Envía el reporte por correo: datos = { ...filtros, correo, formato, mensaje }. */
export const enviarReporte = (tipo, datos) =>
	enviarJson(`${RUTA}/${tipo}/enviar`, Object.fromEntries(Object.entries(datos).filter(([, v]) => v !== null && v !== '')));
