def primera(columnas, candidatas):
    """Devuelve la primera columna de 'candidatas' que exista en 'columnas' (o None)."""
    return next((c for c in candidatas if c in columnas), None)


COLUMNAS_FK_USUARIO = ("usuarioid", "usuario_id", "id_usuario")
COLUMNAS_CORREO = ("correo", "email", "correo_electronico", "e_mail")
