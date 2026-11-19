# Guía Corte 3 — Reportes, Tablero y APK

Todo está integrado en el mismo aplicativo (API `api2026` + web `my-app` + móvil `movil`).

## 0. Preparar (una vez)
```powershell
# BD: crea las vistas para Power BI y el parámetro del tablero
python bd\ejecutar_sql.py bd\migrations\006_vistas_tablero.sql   # o pégalo en el SQL Editor de Neon

# API: instala las 2 librerías nuevas (reportlab = PDF, openpyxl = Excel)
cd api2026
.\myvenv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload --host 0.0.0.0
```
`--host 0.0.0.0` deja que el celular llegue a la API por la WiFi.

Para enviar reportes por correo llena `SMTP_USER` y `SMTP_PASSWORD` en `api2026\.env` (Gmail: contraseña de aplicación).

---

## 1. Módulo de reportes (`/reportes`)
- **3 reportes**, cada uno une 3 o más tablas y **no muestra IDs**:
  | Reporte | Tablas |
  |---|---|
  | Detalle de asistencia | asistencia, estudiantes, cursos, asignaturas, personal_institucional, carga_academica |
  | Consolidado por estudiante | asistencia, estudiantes, cursos, estudiante_acudiente, acudientes |
  | Notificaciones a acudientes | notificaciones, acudientes, asistencia, estudiantes, cursos |
- **Filtros**: rango de fechas (obligatorio), curso, asignatura, estudiante y estado.
- **Acciones**: ver en pantalla (DataTables), **PDF**, **Excel** y **enviar por correo** (adjunto PDF o Excel).
- **Formato**: encabezado con la institución, título, filtros aplicados, tarjetas de resumen, tabla con los colores del aplicativo, estados en color y pie con fecha, usuario y número de página.
- **Por rol**: el docente solo ve sus clases, el acudiente solo a sus hijos y el estudiante solo lo suyo. Eso se filtra en la API con el token.

Rutas de la API: `GET /reportes/{tipo}`, `GET /reportes/{tipo}/pdf`, `GET /reportes/{tipo}/excel`, `POST /reportes/{tipo}/enviar`
(`tipo` = asistencia | consolidado | notificaciones). Se pueden probar en `/docs`.

Para la sustentación, filtra por un curso y un rango de fechas, exporta a PDF y a Excel, y envíalo a tu correo.

---

## 2. Módulo tablero (`/tablero`) con Power BI
### 2.1 Conectar Power BI Desktop a Neon
1. Power BI Desktop → **Obtener datos → Base de datos PostgreSQL**.
2. Servidor: el host de Neon (`ep-xxxx.us-east-1.aws.neon.tech`). Base de datos: `neondb`. Modo: **Importar**.
3. Usuario y contraseña de Neon (los mismos del `.env`).
   - Si pide un certificado o falla el SSL, instala el conector Npgsql que sugiere Power BI y vuelve a intentar.
4. Selecciona las vistas **`vw_tablero_asistencia`**, **`vw_tablero_notificaciones`** y **`vw_tablero_excusas`** → Cargar.

### 2.2 Medidas (Modelado → Nueva medida)
```DAX
Registros = COUNTROWS(vw_tablero_asistencia)
Fallas = SUM(vw_tablero_asistencia[es_falla])
% Asistencia = DIVIDE(SUM(vw_tablero_asistencia[asistio]), [Registros])
Notificaciones enviadas = SUM(vw_tablero_notificaciones[enviada_correo])
% Notificaciones leídas = DIVIDE(SUM(vw_tablero_notificaciones[leida]), COUNTROWS(vw_tablero_notificaciones))
Excusas aprobadas = CALCULATE(COUNTROWS(vw_tablero_excusas), vw_tablero_excusas[estado_revision] = "aprobada")
```

### 2.3 Visuales que pide la guía (solo barras y circular)
- **KPIs** (visual Tarjeta): Registros, Fallas, % Asistencia, Notificaciones enviadas, % Notificaciones leídas.
- **Gráfico de barras**: Fallas por `curso` (eje) y otro de Fallas por `asignatura`.
- **Gráfico circular**: Registros por `estado` (presente, ausente, tarde, excusado).
- **Filtros** (segmentación de datos): `fecha` (entre), `curso`, `asignatura`, `docente`.
- Colores del aplicativo: azul `#3659D9`, verde `#198754`, rojo `#DC3545`, naranja `#FD7E14`, celeste `#0DCAF0`.

### 2.4 Publicar y embeber
1. **Publicar** → Mi área de trabajo (inicia sesión con tu cuenta institucional).
2. En app.powerbi.com abre el informe → **Archivo → Insertar informe → Publicar en la web (público)** → Crear código.
3. Copia el enlace (`https://app.powerbi.com/view?r=...`) o el código `<iframe>` completo.
4. En el aplicativo entra como **Administrador** a **Tablero → Configurar tablero**, pega el enlace y guarda.
   Se guarda en la BD (`configuracion_institucional`, clave `tablero_powerbi_url`) y lo ven todos los roles que tienen el módulo.

> Si tu cuenta institucional no permite "Publicar en la web", el administrador del tenant debe activarlo. La otra opción es usar "Insertar → Sitio web o portal", que pide iniciar sesión en Power BI para verlo.

---

## 3. Versión móvil: APK Android con Capacitor (`movil/`)
**Necesitas** Node.js y **Android Studio** (trae el SDK y Java). Ábrelo una vez para que descargue el SDK.

```powershell
# 1. URL de la API para el celular: la IP de tu PC en la WiFi (ver con: ipconfig)
cd my-app
copy .env.movil.example .env.movil      # edita VITE_API_BASE_URL=http://TU_IP:8000
npm install

# 2. Proyecto Android (solo la primera vez)
cd ..\movil
npm install
npm run web                 # compila la web en my-app\build
npm run agregar-android     # crea movil\android y permite http

# 3. Abrir en Android Studio
npm run sincronizar
npm run abrir
```
En Android Studio espera a que termine "Gradle sync" y usa el menú **Build → Build App Bundle(s) / APK(s) → Build APK(s)**.
El APK queda en **`movil\android\app\build\outputs\apk\debug\app-debug.apk`** (el aviso "locate" de Android Studio abre la carpeta).

**Sin abrir Android Studio** (después de abrirlo una vez): `npm run apk`. Si sale "JAVA_HOME is not set", ejecuta antes
`$env:JAVA_HOME="C:\Program Files\Android\Android Studio\jbr"` y `$env:ANDROID_HOME="$env:LOCALAPPDATA\Android\Sdk"`.

**Instalar en el celular:**
- Copia `app-debug.apk` al celular (cable, Drive o WhatsApp), ábrelo y acepta "instalar apps de origen desconocido".
- O con el celular conectado por USB (depuración USB activa): `adb install app-debug.apk`.

**Cada vez que cambies la web:** `npm run sincronizar` (o `npm run apk`) dentro de `movil`.

Notas:
- El celular y el PC deben estar en la misma WiFi, y la API corriendo con `--host 0.0.0.0`. Si Windows pregunta por el firewall, permite el acceso a Python.
- Si la API ya está en la nube, pon esa URL en `.env.movil` y funciona desde cualquier red.
- En el APK los reportes se reciben con **Enviar por correo** (el celular no descarga archivos desde la app).
- La app carga Bootstrap y DataTables por CDN, así que el celular necesita internet.
