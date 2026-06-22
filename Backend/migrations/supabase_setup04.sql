-- Audit logging table for compliance & debugging
CREATE TABLE IF NOT EXISTS audit_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    electricity_id TEXT REFERENCES users(electricity_id),
    endpoint TEXT NOT NULL,
    method TEXT NOT NULL,
    sql_used TEXT,
    latency_ms NUMERIC,
    status_code INTEGER,
    user_agent TEXT,
    ip_address TEXT,
    logged_at TIMESTAMPTZ DEFAULT NOW()
);

-- Index for querying by user
CREATE INDEX idx_audit_logs_electricity ON audit_logs(electricity_id, logged_at);

-- RLS policy
ALTER TABLE audit_logs ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Backend only" ON audit_logs FOR ALL USING (true);