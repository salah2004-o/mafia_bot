# database.py
import sqlite3
from config import DB_PATH

def init_db():
    """إنشاء الجداول إذا لم تكن موجودة"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            score INTEGER DEFAULT 0,
            wins INTEGER DEFAULT 0,
            losses INTEGER DEFAULT 0
        )
    ''')
    conn.commit()
    conn.close()

def register_user_db(user_id: int, username: str):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("INSERT OR IGNORE INTO users (user_id, username) VALUES (?, ?)", (user_id, username))
    conn.commit()
    conn.close()

def update_player_stats(user_id: int, is_winner: bool):
    """تحديث النقاط: الفائز +10، الخاسر -5 بحد أدنى 0"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    if is_winner:
        cursor.execute("UPDATE users SET score = score + 10, wins = wins + 1 WHERE user_id = ?", (user_id,))
    else:
        cursor.execute("UPDATE users SET score = MAX(0, score - 5), losses = losses + 1 WHERE user_id = ?", (user_id,))
    conn.commit()
    conn.close()

def get_top_players():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT username, score FROM users ORDER BY score DESC LIMIT 10")
    leaders = cursor.fetchall()
    conn.close()
    return leaders