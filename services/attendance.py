def attendance_from_count(student_count, enrolled_students):
    if enrolled_students <= 0:
        return 0.0
    return round(min(student_count / enrolled_students, 1.0) * 100, 2)
