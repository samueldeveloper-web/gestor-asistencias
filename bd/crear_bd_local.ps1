# crear_bd_local.ps1 · Crea la versión LOCAL de la base de datos.
#
# Requisito: PostgreSQL instalado en Windows (trae psql, pg_dump, createdb).
# Usa pg_dump de la misma versión que Neon o más nueva (Neon usa 16 o 17).
#
# Modo 1 (recomendado) · copia exacta de Neon, con todos los datos:
#   $env:DATABASE_URL = "postgresql://usuario:clave@host.neon.tech/neondb?sslmode=require"
#   powershell -ExecutionPolicy Bypass -File bd\crear_bd_local.ps1
#
# Modo 2 · BD vacía desde schema.sql + módulos + datos de prueba + vistas del tablero:
#   powershell -ExecutionPolicy Bypass -File bd\crear_bd_local.ps1 -Vacia
#
# Parámetros opcionales: -Base asistencia_local  -Usuario postgres  -Puerto 5432

param(
    [string]$NeonUrl = $env:DATABASE_URL,
    [string]$Base = "asistencia_local",
    [string]$Usuario = "postgres",
    [string]$Puerto = "5432",
    [switch]$Vacia
)

$ErrorActionPreference = "Stop"
$aqui = Split-Path -Parent $MyInvocation.MyCommand.Path

# Busca los programas de PostgreSQL si no están en el PATH.
if (-not (Get-Command psql -ErrorAction SilentlyContinue)) {
    $bin = Get-ChildItem "C:\Program Files\PostgreSQL\*\bin" -Directory -ErrorAction SilentlyContinue |
           Sort-Object { [int]($_.Parent.Name -replace '\D', '') } -Descending | Select-Object -First 1
    if ($bin) { $env:PATH = "$($bin.FullName);$env:PATH" }
}
foreach ($cmd in "psql", "pg_dump", "createdb", "dropdb") {
    if (-not (Get-Command $cmd -ErrorAction SilentlyContinue)) {
        throw "No encuentro '$cmd'. Instala PostgreSQL (https://www.postgresql.org/download/windows/) o agrega su carpeta bin al PATH."
    }
}

function Revisar($paso) {
    if ($LASTEXITCODE -ne 0) { throw "Falló: $paso" }
}

$clave = Read-Host "Contraseña del usuario '$Usuario' de tu PostgreSQL local" -AsSecureString
$env:PGPASSWORD = [Runtime.InteropServices.Marshal]::PtrToStringAuto(
    [Runtime.InteropServices.Marshal]::SecureStringToBSTR($clave))
$conexion = @("-h", "localhost", "-p", $Puerto, "-U", $Usuario)

Write-Host "Creando la base '$Base' (si ya existía se reemplaza)..."
dropdb @conexion --if-exists $Base; Revisar "borrar la base anterior (¿está abierta en pgAdmin?)"
createdb @conexion -E UTF8 $Base; Revisar "crear la base"

if ($Vacia -or -not $NeonUrl) {
    if (-not $Vacia) { Write-Host "No hay DATABASE_URL: se crea la base vacía con datos de prueba." }
    foreach ($archivo in "schema.sql", "migrations\005_modulos_y_permisos.sql", "seed.sql", "migrations\006_vistas_tablero.sql") {
        Write-Host "Ejecutando $archivo..."
        psql @conexion -d $Base -q -v ON_ERROR_STOP=1 -f (Join-Path $aqui $archivo); Revisar $archivo
    }
} else {
    $respaldo = Join-Path $aqui "respaldo_neon.sql"
    Write-Host "Copiando Neon a $respaldo..."
    $env:PGPASSWORD_LOCAL = $env:PGPASSWORD
    Remove-Item Env:PGPASSWORD   # la clave de Neon va dentro de la URL
    pg_dump $NeonUrl --no-owner --no-privileges -f $respaldo; Revisar "pg_dump de Neon"
    $env:PGPASSWORD = $env:PGPASSWORD_LOCAL
    Write-Host "Restaurando en la base local..."
    psql @conexion -d $Base -q -f $respaldo; Revisar "restaurar el respaldo"
}

Write-Host ""
Write-Host "Listo. Filas por tabla en '$Base':"
psql @conexion -d $Base -c "SELECT table_name AS tabla, (xpath('/row/n/text()', query_to_xml(format('select count(*) as n from public.%I', table_name), false, true, '')))[1]::text::int AS filas FROM information_schema.tables WHERE table_schema = 'public' AND table_type = 'BASE TABLE' ORDER BY 1;"
Write-Host "Para el backend local usa en api2026\.env: DB_HOST=localhost DB_PORT=$Puerto DB_NAME=$Base DB_USER=$Usuario"
Remove-Item Env:PGPASSWORD -ErrorAction SilentlyContinue
Remove-Item Env:PGPASSWORD_LOCAL -ErrorAction SilentlyContinue
