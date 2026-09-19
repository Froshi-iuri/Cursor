from fastapi import APIRouter, HTTPException, Query

from backend.exceptions import BusinessError, SolicitudNotFoundError
from backend.models import CambiarEstadoIn, SolicitudCreate
from backend.services import solicitud_service

router = APIRouter(prefix="/api/solicitudes", tags=["solicitudes"])


@router.get("")
def listar(
    estado: str | None = Query(default=None),
    tipo: str | None = Query(default=None),
    comuna: str | None = Query(default=None),
):
    return solicitud_service.listar_solicitudes(estado=estado, tipo=tipo, comuna=comuna)


@router.get("/{solicitud_id}")
def detalle(solicitud_id: int):
    try:
        return solicitud_service.obtener_solicitud(solicitud_id)
    except SolicitudNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.post("", status_code=201)
def crear(payload: SolicitudCreate):
    return solicitud_service.crear_solicitud(payload)


@router.post("/{solicitud_id}/cambiar-estado")
def cambiar_estado(solicitud_id: int, payload: CambiarEstadoIn):
    try:
        return solicitud_service.cambiar_estado(solicitud_id, payload)
    except SolicitudNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except BusinessError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
