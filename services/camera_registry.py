from services.database import upsert_camera_row, _pg_conn, _sqlite_conn, _use_postgres

def upsert_camera(camera_id, name, location, status="offline", source="worker"):
    return upsert_camera_row(camera_id, name, location, status, source)

def get_cameras():
    if _use_postgres():
        with _pg_conn() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT * FROM cameras ORDER BY camera_id")
                rows = cur.fetchall()
                cols = [d[0] for d in cur.description]
                return [dict(zip(cols, r)) for r in rows]
    with _sqlite_conn() as conn:
        rows = conn.execute("SELECT * FROM cameras ORDER BY camera_id").fetchall()
        return [dict(r) for r in rows]

def get_camera_status(camera_id):
    if _use_postgres():
        with _pg_conn() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT * FROM cameras WHERE camera_id=%s", (camera_id,))
                row = cur.fetchone()
                if not row:
                    return None
                cols = [d[0] for d in cur.description]
                return dict(zip(cols, row))
    with _sqlite_conn() as conn:
        row = conn.execute("SELECT * FROM cameras WHERE camera_id=?", (camera_id,)).fetchone()
        return dict(row) if row else None
