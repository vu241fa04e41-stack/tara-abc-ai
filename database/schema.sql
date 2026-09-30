CREATE TABLE IF NOT EXISTS cameras (
    camera_id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    location TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'offline',
    source TEXT NOT NULL DEFAULT 'worker',
    last_seen TEXT
);

CREATE TABLE IF NOT EXISTS detections (
    id INTEGER PRIMARY KEY,
    camera_id INTEGER NOT NULL,
    detected_at TEXT NOT NULL,
    student_count INTEGER NOT NULL DEFAULT 0,
    occupied_seats INTEGER NOT NULL DEFAULT 0,
    phone_users INTEGER NOT NULL DEFAULT 0,
    standing INTEGER NOT NULL DEFAULT 0,
    moving INTEGER NOT NULL DEFAULT 0,
    attention_score REAL NOT NULL DEFAULT 0,
    noise_level TEXT NOT NULL DEFAULT 'Unknown',
    mode TEXT NOT NULL DEFAULT 'ai'
);
