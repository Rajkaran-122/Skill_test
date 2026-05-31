-- ============================================================
-- Store Intelligence Platform — Database Initialization
-- ============================================================
-- This script runs on first container start.
-- It creates extensions, tables, hypertables, indexes,
-- continuous aggregates, retention policies, and compression.
-- ============================================================

-- Enable extensions
CREATE EXTENSION IF NOT EXISTS timescaledb;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ===========================
-- STORES
-- ===========================
CREATE TABLE IF NOT EXISTS stores (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    store_code  VARCHAR(20) UNIQUE NOT NULL,
    name        VARCHAR(255) NOT NULL,
    address     TEXT,
    city        VARCHAR(100),
    region      VARCHAR(100),
    timezone    VARCHAR(50) DEFAULT 'UTC',
    latitude    DECIMAL(10, 8),
    longitude   DECIMAL(11, 8),
    is_active   BOOLEAN DEFAULT TRUE,
    created_at  TIMESTAMPTZ DEFAULT NOW(),
    updated_at  TIMESTAMPTZ DEFAULT NOW()
);

-- ===========================
-- CAMERAS
-- ===========================
CREATE TABLE IF NOT EXISTS cameras (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    store_id    UUID REFERENCES stores(id) ON DELETE CASCADE,
    camera_code VARCHAR(20) NOT NULL,
    name        VARCHAR(255),
    location    VARCHAR(255),
    stream_url  VARCHAR(500),
    resolution  VARCHAR(20),
    fps         INT DEFAULT 30,
    is_active   BOOLEAN DEFAULT TRUE,
    created_at  TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(store_id, camera_code)
);

-- ===========================
-- ZONES
-- ===========================
CREATE TABLE IF NOT EXISTS zones (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    store_id    UUID REFERENCES stores(id) ON DELETE CASCADE,
    zone_code   VARCHAR(50) NOT NULL,
    name        VARCHAR(255) NOT NULL,
    zone_type   VARCHAR(50) NOT NULL,
    polygon     JSONB,
    camera_ids  UUID[],
    is_active   BOOLEAN DEFAULT TRUE,
    created_at  TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(store_id, zone_code)
);

-- ===========================
-- EVENTS (Hypertable)
-- ===========================
CREATE TABLE IF NOT EXISTS events (
    id          UUID DEFAULT gen_random_uuid(),
    event_id    VARCHAR(50) NOT NULL,
    store_id    UUID NOT NULL,
    camera_id   UUID,
    visitor_id  VARCHAR(50) NOT NULL,
    event_type  VARCHAR(30) NOT NULL,
    zone_id     UUID,
    confidence  DECIMAL(4, 3),
    metadata    JSONB DEFAULT '{}',
    timestamp   TIMESTAMPTZ NOT NULL,
    created_at  TIMESTAMPTZ DEFAULT NOW(),
    PRIMARY KEY (id, timestamp)
);

SELECT create_hypertable('events', 'timestamp',
    chunk_time_interval => INTERVAL '7 days',
    if_not_exists => TRUE
);

CREATE INDEX IF NOT EXISTS idx_events_store_time ON events (store_id, timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_events_visitor ON events (visitor_id, timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_events_type ON events (event_type, timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_events_zone ON events (zone_id, timestamp DESC);

-- ===========================
-- SESSIONS (Visitor Journey)
-- ===========================
CREATE TABLE IF NOT EXISTS sessions (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    store_id        UUID NOT NULL,
    visitor_id      VARCHAR(50) NOT NULL,
    session_start   TIMESTAMPTZ NOT NULL,
    session_end     TIMESTAMPTZ,
    duration_seconds INT,
    zones_visited   JSONB DEFAULT '[]',
    is_staff        BOOLEAN DEFAULT FALSE,
    is_converted    BOOLEAN DEFAULT FALSE,
    entry_camera    UUID,
    exit_camera     UUID,
    created_at      TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_sessions_store_time ON sessions (store_id, session_start DESC);
CREATE INDEX IF NOT EXISTS idx_sessions_visitor ON sessions (visitor_id, session_start DESC);

-- ===========================
-- TRANSACTIONS (POS Data)
-- ===========================
CREATE TABLE IF NOT EXISTS transactions (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    store_id        UUID NOT NULL,
    transaction_id  VARCHAR(50) UNIQUE NOT NULL,
    amount          DECIMAL(12, 2),
    items_count     INT,
    payment_method  VARCHAR(30),
    visitor_id      VARCHAR(50),
    timestamp       TIMESTAMPTZ NOT NULL,
    created_at      TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_transactions_store_time ON transactions (store_id, timestamp DESC);

-- ===========================
-- ANOMALIES (Hypertable)
-- ===========================
CREATE TABLE IF NOT EXISTS anomalies (
    id              UUID DEFAULT gen_random_uuid(),
    store_id        UUID NOT NULL,
    anomaly_type    VARCHAR(50) NOT NULL,
    severity        VARCHAR(20) NOT NULL,
    description     TEXT,
    metadata        JSONB DEFAULT '{}',
    is_resolved     BOOLEAN DEFAULT FALSE,
    resolved_at     TIMESTAMPTZ,
    detected_at     TIMESTAMPTZ NOT NULL,
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    PRIMARY KEY (id, detected_at)
);

SELECT create_hypertable('anomalies', 'detected_at',
    chunk_time_interval => INTERVAL '30 days',
    if_not_exists => TRUE
);

CREATE INDEX IF NOT EXISTS idx_anomalies_store ON anomalies (store_id, detected_at DESC);
CREATE INDEX IF NOT EXISTS idx_anomalies_type ON anomalies (anomaly_type, detected_at DESC);
CREATE INDEX IF NOT EXISTS idx_anomalies_unresolved ON anomalies (store_id, is_resolved, detected_at DESC);

-- ===========================
-- AUDIT LOGS (Hypertable)
-- ===========================
CREATE TABLE IF NOT EXISTS audit_logs (
    id          UUID DEFAULT gen_random_uuid(),
    user_id     UUID,
    action      VARCHAR(100) NOT NULL,
    resource    VARCHAR(100),
    details     JSONB DEFAULT '{}',
    ip_address  INET,
    timestamp   TIMESTAMPTZ DEFAULT NOW(),
    PRIMARY KEY (id, timestamp)
);

SELECT create_hypertable('audit_logs', 'timestamp',
    chunk_time_interval => INTERVAL '30 days',
    if_not_exists => TRUE
);

-- ===========================
-- CONTINUOUS AGGREGATES
-- ===========================

-- Hourly visitor metrics
CREATE MATERIALIZED VIEW IF NOT EXISTS hourly_metrics
WITH (timescaledb.continuous) AS
SELECT
    time_bucket('1 hour', timestamp) AS bucket,
    store_id,
    COUNT(DISTINCT visitor_id) FILTER (WHERE event_type = 'VISITOR_ENTER') AS visitor_count,
    COUNT(DISTINCT visitor_id) FILTER (WHERE event_type = 'PURCHASE') AS purchase_count,
    AVG(confidence) AS avg_confidence,
    COUNT(*) AS total_events
FROM events
GROUP BY bucket, store_id
WITH NO DATA;

SELECT add_continuous_aggregate_policy('hourly_metrics',
    start_offset    => INTERVAL '2 hours',
    end_offset      => INTERVAL '15 minutes',
    schedule_interval => INTERVAL '15 minutes',
    if_not_exists   => TRUE
);

-- Daily zone metrics
CREATE MATERIALIZED VIEW IF NOT EXISTS daily_zone_metrics
WITH (timescaledb.continuous) AS
SELECT
    time_bucket('1 day', timestamp) AS bucket,
    store_id,
    zone_id,
    COUNT(DISTINCT visitor_id) AS unique_visitors,
    COUNT(*) FILTER (WHERE event_type = 'ZONE_ENTER') AS entries,
    COUNT(*) FILTER (WHERE event_type = 'ZONE_EXIT') AS exits,
    COUNT(*) AS total_events
FROM events
WHERE zone_id IS NOT NULL
GROUP BY bucket, store_id, zone_id
WITH NO DATA;

SELECT add_continuous_aggregate_policy('daily_zone_metrics',
    start_offset    => INTERVAL '3 days',
    end_offset      => INTERVAL '1 hour',
    schedule_interval => INTERVAL '1 hour',
    if_not_exists   => TRUE
);

-- ===========================
-- RETENTION & COMPRESSION
-- ===========================

-- Retain raw events for 30 days
SELECT add_retention_policy('events', INTERVAL '30 days', if_not_exists => TRUE);

-- Retain anomalies for 365 days
SELECT add_retention_policy('anomalies', INTERVAL '365 days', if_not_exists => TRUE);

-- Retain audit logs for 365 days
SELECT add_retention_policy('audit_logs', INTERVAL '365 days', if_not_exists => TRUE);

-- Compress events older than 7 days
ALTER TABLE events SET (
    timescaledb.compress,
    timescaledb.compress_segmentby = 'store_id',
    timescaledb.compress_orderby = 'timestamp DESC'
);

SELECT add_compression_policy('events', INTERVAL '7 days', if_not_exists => TRUE);

-- ===========================
-- HELPER FUNCTIONS
-- ===========================

-- Function to update 'updated_at' timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger for stores
CREATE TRIGGER update_stores_updated_at
    BEFORE UPDATE ON stores
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- ============================================================
-- Schema initialization complete
-- ============================================================
