import os
import json
import psycopg2
from dotenv import load_dotenv
from datetime import datetime

# Load environment variables
load_dotenv('.env')

def get_db_connection():
    """Establish database connection using environment variables"""
    return psycopg2.connect(
        host=os.getenv('DB_HOST'),
        database=os.getenv('POSTGRES_DB'),
        user=os.getenv('POSTGRES_USER'),
        password=os.getenv('POSTGRES_PASSWORD'),
        port=os.getenv('DB_PORT', '5432')
    )

def create_raw_schema(conn):
    """Create the raw schema and table if they don't exist"""
    with conn.cursor() as cursor:
        cursor.execute("""
        CREATE SCHEMA IF NOT EXISTS raw;
        CREATE TABLE IF NOT EXISTS raw.telegram_messages (
            id SERIAL PRIMARY KEY,
            message_data JSONB,
            scrape_date DATE,
            channel_name VARCHAR(255),
            loaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        CREATE INDEX IF NOT EXISTS idx_channel_name ON raw.telegram_messages(channel_name);
        CREATE INDEX IF NOT EXISTS idx_scrape_date ON raw.telegram_messages(scrape_date);
        """)
    conn.commit()

def process_json_file(file_path, conn, data_root):
    """Process a single JSON file and load its contents to the database"""

    # Get relative path from data_root, normalize to forward slashes
    relative_path = os.path.relpath(file_path, data_root).replace('\\', '/')

    # Extract date and channel from the relative path parts
    # Assuming folder structure: <scrape_date>/<channel_name>/<file.json>
    path_parts = relative_path.split('/')
    if len(path_parts) < 3:
        print(f"Skipping file with unexpected path format: {relative_path}")
        return 0

    scrape_date_str = path_parts[0]
    channel_name = path_parts[1]

    try:
        scrape_date = datetime.strptime(scrape_date_str, '%Y-%m-%d').date()
    except ValueError:
        print(f"Invalid scrape date format in path: {scrape_date_str}")
        return 0

    with conn.cursor() as cursor:
        # Check if this file (by relative path) has already been loaded
        cursor.execute("""
            SELECT 1 FROM raw.telegram_messages
            WHERE message_data->'scrape_metadata'->>'source_path' = %s
            LIMIT 1
        """, (relative_path,))
        if cursor.fetchone():
            print(f"Skipping already loaded file: {relative_path}")
            return 0

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            messages = json.load(f)
    except (json.JSONDecodeError, FileNotFoundError) as e:
        print(f"Error processing {relative_path}: {e}")
        return 0

    with conn.cursor() as cursor:
        for message in messages:
            # Add metadata including full relative path to uniquely identify source file
            message['scrape_metadata'] = {
                'scrape_date': scrape_date.isoformat(),
                'channel_name': channel_name,
                'source_path': relative_path
            }

            cursor.execute("""
                INSERT INTO raw.telegram_messages 
                    (message_data, scrape_date, channel_name) 
                VALUES (%s, %s, %s)
            """,
            (json.dumps(message), scrape_date, channel_name))

    print(f"Loaded {len(messages)} messages from {relative_path}")
    return len(messages)

def load_scraped_data(data_root):
    """Main function to load all scraped data"""
    conn = get_db_connection()
    create_raw_schema(conn)

    total_messages = 0
    processed_files = 0

    for root, _, files in os.walk(data_root):
        for file in files:
            if file.endswith('.json'):
                file_path = os.path.join(root, file)
                count = process_json_file(file_path, conn, data_root)
                if count > 0:
                    total_messages += count
                    processed_files += 1
                    if processed_files % 10 == 0:
                        print(f"Processed {processed_files} files ({total_messages} messages)")

    conn.commit()
    conn.close()
    print(f"\nFinished! Processed {processed_files} files with {total_messages} total messages.")

if __name__ == "__main__":
    data_root = os.path.join('data', 'raw', 'telegram_messages')
    load_scraped_data(data_root)
