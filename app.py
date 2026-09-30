import os
from datetime import datetime, timezone
from flask import Flask, jsonify, render_template, request
from services.database import init_db, get_summary, get_recent_detections, insert_detection, get_camera_status
from services.camera_registry import get_cameras, upsert_camera

app = Flask(__name__)

init_db()

WORKER_API_KEY = os.getenv("WORKER_API_KEY", "").strip()


def _authorized_worker():
    if not WORKER_API_KEY:
        return True
    return request.headers.get("X-Worker-Key", "") == WORKER_API_KEY


@app.get("/")
def dashboard():
    return render_template("dashboard.html")


@app.get("/analytics")
def analytics():
    return render_template("analytics.html")


@app.get("/api/health")
def health():
    return jsonify({
        "status": "online",
        "service": "AI Classroom Monitoring System",
        "time_utc": datetime.now(timezone.utc).isoformat()
    })


@app.get("/api/summary")
def summary():
    return jsonify(get_summary())


@app.get("/api/detections")
def detections():
    try:
        limit = min(max(int(request.args.get("limit", 50)), 1), 200)
    except ValueError:
        limit = 50
    return jsonify(get_recent_detections(limit))


@app.get("/api/cameras")
def cameras():
    return jsonify(get_cameras())


@app.get("/api/cameras/<int:camera_id>")
def camera(camera_id):
    data = get_camera_status(camera_id)
    if not data:
        return jsonify({"error": "camera_not_found"}), 404
    return jsonify(data)


@app.post("/api/worker/detection")
def worker_detection():
    if not _authorized_worker():
        return jsonify({"error": "unauthorized"}), 401

    payload = request.get_json(silent=True) or {}
    required = ["camera_id", "student_count"]
    missing = [x for x in required if x not in payload]
    if missing:
        return jsonify({"error": "missing_fields", "fields": missing}), 400

    camera_id = int(payload["camera_id"])
    student_count = max(int(payload.get("student_count", 0)), 0)

    upsert_camera(
        camera_id=camera_id,
        name=payload.get("camera_name") or f"Camera {camera_id}",
        location=payload.get("location") or "Classroom",
        status="online",
        source=str(payload.get("source", "worker"))
    )

    row = insert_detection(
        camera_id=camera_id,
        student_count=student_count,
        occupied_seats=int(payload.get("occupied_seats", student_count)),
        phone_users=int(payload.get("phone_users", 0)),
        standing=int(payload.get("standing", 0)),
        moving=int(payload.get("moving", 0)),
        attention_score=float(payload.get("attention_score", 0)),
        noise_level=str(payload.get("noise_level", "Unknown")),
        mode=str(payload.get("mode", "ai"))
    )
    return jsonify({"ok": True, "detection": row}), 201


@app.post("/api/cameras/register")
def register_camera():
    if not _authorized_worker():
        return jsonify({"error": "unauthorized"}), 401
    payload = request.get_json(silent=True) or {}
    if "camera_id" not in payload:
        return jsonify({"error": "camera_id_required"}), 400
    row = upsert_camera(
        camera_id=int(payload["camera_id"]),
        name=payload.get("name") or f"Camera {payload['camera_id']}",
        location=payload.get("location") or "Classroom",
        status=payload.get("status", "online"),
        source=payload.get("source", "worker")
    )
    return jsonify(row), 201


@app.errorhandler(404)
def not_found(_):
    if request.path.startswith("/api/"):
        return jsonify({"error": "not_found"}), 404
    return render_template("dashboard.html"), 404


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "5000")), debug=False)
