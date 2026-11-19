# Contrato de la API — Gestor de asistencia (api2026)

Base local: `http://127.0.0.1:8000` · Documentación interactiva: `/docs`
Todas las respuestas son JSON. Los nombres de campos son **exactamente las columnas de Neon** (ver `herramientas/reporte_bd.md`).

## Autenticación (JWT)
Todas las rutas piden `Authorization: Bearer <access_token>`, **excepto** `POST /auth/login` y `GET /roles/`.
Sin token o con token vencido → `401 {"detail": "..."}`. El token dura `JWT_MINUTOS` (480 por defecto).

### `POST /auth/login`
Entrada: `{ "identifier": "usuario o correo", "password": "...", "rolid": 4 }` (`rolid` opcional; si se envía y no coincide → 403).
Salida:
```json
{
  "access_token": "eyJ...", "token_type": "bearer",
  "usuario": {
    "usuarioid": 3, "username": "lgomez", "email": "luis@colegio.edu.co",
    "nombre": "Luis Gómez", "rolid": 4, "rol": "Docente",
    "perfil": { "tipo": "docente", "id": 1, "nombre": "Luis Gómez" }
  },
  "modulos": [ { "moduloid": 2, "nombre": "Asistencia", "ruta": "/registros", "descripcion": "...", "icono": "bi-check2",
                 "permiso_crear": true, "permiso_leer": true, "permiso_actualizar": true, "permiso_eliminar": false } ]
}
```
- `perfil.tipo`: `acudiente` (id = `acudiente_id`), `docente` (id = `personalid`), `estudiante` (id = `estudiante_id`) o `null` (administrador).
- Errores: 401 usuario/contraseña incorrectos, 403 usuario inactivo o rol distinto.

### Otras
| Método | Ruta | Uso |
|---|---|---|
| GET | `/auth/me` | Misma respuesta que el login (recargar sesión). |
| PUT | `/auth/password` | `{password_actual, password_nueva}` |
| GET | `/roles/` | **Pública**. Roles activos para el select del login. |
| GET | `/roles/{rolid}/modulos` | Módulos del rol con `permiso_leer = true` (desde `modulo_por_rol`), con permisos. |

Roles en Neon: **1 Administrador, 2 Estudiante, 3 Acudiente, 4 Docente**.

## CRUD (igual para todos los recursos)
| Método | Ruta | Respuesta |
|---|---|---|
| GET | `/<recurso>/` | Lista de filas **activas** (`esta_activo` no es false). `?incluir_inactivos=true` trae todas. Filtros por cualquier columna: `?estudianteid=3&fecha=2026-11-19`. |
| GET | `/<recurso>/{id}` | La fila, o 404. |
| POST | `/<recurso>/` | 201 `{ "mensaje", "id", "data": fila_creada }` |
| PUT | `/<recurso>/{id}` | `{ "mensaje", "data": fila_actualizada }`. Solo cambia los campos enviados; ignora la PK y las fechas (se puede mandar la fila entera). |
| DELETE | `/<recurso>/{id}` | **Borrado lógico**: pone `esta_activo = false`. `{ "mensaje" }` |
| PATCH | `/<recurso>/{id}/estado` | `{ "esta_activo": true/false }` para reactivar/desactivar. |

`fecha_creacion` y `fecha_actualizacion` las pone la BD; nunca se envían.
Errores: `404` no existe · `409` duplicado (UNIQUE) o FK inválida · `422` falta un campo obligatorio, valor fuera del CHECK o formato inválido · `503` sin conexión a la BD. Siempre `{"detail": "mensaje en español"}`.

## Recursos y campos (POST: **negrita** = obligatorio)
| Ruta | Tabla · PK | Campos |
|---|---|---|
| `/roles` | rol · `rolid` | **nombre**, descripcion |
| `/modulos` | modulo · `moduloid` | **nombre**, **ruta**, descripcion, icono |
| `/modulo-por-rol` | modulo_por_rol · `modulo_por_rolid` | **rolid**, **moduloid**, permiso_crear, permiso_leer, permiso_actualizar, permiso_eliminar |
| `/usuarios` | usuario · `usuarioid` | **username**, **email**, **password** (se guarda en bcrypt; nunca se devuelve), **rolid**, personal_institucionalid \| estudianteid \| acudienteid (máximo uno) |
| `/estudiantes` | estudiantes · `estudiante_id` | **nombres**, **apellidos**, **documento_identidad**, **fecha_nacimiento** (YYYY-MM-DD), direccion |
| `/acudientes` | acudientes · `acudiente_id` | **nombres**, **apellidos**, **telefono**, **email**, **documento_identidad**, direccion, fecha_nacimiento |
| `/acudientes/{id}/estudiantes` | (GET) | Hijos del acudiente: fila de estudiante + `estudiante_acudienteid`, `parentesco`, `contacto_principal` |
| `/estudiante-acudiente` | estudiante_acudiente · `estudiante_acudienteid` | **estudianteid**, **acudienteid**, **parentesco**, contacto_principal |
| `/cursos` | cursos · `cursoid` | **nombre_curso**, **nivel_educativo** |
| `/asignaturas` | asignaturas · `materiaid` | **nombre_materia**, descripcion |
| `/matriculas` | matriculas · `matriculaid` | **estudianteid**, **cursoid**, **anio_lectivo**, estado (activo\|retirado\|graduado\|promovido), fecha_matricula |
| `/personal-institucion` | personal_institucional · `personalid` | **nombres**, **apellidos**, **documento_identidad**, **telefono**, **email**, **cargo**, direccion |
| `/carga-academica` | carga_academica · `cargaid` | **cursoid**, **materiaid**, **personal_institucionalid**, **anio_lectivo** |
| `/asistencia` | asistencia · `asistenciaid` | **estudianteid**, **cursoid**, **materiaid**, **estado** (presente\|ausente\|tarde\|excusado), **fecha**, personal_institucionalid |
| `/notificaciones` | notificaciones · `notificacionid` | **acudienteid**, **titulo**, **mensaje**, estudianteid, asistenciaid, tipo (asistencia\|excusa\|general), leido. Lectura: enviado_correo, fecha_correo, fecha_envio |
| `/excusas` | excusas · `excusaid` | **asistenciaid**, **motivo**, acudienteid, estudianteid (si falta se toma de la asistencia), documento_adjunto. Lectura: estado (pendiente\|aprobada\|rechazada) |
| `/configuracion` | configuracion_institucional · `clave` (texto) | **clave**, **valor**. Rutas con la clave: `/configuracion/anio_lectivo` |

## Función principal: falla → notificación → correo
1. Docente: `POST /asistencia/` con `estado: "ausente"`. Respuesta incluye `"notificacion": "Se notificará por correo al acudiente"`.
2. El **trigger de la BD** crea la fila en `notificaciones` para cada acudiente del estudiante.
3. La API envía el correo en segundo plano y marca `enviado_correo = true`, `fecha_correo = now()`.
4. Acudiente: `GET /notificaciones/?acudienteid={perfil.id}` y `PATCH /notificaciones/{id}/leida` `{ "leida": true }`.
5. Acudiente: `POST /excusas/` `{asistenciaid, acudienteid, motivo}`.
6. Docente/Admin: `PUT /excusas/{id}/revisar` `{ "aprobada": true, "observacion": "..." }` → la asistencia pasa a `excusado`.

Extras: `GET /notificaciones/pendientes` (sin enviar) · `POST /notificaciones/enviar-pendientes` → `{pendientes, enviadas, fallidas, sin_correo}`.

## Filtros útiles por rol (usar `usuario.perfil.id`)
- Docente: `/carga-academica/?personal_institucionalid={id}`, `/asistencia/?personal_institucionalid={id}`
- Acudiente: `/acudientes/{id}/estudiantes`, `/notificaciones/?acudienteid={id}`, `/excusas/?acudienteid={id}`
- Estudiante: `/asistencia/?estudianteid={id}`, `/matriculas/?estudianteid={id}`, `/excusas/?estudianteid={id}`
