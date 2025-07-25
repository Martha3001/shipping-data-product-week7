import json
import cv2
from ultralytics import YOLO
from pathlib import Path
from datetime import datetime, timezone
from datasets import load_dataset

# Base directory to scan recursively
BASE_IMAGE_DIR = Path("data/raw/telegram_messages")
OUTPUT_JSON = Path("data/raw/detected_images/image_detections.json")
YOLO_MODEL = "yolov8n.pt"
OUTPUT_IMG_DIR = Path("data/raw/detected_images")

# Login using e.g. `huggingface-cli login` to access this dataset
ds = load_dataset("Ultralytics/Medical-pills")

# Load YOLOv8 model
model = YOLO(YOLO_MODEL)
model.train(data='../medical.yaml', epochs=50, imgsz=640)

def extract_message_id(filename):
    # Now filename is like '1234.jpg' → message_id = 1234
    try:
        return int(filename.stem)
    except ValueError:
        return None

def detect_objects():
    detections = []

    # Recursively scan all jpg images under base folder
    for image_path in BASE_IMAGE_DIR.rglob("*.jpg"):
        message_id = extract_message_id(image_path)
        if message_id is None:
            continue

        results = model(image_path)

        for r in results:
            # Save annotated image
            # Compute relative path from BASE_IMAGE_DIR and append it to OUTPUT_IMG_DIR
            relative_img_path = image_path.relative_to(BASE_IMAGE_DIR)
            save_path = OUTPUT_IMG_DIR / relative_img_path
            save_path.parent.mkdir(parents=True, exist_ok=True)

            annotated_img = r.plot()
            cv2.imwrite(str(save_path), annotated_img)

            for box in r.boxes:
                class_id = int(box.cls[0])
                confidence = float(box.conf[0])
                class_name = model.names[class_id]

                detections.append({
                    "message_id": message_id,
                    "detected_object_class": class_name,
                    "confidence_score": confidence,
                    "image_filename": image_path.name,
                    "relative_path": str(image_path.relative_to(BASE_IMAGE_DIR)),
                    "processed_at": datetime.now(timezone.utc).isoformat()
                })

    if detections:
        with open(OUTPUT_JSON, "w") as f:
            json.dump(detections, f, indent=2)
        print(f"Detection results saved to {OUTPUT_JSON}")
    else:
        print("No detections found.")

if __name__ == "__main__":
    detect_objects()
