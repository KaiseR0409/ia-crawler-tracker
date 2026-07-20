#libraries imports
import sqlite3
from pathlib import Patch

#Path of data base
DB_PATH = Path("data/tracker.db")


#connect and configure connection with sqlite
def get_connection():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA journald_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    conn.row_factory = sqlite3.Row
    return conn

#init database (creation)
def init_db():
    conn = get_connection()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS visits (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            target_url TEXT NOT NULL,
            traffic_type TEXT NOT NULL CHECK(traffic_type IN ('crawler', 'referral')),
            ai_provider TEXT NOT NULL DEFAULT 'Unknown',
            user_agent TEXT NOT NULL,
            referrer TEXT DEFAULT '',
            ip_hash TEXT DEFAULT ''
        )
    """)
    conn.execute("""
        CREATE INDEX IF NOT EXISTS idx_timestamp ON visits(timestamp)
    """)
    conn.execute("""
        CREATE INDEX IF NOT EXISTS idx_traffic_type ON visits(traffic_type)
    """)
    conn.execute("""
        CREATE INDEX IF NOT EXISTS idx_ai_provider ON visits(ai_provider)
    """)
    conn.commit()
    conn.close()


    