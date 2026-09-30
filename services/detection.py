from pathlib import Path

_model = None

def load_model():
    global _model
    if _model is None:
        from ultralytics import YOLO
        model_path = Path(__file__).resolve().parents[1] / "models" / "yolo11n.pt"
        _model = YOLO(str(model_path))
    return _model

def count_people(frame, confidence=0.35):
    model = load_model()
    result = model.predict(source=frame, conf=confidence, verbose=False)[0]
    count = 0
    boxes = getattr(result, "boxes", None)
    if boxes is not None and boxes.cls is not None:
        for cls in boxes.cls.tolist():
            if int(cls) == 0:  # COCO person class
                count += 1
    return count
