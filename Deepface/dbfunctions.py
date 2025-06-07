import sqlite3
import os

DB_PATH = "emotion_log.db"

def ensure_log_table_exists(conn):
    """Creates the log table if it doesn't already exist."""
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS log (
            timestamp TEXT,
            face_id INTEGER,
            emotion TEXT,
            confidence REAL,
            foreground_app TEXT
        )
    """)
    conn.commit()

def read_logs():
    try:
        # Connect to the database
        conn = sqlite3.connect(DB_PATH)
        ensure_log_table_exists(conn)

        cursor = conn.cursor()
        cursor.execute("""
            SELECT timestamp, face_id, emotion, confidence, foreground_app 
            FROM log 
            ORDER BY timestamp DESC
        """)
        rows = cursor.fetchall()

        if not rows:
            print("No emotion logs found.")
        else:
            print(f"{'Timestamp':<20} | {'Face ID':<7} | {'Emotion':<10} | {'Confidence':<10} | Foreground App")
            print("-" * 80)
            for row in rows:
                timestamp, face_id, emotion, confidence, app = row

                # Decode bytes if necessary
                if isinstance(timestamp, bytes):
                    timestamp = timestamp.decode("utf-8", errors="replace")
                if isinstance(emotion, bytes):
                    emotion = emotion.decode("utf-8", errors="replace")
                if isinstance(app, bytes):
                    app = app.decode("utf-8", errors="replace")

                # Convert confidence to float if needed
                if isinstance(confidence, bytes):
                    try:
                        confidence = float(confidence.decode("utf-8", errors="replace"))
                    except Exception:
                        confidence = 0.0

                print(f"{timestamp:<20} | {face_id:<7} | {emotion:<10} | {confidence:<10.2f} | {app}")

        conn.close()
    except Exception as e:
        print(f"Error reading database: {e}")

def read_last_log():
    try:
        # Connect to the database
        conn = sqlite3.connect(DB_PATH)
        ensure_log_table_exists(conn)

        cursor = conn.cursor()
        cursor.execute("""
            SELECT timestamp, face_id, emotion, confidence, foreground_app 
            FROM log 
            ORDER BY timestamp DESC 
            LIMIT 1
        """)
        row = cursor.fetchone()

        if not row:
            print("No emotion logs found.")
            return None
        else:
            timestamp, face_id, emotion, confidence, app = row

            # Decode bytes if necessary
            if isinstance(timestamp, bytes):
                timestamp = timestamp.decode("utf-8", errors="replace")
            if isinstance(emotion, bytes):
                emotion = emotion.decode("utf-8", errors="replace")
            if isinstance(app, bytes):
                app = app.decode("utf-8", errors="replace")

            # Convert confidence to float if needed
            if isinstance(confidence, bytes):
                try:
                    confidence = float(confidence.decode("utf-8", errors="replace"))
                except Exception:
                    confidence = 0.0

            print(f"{'Timestamp':<20} | {'Face ID':<7} | {'Emotion':<10} | {'Confidence':<10} | Foreground App")
            print("-" * 80)
            print(f"{timestamp:<20} | {face_id:<7} | {emotion:<10} | {confidence:<10.2f} | {app}")
            return row

        conn.close()
    except Exception as e:
        print(f"Error reading database: {e}")
        return None


# if __name__ == "__main__":
#     read_logs()
