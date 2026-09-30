def estimate_behavior(student_count, phone_users=0, standing=0, moving=0):
    if student_count <= 0:
        return {"attention_score": 0.0, "engagement": "No data"}
    distractions = min(phone_users + standing + moving, student_count)
    score = max(0.0, 100.0 - (distractions / student_count) * 100.0)
    if score >= 80:
        label = "High"
    elif score >= 60:
        label = "Moderate"
    else:
        label = "Low"
    return {"attention_score": round(score, 1), "engagement": label}
