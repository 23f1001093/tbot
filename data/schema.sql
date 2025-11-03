-- Database schema for calls.db
-- SQLite database for storing call history and transcripts

-- Calls table
CREATE TABLE IF NOT EXISTS calls (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    call_id INTEGER UNIQUE NOT NULL,
    user_id INTEGER,
    phone_number TEXT,
    start_time TIMESTAMP NOT NULL,
    end_time TIMESTAMP,
    duration_seconds INTEGER,
    status TEXT CHECK(status IN ('pending', 'active', 'completed', 'failed', 'missed')),
    direction TEXT CHECK(direction IN ('incoming', 'outgoing')),
    recording_path TEXT,
    transcript_path TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Messages table
CREATE TABLE IF NOT EXISTS messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    call_id INTEGER NOT NULL,
    role TEXT CHECK(role IN ('user', 'assistant', 'system')),
    content TEXT NOT NULL,
    timestamp TIMESTAMP NOT NULL,
    confidence REAL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (call_id) REFERENCES calls (call_id) ON DELETE CASCADE
);

-- Call metadata table
CREATE TABLE IF NOT EXISTS call_metadata (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    call_id INTEGER NOT NULL,
    key TEXT NOT NULL,
    value TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (call_id) REFERENCES calls (call_id) ON DELETE CASCADE,
    UNIQUE(call_id, key)
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_calls_user_id ON calls(user_id);
CREATE INDEX IF NOT EXISTS idx_calls_status ON calls(status);
CREATE INDEX IF NOT EXISTS idx_calls_start_time ON calls(start_time);
CREATE INDEX IF NOT EXISTS idx_messages_call_id ON messages(call_id);
CREATE INDEX IF NOT EXISTS idx_messages_timestamp ON messages(timestamp);

-- Triggers for updated_at
CREATE TRIGGER IF NOT EXISTS update_calls_timestamp 
AFTER UPDATE ON calls
BEGIN
    UPDATE calls SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;