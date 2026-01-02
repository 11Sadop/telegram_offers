import sqlite3
from datetime import datetime

DATABASE_FILE = "offers.db"


def init_db():
    """Initialize the database with required tables"""
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS offers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            link TEXT UNIQUE NOT NULL,
            price TEXT,
            category TEXT,
            source TEXT,
            posted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            is_sent BOOLEAN DEFAULT 0
        )
    """)
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_link ON offers(link)
    """)
    conn.commit()
    conn.close()
    print("✅ Database initialized")


def offer_exists(link: str) -> bool:
    """Check if an offer already exists in the database"""
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT 1 FROM offers WHERE link = ?", (link,))
    result = cursor.fetchone()
    conn.close()
    return result is not None


def save_offer(title: str, link: str, price: str = None, 
               category: str = None, source: str = None) -> bool:
    """Save a new offer to the database. Returns True if saved, False if exists."""
    if offer_exists(link):
        return False
    
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO offers (title, link, price, category, source)
        VALUES (?, ?, ?, ?, ?)
    """, (title, link, price, category, source))
    conn.commit()
    conn.close()
    return True


def mark_as_sent(link: str):
    """Mark an offer as sent to the channel"""
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    cursor.execute("UPDATE offers SET is_sent = 1 WHERE link = ?", (link,))
    conn.commit()
    conn.close()


def get_unsent_offers(limit: int = 10):
    """Get offers that haven't been sent yet"""
    conn = sqlite3.connect(DATABASE_FILE)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("""
        SELECT * FROM offers 
        WHERE is_sent = 0 
        ORDER BY posted_at DESC 
        LIMIT ?
    """, (limit,))
    results = cursor.fetchall()
    conn.close()
    return results


def get_stats():
    """Get database statistics"""
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM offers")
    total = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM offers WHERE is_sent = 1")
    sent = cursor.fetchone()[0]
    
    conn.close()
    return {"total": total, "sent": sent, "pending": total - sent}
