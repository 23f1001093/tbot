"""
Database manager for call history
"""

import os
import sqlite3
import logging
from typing import List, Dict, Optional
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)

class Database:
    """SQLite database manager"""
    
    def __init__(self):
        """Initialize database"""
        db_url = os.getenv('DATABASE_URL', 'sqlite:///data/calls.db')
        db_path = db_url.replace('sqlite:///', '')
        
        # Ensure directory exists
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        
        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row
        
        self._create_tables()
        logger.info(f"✅ Database initialized: {db_path}")
    
    def _create_tables(self):
        """Create database tables"""
        self.conn.execute('''
            CREATE TABLE IF NOT EXISTS calls (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                call_id INTEGER UNIQUE,
                user_id INTEGER,
                start_time TIMESTAMP,
                end_time TIMESTAMP,
                duration INTEGER,
                status TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        self.conn.execute('''
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                call_id INTEGER,
                role TEXT,
                content TEXT,
                timestamp TIMESTAMP,
                FOREIGN KEY (call_id) REFERENCES calls (call_id)
            )
        ''')
        
        self.conn.commit()
    
    def save_call(self, call_data: Dict):
        """Save call record"""
        try:
            self.conn.execute('''
                INSERT INTO calls (call_id, user_id, start_time, end_time, duration, status)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                call_data['call_id'],
                call_data.get('user_id'),
                call_data.get('start_time'),
                call_data.get('end_time'),
                call_data.get('duration', 0),
                call_data.get('status', 'completed')
            ))
            self.conn.commit()
            logger.info(f"Call {call_data['call_id']} saved")
        except Exception as e:
            logger.error(f"Error saving call: {e}")
    
    def save_message(self, call_id: int, role: str, content: str):
        """Save message"""
        try:
            self.conn.execute('''
                INSERT INTO messages (call_id, role, content, timestamp)
                VALUES (?, ?, ?, ?)
            ''', (call_id, role, content, datetime.utcnow()))
            self.conn.commit()
        except Exception as e:
            logger.error(f"Error saving message: {e}")
    
    def get_call_history(self, limit: int = 10) -> List[Dict]:
        """Get recent calls"""
        cursor = self.conn.execute('''
            SELECT * FROM calls
            ORDER BY created_at DESC
            LIMIT ?
        ''', (limit,))
        
        return [dict(row) for row in cursor.fetchall()]
    
    def close(self):
        """Close database connection"""
        self.conn.close()