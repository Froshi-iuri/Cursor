from fastapi import APIRouter, Query

from backend.services import animal_service

router = APIRouter(prefix="/api/animales", tags=["animales"])


@router.get("")
def listar(disponible_adopcion: bool | None = Query(default=None)):
    return animal_service.listar_animales(disponible_adopcion=disponible_adopcion)
