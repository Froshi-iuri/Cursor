from database.seed_vetericano import seed
from database.connection import connect


def test_get_solicitudes_lista(client, db_path):
    conn = connect(db_path)
    seed(conn)
    conn.close()

    response = client.get("/api/solicitudes")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1
    assert "codigo" in data[0]


def test_get_solicitudes_filtros_estado_y_comuna(client, db_path):
    conn = connect(db_path)
    seed(conn)
    conn.close()

    por_estado = client.get("/api/solicitudes", params={"estado": "RECIBIDA"})
    assert por_estado.status_code == 200
    assert all(item["estado_actual"] == "RECIBIDA" for item in por_estado.json())

    por_comuna = client.get("/api/solicitudes", params={"comuna": "Comuna 1"})
    assert por_comuna.status_code == 200
    assert all(item["comuna"] == "Comuna 1" for item in por_comuna.json())
    assert len(por_comuna.json()) >= 1


def test_post_solicitud_crea_con_codigo_y_estado_recibida(client, db_path):
    response = client.post(
        "/api/solicitudes",
        json={
            "tipo": "vacunacion",
            "ciudadano_nombre": "Gloria Inés Cobo",
            "ciudadano_telefono": "3124447788",
            "descripcion": "Vacunación en Villa del Viento",
            "barrio": "Villa del Viento",
            "comuna": "Comuna 2",
        },
    )
    assert response.status_code == 201
    body = response.json()
    assert body["estado_actual"] == "RECIBIDA"
    assert body["codigo"].startswith("VET-")
    partes = body["codigo"].split("-")
    assert len(partes) == 3
    assert partes[2].isdigit()


def test_cambiar_estado_valido_invalido_y_404(client, db_path):
    creada = client.post(
        "/api/solicitudes",
        json={
            "tipo": "rescate",
            "ciudadano_nombre": "Pedro Nel",
            "ciudadano_telefono": "3001112233",
            "descripcion": "Felino en Cadillal",
            "barrio": "Cadillal",
            "comuna": "Comuna 3",
        },
    ).json()
    solicitud_id = creada["id"]

    ok = client.post(
        f"/api/solicitudes/{solicitud_id}/cambiar-estado",
        json={
            "estado_nuevo": "ASIGNADA",
            "responsable": "Auxiliar operativo CBA",
            "observaciones": "Cuadrilla asignada a Comuna 3.",
        },
    )
    assert ok.status_code == 200
    assert ok.json()["estado_actual"] == "ASIGNADA"
    assert ok.json()["historial"][-1]["estado_nuevo"] == "ASIGNADA"

    invalida = client.post(
        f"/api/solicitudes/{solicitud_id}/cambiar-estado",
        json={
            "estado_nuevo": "CERRADA",
            "responsable": "Auxiliar operativo CBA",
            "observaciones": "Intento de salto ilegal.",
        },
    )
    assert invalida.status_code == 400
    detail = invalida.json()["detail"]
    assert "Transición inválida" in detail

    missing = client.post(
        "/api/solicitudes/99999/cambiar-estado",
        json={
            "estado_nuevo": "ASIGNADA",
            "responsable": "Auxiliar operativo CBA",
            "observaciones": "No existe.",
        },
    )
    assert missing.status_code == 404


def test_get_kpis_estructura(client, db_path):
    conn = connect(db_path)
    seed(conn)
    conn.close()

    response = client.get("/api/kpis")
    assert response.status_code == 200
    body = response.json()
    assert "total_solicitudes" in body
    assert "por_estado" in body
    assert "por_comuna" in body
    assert body["total_solicitudes"] >= 1
    assert isinstance(body["por_estado"], dict)
    assert isinstance(body["por_comuna"], dict)
