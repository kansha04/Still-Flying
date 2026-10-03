DROP TABLE IF EXISTS status_events, airframes, operators, aircraft_types;

CREATE TABLE aircraft_types (
    id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    
    manufacturer TEXT NOT NULL,
    model TEXT NOT NULL,
    variant TEXT,
    icao_type_code TEXT
);

CREATE TABLE operators (
    id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    name TEXT NOT NULL,
    country TEXT NOT NULL,
    icao_code TEXT,
    iata_code TEXT
);

CREATE TABLE airframes (
    id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    type_id INTEGER NOT NULL,
    operator_id INTEGER NOT NULL,

    registration TEXT,
    icao24_hex VARCHAR(6),
    serial_number TEXT,
    built_date DATE,

    CONSTRAINT fk_airframe_type
        FOREIGN KEY (type_id)
        REFERENCES aircraft_types(id),

    CONSTRAINT fk_airframe_operator
        FOREIGN KEY (operator_id)
        REFERENCES operators(id)

);

CREATE TABLE status_events (
    id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    airframe_id INTEGER NOT NULL,
    status TEXT NOT NULL,
    occured_at TIMESTAMPTZ,
    source TEXT NOT NULL,
    notes TEXT,

    CONSTRAINT fk_status_airframe
        FOREIGN KEY (airframe_id)
            REFERENCES airframes(id)
            ON DELETE CASCADE
);

CREATE INDEX idx_airframes_icao24_hex ON airframes(icao24_hex);
CREATE INDEX idx_airframes_registration ON airframes(registration);
CREATE INDEX idx_airframes_type_id ON airframes(type_id);