PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS Animal (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL,
    especie TEXT NOT NULL CHECK (especie IN ('canino', 'felino', 'equino')),
    raza TEXT NOT NULL,
    edad_aproximada TEXT,
    estado_salud TEXT NOT NULL CHECK (
        estado_salud IN ('Excelente', 'En Tratamiento', 'Crítico', 'Estable', 'Recuperado')
    ),
    disponible_adopcion INTEGER NOT NULL DEFAULT 0 CHECK (disponible_adopcion IN (0, 1)),
    fecha_ingreso TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS Solicitud (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    codigo TEXT UNIQUE NOT NULL,
    tipo TEXT NOT NULL CHECK (tipo IN ('rescate', 'adopcion', 'vacunacion', 'esterilizacion')),
    ciudadano_nombre TEXT NOT NULL,
    ciudadano_telefono TEXT NOT NULL,
    descripcion TEXT NOT NULL,
    barrio TEXT NOT NULL,
    comuna TEXT NOT NULL,
    fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    estado_actual TEXT NOT NULL DEFAULT 'RECIBIDA' CHECK (
        estado_actual IN ('RECIBIDA', 'ASIGNADA', 'EN PROCESO', 'ATENDIDA', 'CERRADA')
    ),
    animal_id INTEGER NULL,
    FOREIGN KEY (animal_id) REFERENCES Animal(id) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS HistorialEstado (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    solicitud_id INTEGER NOT NULL,
    estado_anterior TEXT NULL,
    estado_nuevo TEXT NOT NULL,
    fecha_cambio TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    responsable TEXT NOT NULL,
    observaciones TEXT NOT NULL,
    FOREIGN KEY (solicitud_id) REFERENCES Solicitud(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_solicitud_estado ON Solicitud(estado_actual);
CREATE INDEX IF NOT EXISTS idx_solicitud_comuna ON Solicitud(comuna);
CREATE INDEX IF NOT EXISTS idx_solicitud_tipo ON Solicitud(tipo);
CREATE INDEX IF NOT EXISTS idx_historial_solicitud ON HistorialEstado(solicitud_id);
