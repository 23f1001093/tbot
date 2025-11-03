#!/bin/bash

# Initialize data directories

echo "Creating data directories..."

# Create all required directories
mkdir -p recordings
mkdir -p transcripts
mkdir -p temp
mkdir -p sessions
mkdir -p conversations
mkdir -p exports

# Create README files for each directory
cat > recordings/README.md << 'EOF'
# Call Recordings

This directory contains audio recordings of calls.

Format: `call_[CALL_ID]_[TIMESTAMP].opus`

Note: Recordings are automatically deleted after 30 days unless configured otherwise.
EOF

cat > transcripts/README.md << 'EOF'
# Call Transcripts

This directory contains JSON transcripts of calls.

Format: `transcript_[CALL_ID]_[TIMESTAMP].json`

Structure:
```json
{
    "call_id": 12345,
    "start_time": "2025-01-01T10:00:00Z",
    "messages": [...],
    "summary": "..."
}
```
EOF

cat > temp/README.md << 'EOF'
# Temporary Files

This directory contains temporary audio processing files.

Files are automatically cleaned up after processing.
EOF

# Initialize database
if [ ! -f "calls.db" ]; then
    echo "Initializing database..."
    sqlite3 calls.db < schema.sql
    echo "✓ Database initialized"
fi

# Set permissions
chmod 755 recordings transcripts temp sessions conversations exports
chmod 644 calls.db

echo "✓ Data directories initialized"