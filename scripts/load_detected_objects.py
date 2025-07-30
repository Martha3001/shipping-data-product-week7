# import os
# import json
# import psycopg2
# from dotenv import load_dotenv
# from datetime import datetime

# # Load environment variables from .env file
# load_dotenv('.env')

# def get_db_connection():
#     """Establish database connection using environment variables."""
#     return psycopg2.connect(
#         host=os.getenv('DB_HOST'),
#         database=os.getenv('POSTGRES_DB'),
#         user=os.getenv('POSTGRES_USER'),
#         password=os.getenv('POSTGRES_PASSWORD'),
#         port=os.getenv('DB_PORT', '5432')
#     )

# def create_detections_table(conn):
#     """Create the raw.image_detections table if it doesn't exist."""
#     with conn.cursor() as cursor:
#         cursor.execute("""
#             CREATE TABLE IF NOT EXISTS raw.image_detections (
#                 id SERIAL PRIMARY KEY,
#                 message_id INTEGER,
#                 detected_object_class VARCHAR(255),
#                 confidence_score REAL,
#                 image_filename VARCHAR(255),
#                 relative_path TEXT,
#                 processed_at TIMESTAMP,
#                 loaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
#             );
#             CREATE INDEX IF NOT EXISTS idx_message_id ON raw.image_detections(message_id);
#             CREATE INDEX IF NOT EXISTS idx_detected_object_class ON raw.image_detections(detected_object_class);
#         """)
#     conn.commit()

# def load_detection_json(file_path, conn):
#     """Load detection results from JSON file into the database."""
#     try:
#         with open(file_path, 'r', encoding='utf-8') as f:
#             detections = json.load(f)
#     except Exception as e:
#         print(f"Failed to read JSON file {file_path}: {e}")
#         return 0

#     count = 0
#     with conn.cursor() as cursor:
#         for det in detections:
#             try:
#                 processed_at = datetime.fromisoformat(det['processed_at'])
#                 cursor.execute("""
#                     INSERT INTO raw.image_detections
#                         (message_id, detected_object_class, confidence_score, image_filename, relative_path, processed_at)
#                     VALUES (%s, %s, %s, %s, %s, %s)
#                 """, (
#                     det['message_id'],
#                     det['detected_object_class'],
#                     det['confidence_score'],
#                     det['image_filename'],
#                     det['relative_path'],
#                     processed_at
#                 ))
#                 count += 1
#             except Exception as e:
#                 print(f"Skipping a record due to error: {e}")
#     conn.commit()
#     print(f"Successfully loaded {count} detections from {file_path}")
#     return count

# if __name__ == "__main__":
#     detection_json_path = os.path.join('data', 'raw', 'detected_images', 'image_detections.json')

#     if not os.path.exists(detection_json_path):
#         print(f"Detection JSON file not found at: {detection_json_path}")
#         exit(1)

#     conn = get_db_connection()
#     try:
#         create_detections_table(conn)
#         load_detection_json(detection_json_path, conn)
#     finally:
#         conn.close()

import os
import json
import psycopg2
from dotenv import load_dotenv
from datetime import datetime

# Load environment variables from .env file
load_dotenv('.env')

def get_db_connection():
    """Establish database connection using environment variables."""
    return psycopg2.connect(
        host=os.getenv('DB_HOST'),
        database=os.getenv('POSTGRES_DB'),
        user=os.getenv('POSTGRES_USER'),
        password=os.getenv('POSTGRES_PASSWORD'),
        port=os.getenv('DB_PORT', '5432')
    )

def create_detections_table(conn):
    """Create the raw.image_detections table with necessary constraints and indexes."""
    with conn.cursor() as cursor:
        cursor.execute("""
            CREATE SCHEMA IF NOT EXISTS raw;

            CREATE TABLE IF NOT EXISTS raw.image_detections (
                id SERIAL PRIMARY KEY,
                message_id INTEGER,
                detected_object_class VARCHAR(255),
                confidence_score REAL,
                image_filename VARCHAR(255),
                relative_path TEXT,
                processed_at TIMESTAMP,
                loaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );

            CREATE INDEX IF NOT EXISTS idx_message_id 
                ON raw.image_detections(message_id);

            CREATE INDEX IF NOT EXISTS idx_detected_object_class 
                ON raw.image_detections(detected_object_class);

            -- ✅ This line adds the missing unique constraint
            CREATE UNIQUE INDEX IF NOT EXISTS uniq_detection 
                ON raw.image_detections(message_id, image_filename, detected_object_class);
        """)
    conn.commit()


def load_detection_json(file_path, conn):
    """Load detection results from a JSON file into the database, skipping duplicates."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            detections = json.load(f)
    except Exception as e:
        print(f"Failed to read JSON file {file_path}: {e}")
        return 0

    count = 0
    for det in detections:
        try:
            with conn.cursor() as cursor:
                processed_at = datetime.fromisoformat(det['processed_at'])
                cursor.execute("""
                    INSERT INTO raw.image_detections
                        (message_id, detected_object_class, confidence_score, image_filename, relative_path, processed_at)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    ON CONFLICT (message_id, image_filename, detected_object_class) DO NOTHING
                """, (
                    det['message_id'],
                    det['detected_object_class'],
                    det['confidence_score'],
                    det['image_filename'],
                    det['relative_path'],
                    processed_at
                ))
                if cursor.rowcount > 0:
                    count += 1
        except Exception as e:
            print(f"Skipping a record due to error: {e}")
            conn.rollback()  # Important: Rollback to recover from failure

    conn.commit()
    print(f"Successfully inserted {count} new detections from {file_path}")
    return count

if __name__ == "__main__":
    detection_json_path = os.path.join('data', 'raw', 'detected_images', 'image_detections.json')

    if not os.path.exists(detection_json_path):
        print(f"Detection JSON file not found at: {detection_json_path}")
        exit(1)

    conn = get_db_connection()
    try:
        create_detections_table(conn)
        load_detection_json(detection_json_path, conn)
    finally:
        conn.close()
