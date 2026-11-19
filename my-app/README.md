# Aula Presente · Frontend (SvelteKit + JavaScript)

Gestor de asistencia estudiantil que notifica a los acudientes las fallas de sus hijos.
Proyecto SvelteKit (plantilla minimal, **JavaScript**, sin TypeScript) con **Bootstrap 5** y **DataTables** por CDN.

## Ejecutar

```sh
npm install
copy .env.example .env      # Windows (en Linux/Mac: cp .env.example .env)
npm run dev -- --open       # http://localhost:5173
```

La API (`api2026`) debe estar encendida: `uvicorn main:app --reload` en `http://127.0.0.1:8000`.
Si la API está en la nube, cambia `VITE_API_BASE_URL` en `.env`.

## Estructura

```
src/
├── app.html                 Bootstrap 5, Bootstrap Icons, jQuery y DataTables por CDN
├── lib/
│   ├── api/                 http.js (único fetch y URL) + un <recurso>Api.js por tabla
│   ├── components/          13 componentes PascalCase reutilizados
│   ├── catalogos.js         carga de listas y alcance por rol (mis hijos, mis cursos…)
│   ├── sesion.js            token JWT, usuario, módulos y permisos
│   ├── utilidades.js        formatos, insignias y opciones de select
│   └── estilos.css          colores de la plantilla
└── routes/
    ├── +layout.svelte       encabezado, menú lateral (desde modulo_por_rol), pie y guardia de rutas
    ├── login/               login con selector de rol
    └── <módulo>/+page.svelte
```

## Componentes reutilizados
`Encabezado`, `MenuLateral`, `PiePagina`, `EncabezadoPagina`, `Alerta`, `Cargando`, `EtiquetaEstado`,
`TarjetaIndicador`, `TablaDatos` (DataTables), `VentanaModal`, `CampoFormulario`, `FormularioRecurso`,
`ConfirmarEliminacion` y `PaginaCrud` (combina tabla + formulario + confirmación).

## Módulos por rol
El menú y el acceso a cada ruta salen **solo** de la tabla `modulo_por_rol` (respuesta del login).
Los botones Crear / Editar / Eliminar se muestran según `permiso_crear`, `permiso_actualizar` y `permiso_eliminar`.

| Ruta | Administrador | Docente | Acudiente | Estudiante |
|---|---|---|---|---|
| /dashboard | ✔ | ✔ | ✔ | ✔ |
| /estudiantes, /acudientes, /docentes, /cursos, /asignaturas, /carga-academica, /matriculas | CRUD | estudiantes (lectura) | | |
| /mis-cursos | | ✔ | | |
| /mis-hijos | | | ✔ (edita parentesco) | |
| /asistencia | CRUD | CRUD + tomar lista | lectura | lectura |
| /excusas | revisar | revisar (aprobar/rechazar) | CRUD | lectura |
| /notificaciones | CRUD + enviar correos | CRUD | leer / archivar | |
| /usuarios, /roles-modulos | CRUD | | | |

## Reglas que cumple
- Nunca se muestran IDs ni se piden: todos los campos de relación son `select` con nombres.
- Eliminar = borrado lógico (`DELETE` de la API pone `esta_activo = false`).
- Todas las tablas usan DataTables (búsqueda, orden, paginación, responsive, en español).

## Función principal
1. Docente → Asistencia → **Tomar lista** y marca *Ausente*.
2. La BD crea la notificación y la API envía el correo al acudiente.
3. Acudiente → Notificaciones (la lee) → Excusas → **Nueva excusa**.
4. Docente → Excusas → **Editar** → Aprobar: la asistencia pasa a *Excusado* en todos los roles.
