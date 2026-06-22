-- Enable pgvector for long-term memory embeddings
CREATE EXTENSION IF NOT EXISTS vector;

-- Chat Sessions (medium-term memory)
CREATE TABLE IF NOT EXISTS chat_sessions (
  session_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  electricity_id TEXT REFERENCES users(electricity_id) ON DELETE CASCADE,
  title TEXT,
  started_at TIMESTAMPTZ DEFAULT NOW(),
  ended_at TIMESTAMPTZ,
  is_active BOOLEAN DEFAULT true
);

-- Chat Messages (normalized for pagination)
CREATE TABLE IF NOT EXISTS chat_messages (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  session_id UUID REFERENCES chat_sessions(session_id) ON DELETE CASCADE,
  role TEXT CHECK (role IN ('user', 'assistant')),
  content TEXT NOT NULL,
  metadata JSONB DEFAULT '{}', -- store tool calls, confidence, etc.
  timestamp TIMESTAMPTZ DEFAULT NOW()
);

-- User Preferences (long-term memory)
CREATE TABLE IF NOT EXISTS user_preferences (
  electricity_id TEXT PRIMARY KEY REFERENCES users(electricity_id) ON DELETE CASCADE,
  preferred_language TEXT DEFAULT 'en',
  response_detail_level TEXT DEFAULT 'concise' CHECK (response_detail_level IN ('concise', 'detailed')),
  common_queries JSONB DEFAULT '[]',
  preference_vec vector(1536), -- for semantic similarity
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX idx_chat_sessions_electricity ON chat_sessions(electricity_id, is_active);
CREATE INDEX idx_chat_messages_session ON chat_messages(session_id, timestamp);
CREATE INDEX IF NOT EXISTS idx_user_preferences_vec 
  ON user_preferences USING hnsw (preference_vec vector_cosine_ops)
  WITH (m = 16, ef_construction = 64);

-- RLS Policies (restrict access to own data)
ALTER TABLE chat_sessions ENABLE ROW LEVEL SECURITY;
ALTER TABLE chat_messages ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_preferences ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can manage own chat sessions" ON chat_sessions
  FOR ALL USING (electricity_id = current_setting('app.current_electricity_id', true));

CREATE POLICY "Users can manage own chat messages" ON chat_messages
  FOR ALL USING (
    session_id IN (
      SELECT session_id FROM chat_sessions WHERE electricity_id = current_setting('app.current_electricity_id', true)
    )
  );

CREATE POLICY "Users can manage own preferences" ON user_preferences
  FOR ALL USING (electricity_id = current_setting('app.current_electricity_id', true));