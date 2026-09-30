import os
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]
SQLITE_PATH = BASE_DIR / "database" / "classroom.db"
SCHEMA_PATH = BASE_DIR / "database" / "schema.sql"

DATABASE_URL = os.getenv("DATABASE_URL", "").strip()

def _now():
    return datetime.now(timezone.utc).isoformat()

def _use_postgres():
    return bool(DATABASE_URL)

def _pg_conn():
    import psycopg
    return psycopg.connect(DATABASE_URL)

def _sqlite_conn():
    SQLITE_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(SQLITE_PATH))
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    schema = SCHEMA_PATH.read_text(encoding="utf-8")
    if _use_postgres():
        schema_pg = schema.replace("id INTEGER PRIMARY KEY", "id SERIAL PRIMARY KEY")
        with _pg_conn() as conn:
            with conn.cursor() as cur:
                for statement in schema_pg.split(";"):
                    statement = statement.strip()
                    if statement:
                        cur.execute(statement)
            conn.commit()
        return

    with _sqlite_conn() as conn:
        conn.executescript(schema)
        conn.commit()

def _row_dict(cursor, row):
    if row is None:
        return None
    if hasattr(cursor, "description"):
        columns = [d[0] for d in cursor.description]
        return dict(zip(columns, row))
    return dict(row)

def upsert_camera_row(camera_id, name, location, status, source):
    now = _now()
    if _use_postgres():
        with _pg_conn() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO cameras(camera_id,name,location,status,source,last_seen)
                    VALUES(%s,%s,%s,%s,%s,%s)
                    ON CONFLICT(camera_id) DO UPDATE SET
                      name=EXCLUDED.name,
                      location=EXCLUDED.location,
                      status=EXCLUDED.status,
                      source=EXCLUDED.source,
                      last_seen=EXCLUDED.last_seen
                    RETURNING camera_id,name,location,status,source,last_seen
                """, (camera_id, name, location, status, source, now))
                row = cur.fetchone()
                result = _row_dict(cur, row)
            conn.commit()
            return result

    with _sqlite_conn() as conn:
        conn.execute("""
            INSERT INTO cameras(camera_id,name,location,status,source,last_seen)
            VALUES(?,?,?,?,?,?)
            ON CONFLICT(camera_id) DO UPDATE SET
              name=excluded.name,
              location=excluded.location,
              status=excluded.status,
              source=excluded.source,
              last_seen=excluded.last_seen
        """, (camera_id, name, location, status, source, now))
        row = conn.execute("SELECT * FROM cameras WHERE camera_id=?", (camera_id,)).fetchone()
        conn.commit()
        return dict(row)

def insert_detection(camera_id, student_count, occupied_seats, phone_users,
                     standing, moving, attention_score, noise_level, mode):
    now = _now()
    if _use_postgres():
        with _pg_conn() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO detections(
                      camera_id,detected_at,student_count,occupied_seats,phone_users,
                      standing,moving,attention_score,noise_level,mode
                    )
                    VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                    RETURNING *
                """, (camera_id, now, student_count, occupied_seats, phone_users,
                      standing, moving, attention_score, noise_level, mode))
                row = cur.fetchone()
                result = _row_dict(cur, row)
            conn.commit()
            return result

    with _sqlite_conn() as conn:
        cur = conn.execute("""
            INSERT INTO detections(
              camera_id,detected_at,student_count,occupied_seats,phone_users,
              standing,moving,attention_score,noise_level,mode
            )
            VALUES(?,?,?,?,?,?,?,?,?,?)
        """, (camera_id, now, student_count, occupied_seats, phone_users,
              standing, moving, attention_score, noise_level, mode))
        row = conn.execute("SELECT * FROM detections WHERE id=?", (cur.lastrowid,)).fetchone()
        conn.commit()
        return dict(row)

def get_recent_detections(limit=50):
    if _use_postgres():
        with _pg_conn() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT d.*, c.name AS camera_name, c.location
                    FROM detections d
                    LEFT JOIN cameras c ON c.camera_id=d.camera_id
                    ORDER BY d.detected_at DESC LIMIT %s
                """, (limit,))
                rows = cur.fetchall()
                cols = [d[0] for d in cur.description]
                return [dict(zip(cols, r)) for r in rows]

    with _sqlite_conn() as conn:
        rows = conn.execute("""
            SELECT d.*, c.name AS camera_name, c.location
            FROM detections d
            LEFT JOIN cameras c ON c.camera_id=d.camera_id
            ORDER BY d.detected_at DESC LIMIT ?
        """, (limit,)).fetchall()
        return [dict(r) for r in rows]

def get_summary():
    if _use_postgres():
        with _pg_conn() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT COUNT(*) FROM cameras")
                cameras = cur.fetchone()[0]
                cur.execute("SELECT COUNT(*) FROM cameras WHERE status='online'")
                online = cur.fetchone()[0]
                cur.execute("SELECT COALESCE(MAX(detected_at), '') FROM detections")
                last_seen = cur.fetchone()[0]
                cur.execute("""
                    SELECT COALESCE(student_count,0)
                    FROM detections ORDER BY detected_at DESC LIMIT 1
                """)
                row = cur.fetchone()
                students = row[0] if row else 0
                return {"cameras": cameras, "online_cameras": online,
                        "students_now": students, "last_detection": last_seen}

    with _sqlite_conn() as conn:
        cameras = conn.execute("SELECT COUNT(*) FROM cameras").fetchone()[0]
        online = conn.execute("SELECT COUNT(*) FROM cameras WHERE status='online'").fetchone()[0]
        row = conn.execute("""
            SELECT student_count, detected_at FROM detections
            ORDER BY detected_at DESC LIMIT 1
        """).fetchone()
        return {
            "cameras": cameras,
            "online_cameras": online,
            "students_now": row["student_count"] if row else 0,
            "last_detection": row["detected_at"] if row else None
        }
