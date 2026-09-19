from __future__ import annotations

from datetime import datetime

from database.connection import get_db, row_to_dict
from backend.exceptions import (
    AuditRequiredError,
    InvalidStateTransitionError,
    SolicitudNotFoundError,
)
from backend.models import CambiarEstadoIn, SolicitudCreate

ESTADOS = ("RECIBIDA", "ASIGNADA", "EN PROCESO", "ATENDIDA", "CERRADA")

TRANSICIONES_VALIDAS: dict[str, set[str]] = {
    "RECIBIDA": {"ASIGNADA"},
    "ASIGNADA": {"EN PROCESO", "RECIBIDA"},
    "EN PROCESO": {"ATENDIDA"},
    "ATENDIDA": {"CERRADA"},
    "CERRADA": set(),
}


def transiciones_permitidas(estado_actual: str) -> list[str]:
    return sorted(TRANSICIONES_VALIDAS.get(estado_actual, set()))


def _bool_adopcion(value: int | bool | None) -> bool:
    return bool(value)


def serialize_animal(row: dict | None) -> dict | None:
    if not row or row.get("id") is None:
        return None
    return {
        "id": row["id"],
        "nombre": row["nombre"],
        "especie": row["especie"],
        "raza": row["raza"],
        "edad_aproximada": row.get("edad_aproximada"),
        "estado_salud": row["estado_salud"],
        "disponible_adopcion": _bool_adopcion(row.get("disponible_adopcion")),
        "fecha_ingreso": row.get("fecha_ingreso"),
    }


def serialize_solicitud(row: dict, animal: dict | None = None) -> dict:
    data = {
        "id": row["id"],
        "codigo": row["codigo"],
        "tipo": row["tipo"],
        "ciudadano_nombre": row["ciudadano_nombre"],
        "ciudadano_telefono": row["ciudadano_telefono"],
        "descripcion": row["descripcion"],
        "barrio": row["barrio"],
        "comuna": row["comuna"],
        "fecha_registro": row["fecha_registro"],
        "estado_actual": row["estado_actual"],
        "animal_id": row.get("animal_id"),
        "animal": animal,
    }
    return data


SOLICITUD_JOIN = """
    SELECT
        s.id, s.codigo, s.tipo, s.ciudadano_nombre, s.ciudadano_telefono,
        s.descripcion, s.barrio, s.comuna, s.fecha_registro, s.estado_actual,
        s.animal_id,
        a.id AS a_id, a.nombre AS a_nombre, a.especie AS a_especie,
        a.raza AS a_raza, a.edad_aproximada AS a_edad, a.estado_salud AS a_salud,
        a.disponible_adopcion AS a_adopcion, a.fecha_ingreso AS a_ingreso
    FROM Solicitud s
    LEFT JOIN Animal a ON a.id = s.animal_id
"""


def _split_solicitud_animal(row: dict) -> tuple[dict, dict | None]:
    solicitud = {
        "id": row["id"],
        "codigo": row["codigo"],
        "tipo": row["tipo"],
        "ciudadano_nombre": row["ciudadano_nombre"],
        "ciudadano_telefono": row["ciudadano_telefono"],
        "descripcion": row["descripcion"],
        "barrio": row["barrio"],
        "comuna": row["comuna"],
        "fecha_registro": row["fecha_registro"],
        "estado_actual": row["estado_actual"],
        "animal_id": row["animal_id"],
    }
    animal = None
    if row.get("a_id") is not None:
        animal = serialize_animal(
            {
                "id": row["a_id"],
                "nombre": row["a_nombre"],
                "especie": row["a_especie"],
                "raza": row["a_raza"],
                "edad_aproximada": row["a_edad"],
                "estado_salud": row["a_salud"],
                "disponible_adopcion": row["a_adopcion"],
                "fecha_ingreso": row["a_ingreso"],
            }
        )
    return solicitud, animal


def generar_codigo(conn) -> str:
    year = datetime.now().year
    prefix = f"VET-{year}-"
    row = conn.execute(
        "SELECT codigo FROM Solicitud WHERE codigo LIKE ? ORDER BY codigo DESC LIMIT 1",
        (f"{prefix}%",),
    ).fetchone()
    if row is None:
        next_n = 1
    else:
        try:
            next_n = int(row["codigo"].split("-")[-1]) + 1
        except ValueError:
            next_n = 1
    return f"{prefix}{next_n:03d}"


def listar_solicitudes(
    estado: str | None = None,
    tipo: str | None = None,
    comuna: str | None = None,
) -> list[dict]:
    clauses = []
    params: list = []
    if estado:
        clauses.append("s.estado_actual = ?")
        params.append(estado)
    if tipo:
        clauses.append("s.tipo = ?")
        params.append(tipo)
    if comuna:
        clauses.append("s.comuna = ?")
        params.append(comuna)
    sql = SOLICITUD_JOIN
    if clauses:
        sql += " WHERE " + " AND ".join(clauses)
    sql += " ORDER BY s.fecha_registro DESC, s.id DESC"
    with get_db() as conn:
        rows = conn.execute(sql, params).fetchall()
    resultado = []
    for raw in rows:
        row = row_to_dict(raw)
        solicitud, animal = _split_solicitud_animal(row)
        resultado.append(serialize_solicitud(solicitud, animal))
    return resultado


def obtener_solicitud(solicitud_id: int) -> dict:
    with get_db() as conn:
        raw = conn.execute(SOLICITUD_JOIN + " WHERE s.id = ?", (solicitud_id,)).fetchone()
        if raw is None:
            raise SolicitudNotFoundError(solicitud_id)
        solicitud, animal = _split_solicitud_animal(row_to_dict(raw))
        historial_rows = conn.execute(
            """
            SELECT id, solicitud_id, estado_anterior, estado_nuevo,
                   fecha_cambio, responsable, observaciones
            FROM HistorialEstado
            WHERE solicitud_id = ?
            ORDER BY fecha_cambio ASC, id ASC
            """,
            (solicitud_id,),
        ).fetchall()
    data = serialize_solicitud(solicitud, animal)
    data["historial"] = [row_to_dict(h) for h in historial_rows]
    return data


def crear_solicitud(payload: SolicitudCreate) -> dict:
    with get_db() as conn:
        codigo = generar_codigo(conn)
        cur = conn.execute(
            """
            INSERT INTO Solicitud (
                codigo, tipo, ciudadano_nombre, ciudadano_telefono, descripcion,
                barrio, comuna, estado_actual, animal_id
            ) VALUES (?, ?, ?, ?, ?, ?, ?, 'RECIBIDA', ?)
            """,
            (
                codigo,
                payload.tipo,
                payload.ciudadano_nombre.strip(),
                payload.ciudadano_telefono.strip(),
                payload.descripcion.strip(),
                payload.barrio.strip(),
                payload.comuna.strip(),
                payload.animal_id,
            ),
        )
        solicitud_id = cur.lastrowid
        conn.execute(
            """
            INSERT INTO HistorialEstado (
                solicitud_id, estado_anterior, estado_nuevo, responsable, observaciones
            ) VALUES (?, NULL, 'RECIBIDA', ?, ?)
            """,
            (
                solicitud_id,
                "Mesa de entrada CBA",
                "Solicitud ciudadana radicada en el CBA Popayán.",
            ),
        )
    return obtener_solicitud(solicitud_id)


def _validar_auditoria(responsable: str, observaciones: str) -> tuple[str, str]:
    resp = (responsable or "").strip()
    obs = (observaciones or "").strip()
    if not resp:
        raise AuditRequiredError("responsable")
    if not obs:
        raise AuditRequiredError("observaciones")
    return resp, obs


def cambiar_estado(solicitud_id: int, payload: CambiarEstadoIn) -> dict:
    responsable, observaciones = _validar_auditoria(payload.responsable, payload.observaciones)
    estado_nuevo = payload.estado_nuevo

    with get_db() as conn:
        raw = conn.execute(
            "SELECT id, estado_actual FROM Solicitud WHERE id = ?",
            (solicitud_id,),
        ).fetchone()
        if raw is None:
            raise SolicitudNotFoundError(solicitud_id)
        estado_actual = raw["estado_actual"]
        permitidos = transiciones_permitidas(estado_actual)
        if estado_nuevo not in TRANSICIONES_VALIDAS.get(estado_actual, set()):
            raise InvalidStateTransitionError(estado_actual, estado_nuevo, permitidos)

        conn.execute(
            "UPDATE Solicitud SET estado_actual = ? WHERE id = ?",
            (estado_nuevo, solicitud_id),
        )
        conn.execute(
            """
            INSERT INTO HistorialEstado (
                solicitud_id, estado_anterior, estado_nuevo, responsable, observaciones
            ) VALUES (?, ?, ?, ?, ?)
            """,
            (solicitud_id, estado_actual, estado_nuevo, responsable, observaciones),
        )
    return obtener_solicitud(solicitud_id)
