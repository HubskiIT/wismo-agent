-- =============================================================================
-- WISMO Agent. Inicjalizacja bazy danych.
-- Uruchamiane raz przy pierwszym starcie kontenera postgres.
-- =============================================================================

-- Tabela audit log rozmów z agentem
CREATE TABLE IF NOT EXISTS agent_conversations (
    id           BIGSERIAL PRIMARY KEY,
    session_id   VARCHAR(64) NOT NULL,
    channel      VARCHAR(16) NOT NULL,
    user_msg     TEXT,
    agent_msg    TEXT,
    tools_used   JSONB,
    latency_ms   INTEGER,
    tokens_in    INTEGER,
    tokens_out   INTEGER,
    cost_usd     NUMERIC(10, 6),
    guardrails   JSONB,
    order_id     VARCHAR(64),
    created_at   TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_conv_session ON agent_conversations (session_id);
CREATE INDEX IF NOT EXISTS idx_conv_created ON agent_conversations (created_at DESC);
CREATE INDEX IF NOT EXISTS idx_conv_channel ON agent_conversations (channel);
CREATE INDEX IF NOT EXISTS idx_conv_order   ON agent_conversations (order_id) WHERE order_id IS NOT NULL;

-- Tabela eskalacji do konsultanta
CREATE TABLE IF NOT EXISTS escalations (
    id             BIGSERIAL PRIMARY KEY,
    escalation_id  VARCHAR(64) UNIQUE NOT NULL,
    session_id     VARCHAR(64) NOT NULL,
    priority       VARCHAR(8) NOT NULL CHECK (priority IN ('Low', 'Medium', 'High')),
    reason_code    VARCHAR(64) NOT NULL,
    payload        JSONB NOT NULL,
    resolved_at    TIMESTAMPTZ,
    resolved_by    VARCHAR(128),
    created_at     TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_esc_priority ON escalations (priority);
CREATE INDEX IF NOT EXISTS idx_esc_reason ON escalations (reason_code);
CREATE INDEX IF NOT EXISTS idx_esc_unresolved ON escalations (created_at) WHERE resolved_at IS NULL;

-- Widok metryk deflekcji (do Grafany)
CREATE OR REPLACE VIEW v_metrics_daily AS
SELECT
    DATE(created_at) AS day,
    channel,
    COUNT(*) AS total_sessions,
    COUNT(*) FILTER (WHERE guardrails->>'escalated' = 'true') AS escalated,
    (COUNT(*) - COUNT(*) FILTER (WHERE guardrails->>'escalated' = 'true'))::float / NULLIF(COUNT(*), 0) AS deflection_rate,
    AVG(latency_ms)::integer AS avg_latency_ms,
    SUM(cost_usd) AS total_cost_usd
FROM agent_conversations
GROUP BY DATE(created_at), channel
ORDER BY day DESC;
