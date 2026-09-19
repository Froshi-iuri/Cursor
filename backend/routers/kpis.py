from fastapi import APIRouter

from backend.services import kpi_service

router = APIRouter(prefix="/api/kpis", tags=["kpis"])


@router.get("")
def kpis():
    return kpi_service.obtener_kpis()
