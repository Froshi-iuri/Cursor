"""Sembrado de datos representativos del CBA Popayán."""

from __future__ import annotations

import sqlite3
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from database.connection import connect, get_db_path, init_schema  # noqa: E402

ANIMALES = [
    ("Luna", "canino", "Criollo", "2 años", "Excelente", 1, "2025-11-02 09:15:00"),
    ("Misi", "felino", "Comunidad urbana", "8 meses", "Estable", 1, "2026-01-14 11:40:00"),
    ("Relámpago", "equino", "Criollo carretillero", "7 años", "En Tratamiento", 0, "2026-03-08 08:00:00"),
    ("Rocky", "canino", "Criollo mestizo", "4 años", "Recuperado", 1, "2026-04-21 16:20:00"),
    ("Canela", "felino", "Doméstico pelo corto", "3 años", "Excelente", 1, "2026-06-03 10:05:00"),
    ("Estrella", "equino", "Poni mestizo", "5 años", "Estable", 0, "2026-07-19 07:30:00"),
    ("Toby", "canino", "Labrador mestizo", "6 meses", "Crítico", 0, "2026-09-01 18:45:00"),
]

SOLICITUDES = [
    {
        "codigo": "VET-2026-001",
        "tipo": "rescate",
        "ciudadano_nombre": "María Fernanda Muñoz",
        "ciudadano_telefono": "3125550101",
        "descripcion": "Canino atropellado en vía a Prados del Norte, requiere atención inmediata.",
        "barrio": "Prados del Norte",
        "comuna": "Comuna 1",
        "fecha_registro": "2026-09-02 08:12:00",
        "estado_actual": "RECIBIDA",
        "animal_nombre": "Toby",
    },
    {
        "codigo": "VET-2026-002",
        "tipo": "adopcion",
        "ciudadano_nombre": "Carlos Andrés Hurtado",
        "ciudadano_telefono": "3005550102",
        "descripcion": "Solicitud de adopción de Luna, canina criolla recuperada en el CBA.",
        "barrio": "La Estancia",
        "comuna": "Comuna 2",
        "fecha_registro": "2026-08-20 14:00:00",
        "estado_actual": "ASIGNADA",
        "animal_nombre": "Luna",
    },
    {
        "codigo": "VET-2026-003",
        "tipo": "vacunacion",
        "ciudadano_nombre": "Liliana Gómez",
        "ciudadano_telefono": "3185550103",
        "descripcion": "Jornada de vacunación antirrábica para colonia felina en Pandiguando.",
        "barrio": "Pandiguando",
        "comuna": "Comuna 3",
        "fecha_registro": "2026-08-05 09:30:00",
        "estado_actual": "EN PROCESO",
        "animal_nombre": "Misi",
    },
    {
        "codigo": "VET-2026-004",
        "tipo": "esterilizacion",
        "ciudadano_nombre": "José Luis Valencia",
        "ciudadano_telefono": "3155550104",
        "descripcion": "Esterilización de felina doméstica del Centro Histórico.",
        "barrio": "Centro Histórico",
        "comuna": "Comuna 4",
        "fecha_registro": "2026-07-12 11:10:00",
        "estado_actual": "ATENDIDA",
        "animal_nombre": "Canela",
    },
    {
        "codigo": "VET-2026-005",
        "tipo": "rescate",
        "ciudadano_nombre": "Diana Patricia Campo",
        "ciudadano_telefono": "3115550105",
        "descripcion": "Caballo carretillero decomisado por maltrato y sustitución de tracción animal.",
        "barrio": "Los Sauces",
        "comuna": "Comuna 5",
        "fecha_registro": "2026-03-08 07:50:00",
        "estado_actual": "CERRADA",
        "animal_nombre": "Relámpago",
    },
    {
        "codigo": "VET-2026-006",
        "tipo": "adopcion",
        "ciudadano_nombre": "Andrés Felipe Solarte",
        "ciudadano_telefono": "3045550106",
        "descripcion": "Interés de adopción de Rocky, canino recuperado de La Esmeralda.",
        "barrio": "La Esmeralda",
        "comuna": "Comuna 6",
        "fecha_registro": "2026-09-10 16:22:00",
        "estado_actual": "RECIBIDA",
        "animal_nombre": "Rocky",
    },
    {
        "codigo": "VET-2026-007",
        "tipo": "vacunacion",
        "ciudadano_nombre": "Yolanda Burbano",
        "ciudadano_telefono": "3205550107",
        "descripcion": "Vacunación de caninos comunitarios en Las Palmas.",
        "barrio": "Las Palmas",
        "comuna": "Comuna 7",
        "fecha_registro": "2026-09-04 10:00:00",
        "estado_actual": "ASIGNADA",
        "animal_nombre": None,
    },
    {
        "codigo": "VET-2026-008",
        "tipo": "rescate",
        "ciudadano_nombre": "Héctor Fabio Ordóñez",
        "ciudadano_telefono": "3175550108",
        "descripcion": "Equino abandonado cerca de El Mirador, requiere evaluación clínica.",
        "barrio": "El Mirador",
        "comuna": "Comuna 8",
        "fecha_registro": "2026-07-19 07:10:00",
        "estado_actual": "EN PROCESO",
        "animal_nombre": "Estrella",
    },
    {
        "codigo": "VET-2026-009",
        "tipo": "esterilizacion",
        "ciudadano_nombre": "Paola Andrea Narváez",
        "ciudadano_telefono": "3135550109",
        "descripcion": "Campaña de esterilización en María Oriente.",
        "barrio": "María Oriente",
        "comuna": "Comuna 9",
        "fecha_registro": "2026-06-18 13:40:00",
        "estado_actual": "ATENDIDA",
        "animal_nombre": None,
    },
    {
        "codigo": "VET-2026-010",
        "tipo": "rescate",
        "ciudadano_nombre": "Wilson Eduardo Paz",
        "ciudadano_telefono": "3165550110",
        "descripcion": "Reporte de caninos sin tutor en zona rural de Julumito.",
        "barrio": "Julumito",
        "comuna": "Zona Rural",
        "fecha_registro": "2026-09-15 09:05:00",
        "estado_actual": "RECIBIDA",
        "animal_nombre": None,
    },
    {
        "codigo": "VET-2026-011",
        "tipo": "vacunacion",
        "ciudadano_nombre": "Sandra Milena Torres",
        "ciudadano_telefono": "3015550111",
        "descripcion": "Vacunación de mascotas en El Recuerdo, Comuna 1.",
        "barrio": "El Recuerdo",
        "comuna": "Comuna 1",
        "fecha_registro": "2026-05-22 08:45:00",
        "estado_actual": "CERRADA",
        "animal_nombre": None,
    },
    {
        "codigo": "VET-2026-012",
        "tipo": "adopcion",
        "ciudadano_nombre": "Ricardo Javier Peña",
        "ciudadano_telefono": "3025550112",
        "descripcion": "Visita de hogar para adopción de felino de colonia urbana.",
        "barrio": "La Pamba",
        "comuna": "Comuna 4",
        "fecha_registro": "2026-09-08 15:18:00",
        "estado_actual": "ASIGNADA",
        "animal_nombre": "Misi",
    },
]

SECUENCIA_HASTA = {
    "RECIBIDA": ["RECIBIDA"],
    "ASIGNADA": ["RECIBIDA", "ASIGNADA"],
    "EN PROCESO": ["RECIBIDA", "ASIGNADA", "EN PROCESO"],
    "ATENDIDA": ["RECIBIDA", "ASIGNADA", "EN PROCESO", "ATENDIDA"],
    "CERRADA": ["RECIBIDA", "ASIGNADA", "EN PROCESO", "ATENDIDA", "CERRADA"],
}

RESPONSABLES = {
    "RECIBIDA": ("Mesa de entrada CBA", "Solicitud ciudadana radicada en el CBA Popayán."),
    "ASIGNADA": ("Auxiliar operativo CBA", "Caso asignado a cuadrilla o médico veterinario."),
    "EN PROCESO": ("MV. Camila Rivas", "Atención clínica y seguimiento en terreno o albergue."),
    "ATENDIDA": ("MV. Camila Rivas", "Procedimiento o servicio completado; pendiente cierre administrativo."),
    "CERRADA": ("Coordinación CBA", "Expediente cerrado y archivado."),
}


def _historial_para(estado_final: str) -> list[tuple[str | None, str, str, str]]:
    secuencia = SECUENCIA_HASTA[estado_final]
    filas = []
    anterior = None
    for estado in secuencia:
        responsable, observaciones = RESPONSABLES[estado]
        filas.append((anterior, estado, responsable, observaciones))
        anterior = estado
    return filas


def seed(conn: sqlite3.Connection, *, reset: bool = True) -> None:
    init_schema(conn)
    if reset:
        conn.execute("DELETE FROM HistorialEstado")
        conn.execute("DELETE FROM Solicitud")
        conn.execute("DELETE FROM Animal")
        conn.commit()

    animal_ids: dict[str, int] = {}
    for nombre, especie, raza, edad, salud, adopcion, fecha in ANIMALES:
        cur = conn.execute(
            """
            INSERT INTO Animal (
                nombre, especie, raza, edad_aproximada, estado_salud,
                disponible_adopcion, fecha_ingreso
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (nombre, especie, raza, edad, salud, adopcion, fecha),
        )
        animal_ids[nombre] = cur.lastrowid

    for item in SOLICITUDES:
        animal_id = animal_ids.get(item["animal_nombre"]) if item["animal_nombre"] else None
        cur = conn.execute(
            """
            INSERT INTO Solicitud (
                codigo, tipo, ciudadano_nombre, ciudadano_telefono, descripcion,
                barrio, comuna, fecha_registro, estado_actual, animal_id
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                item["codigo"],
                item["tipo"],
                item["ciudadano_nombre"],
                item["ciudadano_telefono"],
                item["descripcion"],
                item["barrio"],
                item["comuna"],
                item["fecha_registro"],
                item["estado_actual"],
                animal_id,
            ),
        )
        solicitud_id = cur.lastrowid
        for estado_anterior, estado_nuevo, responsable, observaciones in _historial_para(
            item["estado_actual"]
        ):
            conn.execute(
                """
                INSERT INTO HistorialEstado (
                    solicitud_id, estado_anterior, estado_nuevo,
                    responsable, observaciones
                ) VALUES (?, ?, ?, ?, ?)
                """,
                (solicitud_id, estado_anterior, estado_nuevo, responsable, observaciones),
            )
    conn.commit()


def main() -> None:
    db_path = get_db_path()
    conn = connect(db_path)
    try:
        seed(conn)
        total = conn.execute("SELECT COUNT(*) AS n FROM Solicitud").fetchone()["n"]
        animales = conn.execute("SELECT COUNT(*) AS n FROM Animal").fetchone()["n"]
        historial = conn.execute("SELECT COUNT(*) AS n FROM HistorialEstado").fetchone()["n"]
        print(f"Base sembrada en {db_path}")
        print(f"Animales: {animales} | Solicitudes: {total} | Historial: {historial}")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
