import json
import cv2
from ultralytics import YOLO
from pathlib import Path
from datetime import datetime, timezone

# === Paths ===
BASE_IMAGE_DIR = Path("data/raw/telegram_messages")
OUTPUT_JSON = Path("data/raw/detected_images/image_detections.json")
OUTPUT_IMG_DIR = Path("data/raw/detected_images")

# === Load Models ===
general_model = YOLO("yolov8n.pt")  # General object detection (COCO)
pill_model = YOLO("runs/detect/train7/weights/best.pt")  # Trained pill detector

def extract_message_id(filename):
    try:
        return int(filename.stem)
    except ValueError:
        return None

def load_existing_detections():
    if OUTPUT_JSON.exists():
        with open(OUTPUT_JSON, 'r') as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                print(f"Warning: Failed to parse existing detection file {OUTPUT_JSON}")
                return []
    return []

def detect_objects():
    detections = []
    existing_detections = load_existing_detections()

    # Build a set of detected message_ids or relative paths to skip
    detected_message_ids = set(d['message_id'] for d in existing_detections)
    # Or, to be more strict, use relative paths:
    detected_relative_paths = set(d['relative_path'] for d in existing_detections)

    for image_path in BASE_IMAGE_DIR.rglob("*.jpg"):
        message_id = extract_message_id(image_path)
        if message_id is None:
            continue

        relative_path = str(image_path.relative_to(BASE_IMAGE_DIR))

        # Skip if already detected (by message_id or by path)
        if message_id in detected_message_ids or relative_path in detected_relative_paths:
            print(f"Skipping already detected image: {relative_path}")
            continue

        # === Run Both Models ===
        results_general = general_model(image_path)[0]
        results_pill = pill_model(image_path)[0]

        # === Read Original Image for Annotation ===
        image = cv2.imread(str(image_path))

        # === Collect and Draw General Detections ===
        for box in results_general.boxes:
            cls = int(box.cls[0])
            conf = float(box.conf[0])
            label = general_model.names[cls]
            x1, y1, x2, y2 = box.xyxy[0].cpu().numpy().astype(int)

            detections.append({
                "message_id": message_id,
                "detected_object_class": label,
                "confidence_score": conf,
                "image_filename": image_path.name,
                "relative_path": relative_path,
                "processed_at": datetime.now(timezone.utc).isoformat()
            })

            cv2.rectangle(image, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.putText(image, f"{label} {conf:.2f}", (x1, y1 - 5),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

        # === Collect and Draw Pill Detections ===
        for box in results_pill.boxes:
            cls = int(box.cls[0])
            conf = float(box.conf[0])
            if conf < 0.7:
                continue
            label = pill_model.names[cls]
            x1, y1, x2, y2 = box.xyxy[0].cpu().numpy().astype(int)

            detections.append({
                "message_id": message_id,
                "detected_object_class": label,
                "confidence_score": conf,
                "image_filename": image_path.name,
                "relative_path": relative_path,
                "processed_at": datetime.now(timezone.utc).isoformat()
            })

            cv2.rectangle(image, (x1, y1), (x2, y2), (0, 0, 255), 2)
            cv2.putText(image, f"{label} {conf:.2f}", (x1, y1 - 5),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)

        # === Save Annotated Image ===
        save_path = OUTPUT_IMG_DIR / relative_path
        save_path.parent.mkdir(parents=True, exist_ok=True)
        cv2.imwrite(str(save_path), image)

    # === Append new detections to existing and save ===
    all_detections = existing_detections + detections

    if all_detections:
        OUTPUT_JSON.parent.mkdir(parents=True, exist_ok=True)
        with open(OUTPUT_JSON, "w") as f:
            json.dump(all_detections, f, indent=2)
        print(f"[✔] Detection results saved to {OUTPUT_JSON}")
    else:
        print("No new detections found.")

if __name__ == "__main__":
    detect_objects()
