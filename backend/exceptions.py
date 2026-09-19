class BusinessError(Exception):
    """Error de negocio traducido a HTTP 400."""


class InvalidStateTransitionError(BusinessError):
    def __init__(self, estado_actual: str, estado_nuevo: str, validos: list[str]):
        self.estado_actual = estado_actual
        self.estado_nuevo = estado_nuevo
        self.validos = validos
        permitidos = ", ".join(validos) if validos else "ninguna (estado terminal)"
        super().__init__(
            f"Transición inválida de {estado_actual} a {estado_nuevo}. "
            f"Transiciones permitidas: {permitidos}."
        )


class AuditRequiredError(BusinessError):
    def __init__(self, campo: str):
        self.campo = campo
        super().__init__(f"El campo '{campo}' es obligatorio para auditar el cambio de estado.")


class SolicitudNotFoundError(Exception):
    def __init__(self, solicitud_id: int):
        self.solicitud_id = solicitud_id
        super().__init__(f"Solicitud {solicitud_id} no encontrada.")
