from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field

Especie = Literal["canino", "felino", "equino"]
TipoSolicitud = Literal["rescate", "adopcion", "vacunacion", "esterilizacion"]
EstadoSolicitud = Literal["RECIBIDA", "ASIGNADA", "EN PROCESO", "ATENDIDA", "CERRADA"]
EstadoSalud = Literal["Excelente", "En Tratamiento", "Crítico", "Estable", "Recuperado"]


class AnimalOut(BaseModel):
    id: int
    nombre: str
    especie: Especie
    raza: str
    edad_aproximada: str | None = None
    estado_salud: EstadoSalud
    disponible_adopcion: bool
    fecha_ingreso: str | None = None


class HistorialOut(BaseModel):
    id: int
    solicitud_id: int
    estado_anterior: str | None = None
    estado_nuevo: str
    fecha_cambio: str
    responsable: str
    observaciones: str


class SolicitudOut(BaseModel):
    id: int
    codigo: str
    tipo: TipoSolicitud
    ciudadano_nombre: str
    ciudadano_telefono: str
    descripcion: str
    barrio: str
    comuna: str
    fecha_registro: str
    estado_actual: EstadoSolicitud
    animal_id: int | None = None
    animal: AnimalOut | None = None


class SolicitudDetalleOut(SolicitudOut):
    historial: list[HistorialOut] = Field(default_factory=list)


class SolicitudCreate(BaseModel):
    tipo: TipoSolicitud
    ciudadano_nombre: str = Field(min_length=1)
    ciudadano_telefono: str = Field(min_length=7)
    descripcion: str = Field(min_length=1)
    barrio: str = Field(min_length=1)
    comuna: str = Field(min_length=1)
    animal_id: int | None = None


class CambiarEstadoIn(BaseModel):
    estado_nuevo: EstadoSolicitud
    responsable: str = Field(min_length=1)
    observaciones: str = Field(min_length=1)


class KPIsOut(BaseModel):
    total_solicitudes: int
    abiertas: int
    atendidas: int
    tasa_resolucion: float
    por_estado: dict[str, int]
    por_comuna: dict[str, int]
