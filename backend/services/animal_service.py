from database.connection import get_db, row_to_dict
from backend.services.solicitud_service import serialize_animal


def listar_animales(disponible_adopcion: bool | None = None) -> list[dict]:
    sql = """
        SELECT id, nombre, especie, raza, edad_aproximada, estado_salud,
               disponible_adopcion, fecha_ingreso
        FROM Animal
    """
    params: list = []
    if disponible_adopcion is not None:
        sql += " WHERE disponible_adopcion = ?"
        params.append(1 if disponible_adopcion else 0)
    sql += " ORDER BY fecha_ingreso DESC, id DESC"
    with get_db() as conn:
        rows = conn.execute(sql, params).fetchall()
    return [serialize_animal(row_to_dict(r)) for r in rows]
