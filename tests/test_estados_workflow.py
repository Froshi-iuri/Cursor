import pytest

from backend.exceptions import AuditRequiredError, InvalidStateTransitionError
from backend.models import CambiarEstadoIn, SolicitudCreate
from backend.services import solicitud_service
from database.connection import get_db


def _crear_solicitud():
    return solicitud_service.crear_solicitud(
        SolicitudCreate(
            tipo="rescate",
            ciudadano_nombre="Ana Lucía Quintero",
            ciudadano_telefono="3105559999",
            descripcion="Canino herido en Bello Horizonte",
            barrio="Bello Horizonte",
            comuna="Comuna 2",
        )
    )


def _cambio(estado: str, responsable="MV. Prueba", observaciones="Avance justificado"):
    return CambiarEstadoIn.model_construct(
        estado_nuevo=estado,
        responsable=responsable,
        observaciones=observaciones,
    )


def test_flujo_feliz_completo_con_historial(db_path):
    creada = _crear_solicitud()
    solicitud_id = creada["id"]
    assert creada["estado_actual"] == "RECIBIDA"
    assert creada["historial"][0]["estado_anterior"] is None
    assert creada["historial"][0]["estado_nuevo"] == "RECIBIDA"

    secuencia = ["ASIGNADA", "EN PROCESO", "ATENDIDA", "CERRADA"]
    for estado in secuencia:
        actual = solicitud_service.cambiar_estado(solicitud_id, _cambio(estado))
        assert actual["estado_actual"] == estado
        assert actual["historial"][-1]["estado_nuevo"] == estado
        assert actual["historial"][-1]["responsable"] == "MV. Prueba"

    with get_db() as conn:
        n = conn.execute(
            "SELECT COUNT(*) AS n FROM HistorialEstado WHERE solicitud_id = ?",
            (solicitud_id,),
        ).fetchone()["n"]
    assert n == 5


@pytest.mark.parametrize(
    "origen,destino",
    [
        ("RECIBIDA", "ATENDIDA"),
        ("RECIBIDA", "CERRADA"),
        ("ASIGNADA", "CERRADA"),
    ],
)
def test_rechaza_saltos_ilegales_sin_alterar_estado(db_path, origen, destino):
    creada = _crear_solicitud()
    solicitud_id = creada["id"]
    if origen == "ASIGNADA":
        solicitud_service.cambiar_estado(solicitud_id, _cambio("ASIGNADA"))

    with pytest.raises(InvalidStateTransitionError):
        solicitud_service.cambiar_estado(solicitud_id, _cambio(destino))

    actual = solicitud_service.obtener_solicitud(solicitud_id)
    assert actual["estado_actual"] == origen


def test_estado_cerrada_es_terminal(db_path):
    creada = _crear_solicitud()
    solicitud_id = creada["id"]
    for estado in ["ASIGNADA", "EN PROCESO", "ATENDIDA", "CERRADA"]:
        solicitud_service.cambiar_estado(solicitud_id, _cambio(estado))

    with pytest.raises(InvalidStateTransitionError):
        solicitud_service.cambiar_estado(solicitud_id, _cambio("RECIBIDA"))

    assert solicitud_service.obtener_solicitud(solicitud_id)["estado_actual"] == "CERRADA"


def test_auditoria_exige_responsable_y_observaciones(db_path):
    creada = _crear_solicitud()
    solicitud_id = creada["id"]

    with pytest.raises(AuditRequiredError):
        solicitud_service.cambiar_estado(solicitud_id, _cambio("ASIGNADA", responsable="  "))

    with pytest.raises(AuditRequiredError):
        solicitud_service.cambiar_estado(
            solicitud_id, _cambio("ASIGNADA", observaciones="")
        )

    actual = solicitud_service.obtener_solicitud(solicitud_id)
    assert actual["estado_actual"] == "RECIBIDA"
    assert len(actual["historial"]) == 1


def test_reasignacion_asignada_a_recibida(db_path):
    creada = _crear_solicitud()
    solicitud_id = creada["id"]
    solicitud_service.cambiar_estado(solicitud_id, _cambio("ASIGNADA"))
    actual = solicitud_service.cambiar_estado(
        solicitud_id,
        _cambio("RECIBIDA", observaciones="Reasignación justificada por cuadrilla incompleta."),
    )
    assert actual["estado_actual"] == "RECIBIDA"
