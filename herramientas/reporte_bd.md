# Reporte de la base de datos (Neon, PostgreSQL)

Fuente: consulta de solo lectura que el usuario corrió en el SQL Editor de Neon el 19/11/2026.
16 tablas en `public`. Todas tienen `esta_activo` (salvo `excusas`), `fecha_creacion` y `fecha_actualizacion`.
Los nombres de PK/FK NO son uniformes (`estudiante_id` vs `estudianteid`): usar exactamente los de abajo.

| tabla | PK | filas |
|---|---|---|
| acudientes | acudiente_id | 12 |
| asignaturas | materiaid | 9 |
| asistencia | asistenciaid | 12 |
| carga_academica | cargaid | 11 |
| configuracion_institucional | clave (varchar) | 3 |
| cursos | cursoid | 11 |
| estudiante_acudiente | estudiante_acudienteid | 14 |
| estudiantes | estudiante_id | 13 |
| excusas | excusaid | 5 |
| matriculas | matriculaid | 14 |
| modulo | moduloid | 11 |
| modulo_por_rol | modulo_por_rolid | 42 |
| notificaciones | notificacionid | 12 |
| personal_institucional | personalid | 10 |
| rol | rolid | 4 |
| usuario | usuarioid | 4 |

Ojo: la tabla se llama `personal_institucional` (no `personal_institucion`) y la FK que la referencia se llama `personal_institucionalid`.

## Columnas

**acudientes**: acudiente_id serial PK, nombres varchar NN, apellidos varchar NN, telefono varchar NN, email varchar NN, direccion text, fecha_nacimiento date, documento_identidad varchar NN UNIQUE, esta_activo bool NN default true, fecha_creacion timestamp NN, fecha_actualizacion timestamptz NN.

**asignaturas**: materiaid serial PK, nombre_materia varchar NN UNIQUE, descripcion text, esta_activo bool default true (admite NULL), fecha_creacion timestamp, fecha_actualizacion timestamptz.

**asistencia**: asistenciaid serial PK, estudianteid int NN → estudiantes(estudiante_id), cursoid int NN → cursos, personal_institucionalid int → personal_institucional(personalid) ON DELETE SET NULL, materiaid int NN → asignaturas, estado varchar NN CHECK (presente|ausente|tarde|excusado), fecha date NN, esta_activo, fecha_creacion timestamptz, fecha_actualizacion timestamptz. UNIQUE (estudianteid, cursoid, materiaid, fecha).

**carga_academica**: cargaid serial PK, cursoid NN → cursos, materiaid NN → asignaturas, personal_institucionalid NN → personal_institucional, anio_lectivo int NN, esta_activo, fechas. UNIQUE (cursoid, materiaid, anio_lectivo).

**configuracion_institucional**: clave varchar PK, valor text NN, esta_activo, fechas.

**cursos**: cursoid serial PK, nombre_curso varchar NN UNIQUE, nivel_educativo varchar NN, esta_activo (admite NULL), fechas.

**estudiante_acudiente**: estudiante_acudienteid serial PK, estudianteid NN → estudiantes, acudienteid NN → acudientes, parentesco varchar NN, contacto_principal bool NN default false, esta_activo, fechas. (La migración 001 creó índices únicos por par y por contacto principal; pendiente confirmar.)

**estudiantes**: estudiante_id serial PK, nombres NN, apellidos NN, documento_identidad NN UNIQUE, fecha_nacimiento date NN, direccion text, esta_activo (admite NULL), fechas. Ya NO tiene acudiente_id (la 001 se aplicó).

**excusas**: excusaid serial PK, asistenciaid NN → asistencia, estudianteid NN → estudiantes, acudienteid → acudientes, motivo text NN, documento_adjunto varchar, estado varchar default 'pendiente' CHECK (pendiente|aprobada|rechazada), fecha_presentacion timestamp, fechas. **Sin esta_activo.**

**matriculas**: matriculaid serial PK, estudianteid NN → estudiantes, cursoid NN → cursos, anio_lectivo int NN, estado varchar default 'activo' CHECK (activo|retirado|graduado|promovido), fecha_matricula date, esta_activo, fechas. UNIQUE (estudianteid, anio_lectivo).

**modulo**: moduloid serial PK, nombre varchar NN, ruta varchar NN UNIQUE, icono varchar, descripcion text, esta_activo, fechas.

**modulo_por_rol**: modulo_por_rolid serial PK, rolid NN → rol CASCADE, moduloid NN → modulo CASCADE, permiso_crear/leer/actualizar/eliminar bool NN, esta_activo, fechas. UNIQUE (rolid, moduloid).

**notificaciones**: notificacionid serial PK, estudianteid → estudiantes, acudienteid NN → acudientes, titulo varchar NN, mensaje text NN, tipo varchar default 'asistencia' CHECK (asistencia|excusa|general), leido bool default false, fecha_envio timestamp default now, esta_activo, fechas.

**personal_institucional**: personalid serial PK, nombres, apellidos, documento_identidad UNIQUE, telefono, direccion, email, cargo (todos NN salvo direccion), esta_activo (admite NULL), fechas.

**rol**: rolid serial PK, nombre varchar NN UNIQUE, descripcion text, esta_activo, fechas.

**usuario**: usuarioid serial PK, username UNIQUE, email UNIQUE, password_hash NN, rolid NN → rol, personal_institucionalid UNIQUE → personal_institucional, estudianteid UNIQUE → estudiantes, acudienteid UNIQUE → acudientes (los tres ON DELETE SET NULL; CHECK: máximo uno de los tres), esta_activo, ultimo_ingreso timestamptz, fechas.

## Triggers
Cada tabla tiene dos triggers de actualización: `trg_update_<tabla>` y `trg_<tabla>_fecha_actualizacion` (configuracion_institucional solo el segundo). No hay trigger que cree notificaciones al registrar una falla.

## Hallazgos (detalle en el hilo de BD)
1. `excusas` sin `esta_activo`.
2. `esta_activo` admite NULL en asignaturas, cursos, estudiantes, personal_institucional.
3. Triggers de actualización duplicados.
4. FKs duplicadas en asistencia, carga_academica, matriculas, excusas (excusas.asistenciaid con RESTRICT y CASCADE a la vez; carga_academica.personal_institucionalid NOT NULL con SET NULL).
5. `fecha_creacion` mezcla timestamp y timestamptz.
6. Falta trigger falla → notificación; a `notificaciones` le faltan `asistenciaid` y marca de correo enviado.
7. Pocos datos: piden 20 filas en principales y 10 en secundarias.

Pendiente de confirmar con una segunda consulta: datos de rol/modulo/permisos, formato de password_hash, definición de las funciones de trigger e índices.
