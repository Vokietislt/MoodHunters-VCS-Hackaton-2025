import sqlite3
import pandas as pd
from pathlib import Path
from typing import Optional, Tuple, List


class EmotionLogDB:
    def __init__(self, db_path: str = "emotion_log.db"):
        self.db_path = Path(db_path)
        self._ensure_log_table_exists()

    def _connect(self):
        try:
            return sqlite3.connect(self.db_path)
        except sqlite3.Error as e:
            raise ConnectionError(f"Database connection error: {e}")

    def _ensure_log_table_exists(self):
        with self._connect() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS log (
                    timestamp TEXT,
                    face_id INTEGER,
                    emotion TEXT,
                    confidence REAL,
                    foreground_app TEXT
                )
            """)

    def load_data(self) -> pd.DataFrame:
        with self._connect() as conn:
            df = pd.read_sql_query("SELECT * FROM log", conn)

        df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce')
        df['date'] = df['timestamp'].dt.date
        df['time'] = df['timestamp'].dt.time
        return df

    def read_logs(self) -> List[Tuple]:
        with self._connect() as conn:
            cursor = conn.execute("""
                SELECT timestamp, face_id, emotion, confidence, foreground_app 
                FROM log 
                ORDER BY timestamp DESC
            """)
            rows = cursor.fetchall()

        if not rows:
            print("No emotion logs found.")
        else:
            self._print_log_header()
            for row in rows:
                self._print_log_row(row)
        return rows

    def read_last_log(self) -> Optional[Tuple]:
        with self._connect() as conn:
            cursor = conn.execute("""
                SELECT timestamp, face_id, emotion, confidence, foreground_app 
                FROM log 
                ORDER BY timestamp DESC 
                LIMIT 1
            """)
            row = cursor.fetchone()

        if not row:
            print("No emotion logs found.")
            return None

        self._print_log_header()
        self._print_log_row(row)
        return row

    def _print_log_header(self):
        print(f"{'Timestamp':<20} | {'Face ID':<7} | {'Emotion':<10} | {'Confidence':<10} | Foreground App")
        print("-" * 80)

    def _print_log_row(self, row: Tuple):
        timestamp, face_id, emotion, confidence, app = (
            self._decode_str(row[0]),
            row[1],
            self._decode_str(row[2]),
            self._decode_float(row[3]),
            self._decode_str(row[4])
        )
        print(f"{timestamp:<20} | {face_id:<7} | {emotion:<10} | {confidence:<10.2f} | {app}")

    def _decode_str(self, val):
        if isinstance(val, bytes):
            return val.decode("utf-8", errors="replace")
        return str(val)

    def _decode_float(self, val):
        if isinstance(val, bytes):
            try:
                return float(val.decode("utf-8", errors="replace"))
            except Exception:
                return 0.0
        return float(val)
        
    def insert_log(self, timestamp: str, face_id: int, emotion: str, confidence: float, foreground_app: str):
        """Insert a single log entry into the database."""
        with self._connect() as conn:
            conn.execute("""
                INSERT INTO log (timestamp, face_id, emotion, confidence, foreground_app)
                VALUES (?, ?, ?, ?, ?)
            """, (timestamp, face_id, emotion, confidence, foreground_app))

# Example usage:
# db = EmotionLogDB()
# db.read_logs()
# db.read_last_log()
# df = db.load_data()
