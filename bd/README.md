# Base de datos · Aula Presente

PostgreSQL en **Neon** (nube) + versión **local**. 16 tablas, todas con
`esta_activo` (borrado lógico), `fecha_creacion` y `fecha_actualizacion`
automáticas (DEFAULT + trigger BEFORE UPDATE).

| Archivo | Para qué |
|---|---|
| `schema.sql` | Esquema final completo (tablas, llaves, triggers). Fuente única para API, front y modelo en Access. |
| `migrations/001…002` | Ya aplicadas en Neon en octubre. **No volver a correr.** |
| `migrations/003_completar_estructura.sql` | Borrado lógico en todas las tablas, fechas TIMESTAMPTZ, un solo trigger de fecha por tabla, quita FKs duplicadas. |
| `migrations/004_falla_genera_notificacion.sql` | **Función principal**: falla → notificación al acudiente; excusa revisada → aviso. |
| `migrations/005_modulos_y_permisos.sql` | 17 módulos del menú y permisos de los 4 roles. |
| `migrations/006_vistas_tablero.sql` | Vistas para Power BI y clave `tablero_powerbi_url`. Va de último. |
| `seed.sql` | Completa datos de prueba: ≥ 20 filas en tablas principales, ≥ 10 en secundarias. |
| `ejecutar_sql.py` | Ejecuta archivos .sql contra Neon (o local). |
| `crear_bd_local.ps1` | Crea la versión local (copia de Neon o desde cero). |

## 1. Aplicar los cambios en Neon (una sola vez, en este orden)

```powershell
pip install psycopg2-binary
$env:DATABASE_URL = "postgresql://usuario:clave@host.neon.tech/neondb?sslmode=require"
python bd\ejecutar_sql.py bd\migrations\003_completar_estructura.sql bd\migrations\004_falla_genera_notificacion.sql bd\migrations\005_modulos_y_permisos.sql bd\seed.sql bd\migrations\006_vistas_tablero.sql
```

Antes, por seguridad, crea una rama de respaldo en Neon (Branches → Create branch).
Cada archivo es una transacción: si falla, no deja cambios a medias.
Todos se pueden volver a correr sin duplicar nada.

## 2. Versión local

```powershell
$env:DATABASE_URL = "...la de Neon..."
powershell -ExecutionPolicy Bypass -File bd\crear_bd_local.ps1          # copia exacta de Neon
powershell -ExecutionPolicy Bypass -File bd\crear_bd_local.ps1 -Vacia   # desde schema.sql + datos de prueba
```

El respaldo `bd\respaldo_neon.sql` contiene datos personales: no lo subas a GitHub.

## 3. Roles y acceso

| rolid | Rol | Menú |
|---|---|---|
| 1 | Administrador | todo excepto Mis cursos / Mis hijos |
| 2 | Estudiante | Inicio, Asistencia, Excusas, Reportes (lectura) |
| 3 | Acudiente | Inicio, Mis hijos, Asistencia, Excusas (crear), Notificaciones, Reportes |
| 4 | Docente | Inicio, Mis cursos, Estudiantes, Asistencia (registrar), Excusas (revisar), Notificaciones, Reportes, Tablero |

La API debe listar solo módulos con `modulo.esta_activo`, `modulo_por_rol.esta_activo` y `permiso_leer` en TRUE.
Usuarios nuevos de prueba: contraseña **`Aula2026*`** (bcrypt). Ejemplos: `andres.rojas` (Docente), `claudia.rincon` (Acudiente), `valentina.gomez01` (Estudiante), `camilo.torres` (Administrador).

## 4. Función principal (cómo se prueba en la sustentación)

1. El docente registra asistencia `ausente` → el trigger `trg_asistencia_notificar_falla_ins`
   crea una fila en `notificaciones` por cada acudiente activo del estudiante.
2. La API envía el correo de las notificaciones con `enviado_correo = FALSE` y las marca.
3. El acudiente registra una excusa (`pendiente`); el docente la aprueba → la asistencia pasa a
   `excusado` y el acudiente recibe otra notificación (tipo `excusa`).

```sql
SELECT n.fecha_envio, n.titulo, a.email, n.enviado_correo
FROM notificaciones n JOIN acudientes a ON a.acudiente_id = n.acudienteid
ORDER BY n.notificacionid DESC LIMIT 5;
```

## 5. Comprobar fechas automáticas

```sql
UPDATE estudiantes SET direccion = direccion WHERE estudiante_id = 1;
SELECT fecha_creacion, fecha_actualizacion FROM estudiantes WHERE estudiante_id = 1;
```
