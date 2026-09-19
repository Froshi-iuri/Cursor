const API_BASE = `${window.location.origin}/api`;

async function request(path, options = {}) {
  const response = await fetch(`${API_BASE}${path}`, {
    headers: {
      "Content-Type": "application/json",
      ...(options.headers || {}),
    },
    ...options,
  });
  const payload = await response.json().catch(() => ({}));
  if (!response.ok) {
    const detail = payload.detail || payload.message || `Error HTTP ${response.status}`;
    const error = new Error(typeof detail === "string" ? detail : JSON.stringify(detail));
    error.status = response.status;
    error.payload = payload;
    throw error;
  }
  return payload;
}

export async function fetchSolicitudes(filters = {}) {
  const params = new URLSearchParams();
  Object.entries(filters).forEach(([key, value]) => {
    if (value) params.set(key, value);
  });
  const qs = params.toString();
  return request(`/solicitudes${qs ? `?${qs}` : ""}`);
}

export async function fetchSolicitudDetalle(id) {
  return request(`/solicitudes/${id}`);
}

export async function cambiarEstadoSolicitud(id, body) {
  return request(`/solicitudes/${id}/cambiar-estado`, {
    method: "POST",
    body: JSON.stringify(body),
  });
}

export async function crearSolicitud(body) {
  return request("/solicitudes", {
    method: "POST",
    body: JSON.stringify(body),
  });
}

export async function fetchKPIs() {
  return request("/kpis");
}

export async function fetchAnimales(disponibleAdopcion) {
  const qs =
    disponibleAdopcion === undefined || disponibleAdopcion === ""
      ? ""
      : `?disponible_adopcion=${disponibleAdopcion}`;
  return request(`/animales${qs}`);
}
