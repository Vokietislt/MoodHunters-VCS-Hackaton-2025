import sqlite3
import pandas as pd
from pathlib import Path
from typing import Optional, Tuple, List


class EmotionLogDB:
    def __init__(self, db_path: str = "emotion_log.db"):
        self.db_path = Path(db_path)
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)  
        self._ensure_log_table_exists()
    def close(self):
        self.conn.close()
    def _connect(self):
        try:
            return sqlite3.connect(self.db_path)
        except sqlite3.Error as e:
            raise ConnectionError(f"Database connection error: {e}")

    def _ensure_log_table_exists(self):
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS log (
                timestamp TEXT,
                face_id INTEGER,
                emotion TEXT,
                confidence REAL,
                foreground_app TEXT
            )
        """)

    def load_data(self) -> pd.DataFrame:
        df = pd.read_sql_query("SELECT * FROM log", self.conn)
        df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce')
        df['date'] = df['timestamp'].dt.date
        df['time'] = df['timestamp'].dt.time
        return df

    def read_logs(self) -> List[Tuple]:
        cursor = self.conn.execute("""
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
        cursor = self.conn.execute("""
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
        

    def insert_log(self, timestamp, face_id, emotion, confidence, foreground_app):
        self.conn.execute("""
            INSERT INTO log (timestamp, face_id, emotion, confidence, foreground_app)
            VALUES (?, ?, ?, ?, ?)
        """, (timestamp, face_id, emotion, confidence, foreground_app))
        self.conn.commit()  # commit after each write, or batch periodically

# Example usage:
# db = EmotionLogDB()
# db.read_logs()
# db.read_last_log()
# df = db.load_data()
# db
