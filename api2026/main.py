from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import (rutas_acudientes, rutas_configuracion, rutas_asignaturas, rutas_asistencia, rutas_auth,
                     rutas_carga_academica, rutas_cursos, rutas_estudiante_acudiente,
                     rutas_estudiantes, rutas_excusas, rutas_matriculas, rutas_modulo_por_rol,
                     rutas_modulos, rutas_notificaciones, rutas_personal_institucion,
                     rutas_reportes, rutas_roles, rutas_usuarios)
from app.core.config import Config
from app.core.excepciones import registrar_manejadores

app = FastAPI(
    title="API Gestor de Asistencia Estudiantil",
    description="Registro de asistencia y notificación por correo a los acudientes de las fallas. "
                "FastAPI + PostgreSQL (Neon) con SQL puro.",
    version="1.0.0",
)

# CORS: permite que el frontend de SvelteKit consuma la API
app.add_middleware(
    CORSMiddleware,
    allow_origins=Config.CORS_ORIGENES,
    allow_origin_regex=r"https?://(localhost|127\.0\.0\.1)(:\d+)?|capacitor://localhost",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

registrar_manejadores(app)

# Conectamos los módulos de rutas a la aplicación principal
for modulo in (rutas_auth, rutas_roles, rutas_modulos, rutas_modulo_por_rol, rutas_usuarios,
               rutas_estudiantes, rutas_acudientes, rutas_estudiante_acudiente, rutas_cursos,
               rutas_asignaturas, rutas_matriculas, rutas_personal_institucion,
               rutas_carga_academica, rutas_asistencia, rutas_notificaciones, rutas_excusas,
               rutas_configuracion, rutas_reportes):
    app.include_router(modulo.router)


@app.get("/", tags=["Estado"])
def estado_api():
    return {"mensaje": "La API de asistencia se encuentra en línea y funcional", "docs": "/docs"}
