import sqlite3
from pathlib import Path
from datetime import datetime
from typing import Any
from config import DB_PATH

class DatabaseService:
    def __init__(self, db_path: str = DB_PATH):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._ensure_schema()

    def _connect(self):
        conn = sqlite3.connect(self.db_path, timeout=10, check_same_thread=False)
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA busy_timeout = 5000")
        return conn

    def _table_exists(self, conn: sqlite3.Connection, table_name: str) -> bool:
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table_name,))
        return cursor.fetchone() is not None

    def _get_table_columns(self, conn: sqlite3.Connection, table_name: str) -> list[str]:
        cursor = conn.cursor()
        cursor.execute(f"PRAGMA table_info({table_name})")
        return [row[1] for row in cursor.fetchall()]

    def _migrate_old_user_schema(self, conn: sqlite3.Connection) -> None:
        cursor = conn.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS users_new (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                telegram_id INTEGER UNIQUE,
                username TEXT,
                first_name TEXT,
                games_played INTEGER DEFAULT 0,
                wins INTEGER DEFAULT 0,
                losses INTEGER DEFAULT 0,
                jester_wins INTEGER DEFAULT 0,
                mafia_wins INTEGER DEFAULT 0,
                city_wins INTEGER DEFAULT 0,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        cursor.execute(
            """
            INSERT INTO users_new (telegram_id, username, first_name, games_played, wins, losses)
            SELECT user_id, username, '', COALESCE(wins, 0) + COALESCE(losses, 0), COALESCE(wins, 0), COALESCE(losses, 0)
            FROM users
            """
        )
        cursor.execute("DROP TABLE users")
        cursor.execute("ALTER TABLE users_new RENAME TO users")
        conn.commit()

    def _add_missing_user_columns(self, conn: sqlite3.Connection, existing_cols: list[str]) -> None:
        cursor = conn.cursor()
        missing_columns = {
            "telegram_id": "INTEGER UNIQUE",
            "first_name": "TEXT",
            "games_played": "INTEGER DEFAULT 0",
            "jester_wins": "INTEGER DEFAULT 0",
            "mafia_wins": "INTEGER DEFAULT 0",
            "city_wins": "INTEGER DEFAULT 0",
            "created_at": "TEXT DEFAULT CURRENT_TIMESTAMP",
        }
        for column, definition in missing_columns.items():
            if column not in existing_cols:
                cursor.execute(f"ALTER TABLE users ADD COLUMN {column} {definition}")
        conn.commit()

    def _ensure_schema(self) -> None:
        conn = self._connect()
        if self._table_exists(conn, "users"):
            existing_user_columns = self._get_table_columns(conn, "users")
            if "telegram_id" not in existing_user_columns and "user_id" in existing_user_columns:
                self._migrate_old_user_schema(conn)
            else:
                self._add_missing_user_columns(conn, existing_user_columns)
        else:
            cursor = conn.cursor()
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    telegram_id INTEGER UNIQUE,
                    username TEXT,
                    first_name TEXT,
                    games_played INTEGER DEFAULT 0,
                    wins INTEGER DEFAULT 0,
                    losses INTEGER DEFAULT 0,
                    jester_wins INTEGER DEFAULT 0,
                    mafia_wins INTEGER DEFAULT 0,
                    city_wins INTEGER DEFAULT 0,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
                """
            )
            conn.commit()

        cursor = conn.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS game_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                chat_id INTEGER,
                status TEXT,
                phase TEXT,
                night_number INTEGER,
                mode TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS players (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id INTEGER,
                telegram_id INTEGER,
                role TEXT,
                team TEXT,
                alive INTEGER,
                muted INTEGER,
                protected INTEGER,
                used_skill INTEGER,
                joined_at TEXT,
                FOREIGN KEY(session_id) REFERENCES game_sessions(id)
            )
            """
        )
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS actions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id INTEGER,
                actor_id INTEGER,
                target_id INTEGER,
                action_type TEXT,
                night_number INTEGER,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(session_id) REFERENCES game_sessions(id)
            )
            """
        )
        conn.commit()
        conn.close()

    def register_user(self, telegram_id: int, username: str, first_name: str) -> None:
        conn = self._connect()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT OR IGNORE INTO users (telegram_id, username, first_name) VALUES (?, ?, ?)",
            (telegram_id, username, first_name),
        )
        cursor.execute(
            "UPDATE users SET username = ?, first_name = ? WHERE telegram_id = ?",
            (username, first_name, telegram_id),
        )
        conn.commit()
        conn.close()

    def update_user_result(self, telegram_id: int, winner_type: str) -> None:
        conn = self._connect()
        cursor = conn.cursor()
        cursor.execute("UPDATE users SET games_played = games_played + 1 WHERE telegram_id = ?", (telegram_id,))
        if winner_type == "win_mafia":
            cursor.execute("UPDATE users SET wins = wins + 1, mafia_wins = mafia_wins + 1 WHERE telegram_id = ?", (telegram_id,))
        elif winner_type == "win_city":
            cursor.execute("UPDATE users SET wins = wins + 1, city_wins = city_wins + 1 WHERE telegram_id = ?", (telegram_id,))
        elif winner_type == "win_jester":
            cursor.execute("UPDATE users SET wins = wins + 1, jester_wins = jester_wins + 1 WHERE telegram_id = ?", (telegram_id,))
        else:
            cursor.execute("UPDATE users SET losses = losses + 1 WHERE telegram_id = ?", (telegram_id,))
        conn.commit()
        conn.close()

    def get_profile(self, telegram_id: int) -> dict[str, Any] | None:
        conn = self._connect()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT username, first_name, games_played, wins, losses, jester_wins, mafia_wins, city_wins, created_at FROM users WHERE telegram_id = ?",
            (telegram_id,),
        )
        row = cursor.fetchone()
        conn.close()
        if not row:
            return None
        return {
            "username": row[0],
            "first_name": row[1],
            "games_played": row[2],
            "wins": row[3],
            "losses": row[4],
            "jester_wins": row[5],
            "mafia_wins": row[6],
            "city_wins": row[7],
            "created_at": row[8],
        }

    def get_top_players(self, limit: int = 10) -> list[tuple[str, int]]:
        conn = self._connect()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT username, wins FROM users ORDER BY wins DESC, games_played ASC LIMIT ?",
            (limit,),
        )
        rows = cursor.fetchall()
        conn.close()
        return rows

    def create_session_record(self, chat_id: int, status: str, phase: str, night_number: int, mode: str) -> int:
        conn = self._connect()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO game_sessions (chat_id, status, phase, night_number, mode) VALUES (?, ?, ?, ?, ?)",
            (chat_id, status, phase, night_number, mode),
        )
        session_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return session_id

    def update_session_record(self, session_id: int, status: str, phase: str, night_number: int) -> None:
        conn = self._connect()
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE game_sessions SET status = ?, phase = ?, night_number = ? WHERE id = ?",
            (status, phase, night_number, session_id),
        )
        conn.commit()
        conn.close()

    def add_player_record(self, session_id: int, telegram_id: int, role: str, team: str, alive: bool, muted: bool, protected: bool, used_skill: bool, joined_at: str) -> None:
        conn = self._connect()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO players (session_id, telegram_id, role, team, alive, muted, protected, used_skill, joined_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (session_id, telegram_id, role, team, int(alive), int(muted), int(protected), int(used_skill), joined_at),
        )
        conn.commit()
        conn.close()

    def add_action_record(self, session_id: int, actor_id: int, target_id: int, action_type: str, night_number: int) -> None:
        conn = self._connect()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO actions (session_id, actor_id, target_id, action_type, night_number) VALUES (?, ?, ?, ?, ?)",
            (session_id, actor_id, target_id, action_type, night_number),
        )
        conn.commit()
        conn.close()

    def admin_log(self, owner_id: int, owner_name: str, command: str) -> None:
        conn = self._connect()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO actions (session_id, actor_id, target_id, action_type, night_number) VALUES (NULL, NULL, NULL, ?, NULL)",
            (f"ADMIN {owner_name}({owner_id}) -> {command}",),
        )
        conn.commit()
        conn.close()

    def get_stats(self) -> dict[str, Any]:
        conn = self._connect()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM users")
        total_users = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM game_sessions")
        total_games = cursor.fetchone()[0]
        conn.close()
        return {"total_users": total_users, "total_games": total_games, "database_size": self.db_path.stat().st_size if self.db_path.exists() else 0}
