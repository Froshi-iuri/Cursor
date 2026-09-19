# Vetericano — Centro de Bienestar Animal de Popayán

Plataforma para gestionar solicitudes ciudadanas de rescate, adopción, vacunación y esterilización (caninos, felinos y equinos) en las 9 comunas y la zona rural de Popayán.

## Requisitos

- Python 3.11+

## Instalación

```bash
py -m pip install -r requirements.txt
```

## Sembrar la base de datos

```bash
py database/seed_vetericano.py
```

Crea `database/vetericano.db` con animales, solicitudes e historial de auditoría.

## Levantar la API y el panel

Desde la raíz del proyecto:

```bash
py -m uvicorn backend.main:app --reload
```

- Panel administrativo: http://127.0.0.1:8000/
- Documentación OpenAPI: http://127.0.0.1:8000/docs

## Pruebas

```bash
py -m pytest tests/ -v
```

## Flujo de estados

`RECIBIDA` → `ASIGNADA` → `EN PROCESO` → `ATENDIDA` → `CERRADA`

Desde `ASIGNADA` se permite volver a `RECIBIDA` por reasignación justificada. Cada cambio exige responsable, observaciones y queda registrado en `HistorialEstado`.
