from database.connection import get_db

ESTADOS = ("RECIBIDA", "ASIGNADA", "EN PROCESO", "ATENDIDA", "CERRADA")


def obtener_kpis() -> dict:
    with get_db() as conn:
        total = conn.execute("SELECT COUNT(*) AS n FROM Solicitud").fetchone()["n"]
        por_estado_rows = conn.execute(
            "SELECT estado_actual, COUNT(*) AS n FROM Solicitud GROUP BY estado_actual"
        ).fetchall()
        por_comuna_rows = conn.execute(
            "SELECT comuna, COUNT(*) AS n FROM Solicitud GROUP BY comuna ORDER BY comuna"
        ).fetchall()

    por_estado = {estado: 0 for estado in ESTADOS}
    for row in por_estado_rows:
        por_estado[row["estado_actual"]] = row["n"]

    por_comuna = {row["comuna"]: row["n"] for row in por_comuna_rows}
    atendidas = por_estado["ATENDIDA"] + por_estado["CERRADA"]
    abiertas = total - por_estado["CERRADA"]
    tasa = round((atendidas / total) * 100, 2) if total else 0.0

    return {
        "total_solicitudes": total,
        "abiertas": abiertas,
        "atendidas": atendidas,
        "tasa_resolucion": tasa,
        "por_estado": por_estado,
        "por_comuna": por_comuna,
    }
