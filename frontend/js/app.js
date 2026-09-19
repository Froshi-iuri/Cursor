import {
  cambiarEstadoSolicitud,
  crearSolicitud,
  fetchAnimales,
  fetchKPIs,
  fetchSolicitudDetalle,
  fetchSolicitudes,
} from "./api.js";

const TRANSICIONES = {
  RECIBIDA: ["ASIGNADA"],
  ASIGNADA: ["EN PROCESO", "RECIBIDA"],
  "EN PROCESO": ["ATENDIDA"],
  ATENDIDA: ["CERRADA"],
  CERRADA: [],
};

const ICONOS_TIPO = {
  rescate: "🆘",
  adopcion: "🏠",
  vacunacion: "💉",
  esterilizacion: "🩺",
};

const els = {
  kpis: document.getElementById("kpis"),
  tbody: document.getElementById("solicitudes-body"),
  filtroEstado: document.getElementById("filtro-estado"),
  filtroTipo: document.getElementById("filtro-tipo"),
  filtroComuna: document.getElementById("filtro-comuna"),
  btnFiltrar: document.getElementById("btn-filtrar"),
  btnLimpiar: document.getElementById("btn-limpiar"),
  btnNueva: document.getElementById("btn-nueva"),
  toasts: document.getElementById("toasts"),
  modalEstado: document.getElementById("modal-estado"),
  modalExpediente: document.getElementById("modal-expediente"),
  modalNueva: document.getElementById("modal-nueva"),
  formEstado: document.getElementById("form-estado"),
  formNueva: document.getElementById("form-nueva"),
  estadoActual: document.getElementById("estado-actual"),
  estadoNuevo: document.getElementById("estado-nuevo"),
  expediente: document.getElementById("expediente"),
  animalSelect: document.getElementById("animal-id"),
};

let solicitudEstadoId = null;

function toast(message, type = "ok") {
  const node = document.createElement("div");
  node.className = `toast ${type === "error" ? "error" : ""}`;
  node.textContent = message;
  els.toasts.appendChild(node);
  setTimeout(() => node.remove(), 4200);
}

function badgeClass(estado) {
  return estado.replaceAll(" ", "");
}

function openModal(modal) {
  modal.classList.add("open");
}

function closeModal(modal) {
  modal.classList.remove("open");
}

document.querySelectorAll("[data-close]").forEach((btn) => {
  btn.addEventListener("click", () => closeModal(btn.closest(".modal-backdrop")));
});

document.querySelectorAll(".modal-backdrop").forEach((backdrop) => {
  backdrop.addEventListener("click", (event) => {
    if (event.target === backdrop) closeModal(backdrop);
  });
});

function renderKPIs(data) {
  const cards = [
    ["Total solicitudes", data.total_solicitudes],
    ["Abiertas", data.abiertas],
    ["Atendidas", data.atendidas],
    ["Tasa de resolución", `${data.tasa_resolucion}%`],
  ];
  els.kpis.innerHTML = cards
    .map(
      ([label, value]) => `
      <article class="kpi">
        <span>${label}</span>
        <strong>${value}</strong>
      </article>`
    )
    .join("");
}

function renderTabla(solicitudes) {
  if (!solicitudes.length) {
    els.tbody.innerHTML = `<tr><td class="empty" colspan="6">No hay solicitudes con los filtros actuales.</td></tr>`;
    return;
  }
  els.tbody.innerHTML = solicitudes
    .map((s) => {
      const animal = s.animal ? ` · ${s.animal.nombre}` : "";
      return `
        <tr>
          <td><strong>${s.codigo}</strong></td>
          <td>${ICONOS_TIPO[s.tipo] || ""} ${s.tipo}${animal}</td>
          <td>${s.ciudadano_nombre}<br><small>${s.ciudadano_telefono}</small></td>
          <td>${s.comuna}<br><small>${s.barrio}</small></td>
          <td><span class="badge ${badgeClass(s.estado_actual)}">${s.estado_actual}</span></td>
          <td class="actions">
            <button class="btn small" data-estado="${s.id}">Gestionar estado</button>
            <button class="btn small secondary" data-exp="${s.id}">Expediente</button>
          </td>
        </tr>`;
    })
    .join("");
}

function filtrosActuales() {
  return {
    estado: els.filtroEstado.value,
    tipo: els.filtroTipo.value,
    comuna: els.filtroComuna.value,
  };
}

async function refrescar() {
  const [solicitudes, kpis] = await Promise.all([
    fetchSolicitudes(filtrosActuales()),
    fetchKPIs(),
  ]);
  renderTabla(solicitudes);
  renderKPIs(kpis);
}

els.tbody.addEventListener("click", async (event) => {
  const estadoId = event.target.dataset.estado;
  const expId = event.target.dataset.exp;
  try {
    if (estadoId) {
      const detalle = await fetchSolicitudDetalle(estadoId);
      solicitudEstadoId = Number(estadoId);
      els.estadoActual.textContent = detalle.estado_actual;
      const opciones = TRANSICIONES[detalle.estado_actual] || [];
      els.estadoNuevo.innerHTML = opciones.length
        ? opciones.map((op, i) => `<option value="${op}" ${i === 0 ? "selected" : ""}>${op}</option>`).join("")
        : `<option value="">Sin transiciones (estado terminal)</option>`;
      els.formEstado.responsable.value = "";
      els.formEstado.observaciones.value = "";
      els.formEstado.querySelector("button[type=submit]").disabled = opciones.length === 0;
      openModal(els.modalEstado);
    }
    if (expId) {
      const detalle = await fetchSolicitudDetalle(expId);
      els.expediente.innerHTML = `
        <p><strong>${detalle.codigo}</strong> · ${detalle.tipo} · ${detalle.ciudadano_nombre}</p>
        <p>${detalle.descripcion}</p>
        <div class="timeline">
          ${(detalle.historial || [])
            .map(
              (h) => `
            <div class="timeline-item">
              <strong>${h.estado_anterior || "Inicio"} → ${h.estado_nuevo}</strong>
              <small>${h.fecha_cambio} · ${h.responsable}</small>
              <p>${h.observaciones}</p>
            </div>`
            )
            .join("")}
        </div>`;
      openModal(els.modalExpediente);
    }
  } catch (error) {
    toast(error.message, "error");
  }
});

els.formEstado.addEventListener("submit", async (event) => {
  event.preventDefault();
  if (!solicitudEstadoId) return;
  const data = Object.fromEntries(new FormData(els.formEstado));
  try {
    await cambiarEstadoSolicitud(solicitudEstadoId, data);
    closeModal(els.modalEstado);
    toast("Estado actualizado y auditado.");
    await refrescar();
  } catch (error) {
    toast(error.message, "error");
  }
});

els.formNueva.addEventListener("submit", async (event) => {
  event.preventDefault();
  const data = Object.fromEntries(new FormData(els.formNueva));
  if (!data.animal_id) delete data.animal_id;
  else data.animal_id = Number(data.animal_id);
  try {
    const creada = await crearSolicitud(data);
    closeModal(els.modalNueva);
    els.formNueva.reset();
    toast(`Solicitud ${creada.codigo} registrada.`);
    await refrescar();
  } catch (error) {
    toast(error.message, "error");
  }
});

els.btnFiltrar.addEventListener("click", () => refrescar().catch((e) => toast(e.message, "error")));
els.btnLimpiar.addEventListener("click", () => {
  els.filtroEstado.value = "";
  els.filtroTipo.value = "";
  els.filtroComuna.value = "";
  refrescar().catch((e) => toast(e.message, "error"));
});

els.btnNueva.addEventListener("click", async () => {
  try {
    const animales = await fetchAnimales();
    els.animalSelect.innerHTML =
      `<option value="">Sin animal asociado</option>` +
      animales
        .map((a) => `<option value="${a.id}">${a.nombre} (${a.especie})</option>`)
        .join("");
    openModal(els.modalNueva);
  } catch (error) {
    toast(error.message, "error");
  }
});

refrescar().catch((error) => toast(error.message, "error"));
