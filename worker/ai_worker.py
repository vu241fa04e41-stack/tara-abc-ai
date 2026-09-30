import argparse
import os
import time
import cv2
import requests

from services.detection import count_people
from services.behavior import estimate_behavior

def parse_source(value):
    try:
        return int(value)
    except ValueError:
        return value

def main():
    parser = argparse.ArgumentParser(description="AI classroom camera worker")
    parser.add_argument("--camera", type=int, default=int(os.getenv("CAMERA_ID", "1")))
    parser.add_argument("--source", default=os.getenv("CAMERA_SOURCE", "0"))
    parser.add_argument("--api-url", default=os.getenv("API_URL", "http://127.0.0.1:5000"))
    parser.add_argument("--name", default=os.getenv("CAMERA_NAME", "Classroom Camera"))
    parser.add_argument("--location", default=os.getenv("CAMERA_LOCATION", "Classroom"))
    parser.add_argument("--interval", type=float, default=2.0)
    args = parser.parse_args()

    source = parse_source(args.source)
    cap = cv2.VideoCapture(source)
    if not cap.isOpened():
        raise RuntimeError(f"Could not open camera/video source: {source}")

    api = args.api_url.rstrip("/")
    key = os.getenv("WORKER_API_KEY", "")
    headers = {"X-Worker-Key": key} if key else {}

    print(f"Worker started: camera={args.camera}, source={source}, API={api}")

    try:
        while True:
            ok, frame = cap.read()
            if not ok:
                print("Frame read failed; retrying...")
                time.sleep(2)
                continue

            student_count = count_people(frame)
            behavior = estimate_behavior(student_count)

            payload = {
                "camera_id": args.camera,
                "camera_name": args.name,
                "location": args.location,
                "source": str(source),
                "student_count": student_count,
                "occupied_seats": student_count,
                "phone_users": 0,
                "standing": 0,
                "moving": 0,
                "attention_score": behavior["attention_score"],
                "noise_level": "Unknown",
                "mode": "ai"
            }

            try:
                response = requests.post(
                    f"{api}/api/worker/detection",
                    json=payload,
                    headers=headers,
                    timeout=15
                )
                response.raise_for_status()
                print(f"camera={args.camera} students={student_count}")
            except requests.RequestException as exc:
                print(f"API error: {exc}")

            time.sleep(max(args.interval, 0.2))
    finally:
        cap.release()

if __name__ == "__main__":
    main()
