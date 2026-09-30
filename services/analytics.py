from services.database import get_recent_detections

def calculate_metrics(limit=100):
    rows = get_recent_detections(limit)
    if not rows:
        return {
            "samples": 0,
            "average_students": 0,
            "average_attention": 0,
            "phone_events": 0
        }
    return {
        "samples": len(rows),
        "average_students": round(sum(r["student_count"] for r in rows) / len(rows), 2),
        "average_attention": round(sum(float(r["attention_score"]) for r in rows) / len(rows), 2),
        "phone_events": sum(r["phone_users"] for r in rows)
    }
