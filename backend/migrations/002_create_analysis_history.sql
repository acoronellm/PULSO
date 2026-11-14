CREATE TABLE IF NOT EXISTS analyses (
    id UUID PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    probability DOUBLE PRECISION NOT NULL CHECK (probability >= 0 AND probability <= 1),
    classification SMALLINT NOT NULL CHECK (classification IN (0, 1)),
    threshold DOUBLE PRECISION NOT NULL CHECK (threshold >= 0 AND threshold <= 1),
    model_version VARCHAR(50) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS ix_analyses_user_created_at
    ON analyses (user_id, created_at DESC, id DESC);
