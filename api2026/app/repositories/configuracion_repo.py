from app.repositories.base_repo import BaseRepository


class ConfiguracionRepository(BaseRepository):
    TABLA = "configuracion_institucional"
    PK = "clave"
    RECURSO = "Parámetro"

    def _datos_validos(self, datos: dict) -> dict:
        # En esta tabla la PK (clave) la escribe el usuario al crear
        validos = super()._datos_validos(datos)
        if "clave" in datos:
            validos["clave"] = datos["clave"]
        return validos
