from fastapi import APIRouter, Depends

from app.core.excepciones import ErrorApi
from app.core.security import (COLUMNAS_PASSWORD, crear_token, usuario_actual,
                               verificar_password)
from app.models.auth import CambioPassword, LoginEntrada
from app.repositories.auth_repo import AuthRepository
from app.repositories.rol_repo import RolRepository
from app.repositories.usuario_repo import UsuarioRepository
from app.repositories.utilidades import COLUMNAS_CORREO, primera

router = APIRouter(prefix="/auth", tags=["Autenticación"])
usuarios = UsuarioRepository()
roles = RolRepository()
auth = AuthRepository()


def _sesion(usuario: dict) -> dict:
    """Arma la respuesta del login: token + usuario + módulos del rol (desde modulo_por_rol)."""
    pk = usuarios.esquema()["pk"]
    rolid = usuario.get("rolid", usuario.get("rol_id"))
    rol = roles.obtener_por_id(rolid) if rolid is not None else {}
    perfil = auth.perfil_de(usuario)
    username = usuario.get("username") or usuario.get("usuario") or usuario.get("nombre_usuario")
    email = usuario.get(primera(usuario.keys(), COLUMNAS_CORREO) or "")
    datos_usuario = {
        "usuarioid": usuario[pk],
        "username": username,
        "email": email,
        "nombre": (perfil or {}).get("nombre") or username,
        "rolid": rolid,
        "rol": rol.get("nombre"),
        "perfil": perfil,  # {"tipo": "acudiente"|"docente"|"estudiante", "id": ..., "nombre": ...}
    }
    token = crear_token({"sub": str(usuario[pk]), "rolid": rolid, "rol": rol.get("nombre"),
                         "perfil": perfil})
    return {"access_token": token, "token_type": "bearer", "usuario": datos_usuario,
            "modulos": roles.modulos_de_rol(rolid) if rolid is not None else []}


@router.post("/login")
def login(datos: LoginEntrada):
    usuario = usuarios.buscar_para_login(datos.identifier.strip())
    col_pass = usuarios.columna_password()
    if not usuario or not verificar_password(datos.password, usuario.get(col_pass) if col_pass else None):
        raise ErrorApi(401, "Usuario o contraseña incorrectos")
    col_estado = usuarios.esquema()["estado"]
    if col_estado and usuario.get(col_estado) is False:
        raise ErrorApi(403, "El usuario está inactivo")
    rolid = usuario.get("rolid", usuario.get("rol_id"))
    if datos.rolid is not None and datos.rolid != rolid:
        raise ErrorApi(403, "El usuario no tiene el rol seleccionado")
    auth.registrar_ingreso(usuario[usuarios.esquema()["pk"]])
    return _sesion({k: v for k, v in usuario.items() if k not in COLUMNAS_PASSWORD})


@router.get("/me")
def sesion_actual(token: dict = Depends(usuario_actual)):
    """Datos del usuario del token (para recargar la sesión en el front)."""
    if not token:
        raise ErrorApi(401, "Debes iniciar sesión")
    return _sesion(usuarios.obtener_por_id(int(token["sub"])))


@router.put("/password")
def cambiar_password(datos: CambioPassword, token: dict = Depends(usuario_actual)):
    if not token:
        raise ErrorApi(401, "Debes iniciar sesión")
    usuario_id = int(token["sub"])
    usuario = usuarios.buscar_para_login(usuarios.obtener_por_id(usuario_id).get("username") or "")
    col_pass = usuarios.columna_password()
    if not usuario or not verificar_password(datos.password_actual, usuario.get(col_pass)):
        raise ErrorApi(400, "La contraseña actual no es correcta")
    usuarios.actualizar(usuario_id, {"password": datos.password_nueva})
    return {"mensaje": "Contraseña actualizada"}
