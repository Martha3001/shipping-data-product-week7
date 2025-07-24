# load_scraped_data.py
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

def process_json_file(file_path, conn):
    """Process a single JSON file and load its contents to the database"""
    try:
        # Extract date and channel from file path
        path_parts = file_path.split(os.sep)
        scrape_date = datetime.strptime(path_parts[-3], '%Y-%m-%d').date()
        channel_name = path_parts[-2]
        
        with open(file_path, 'r', encoding='utf-8') as f:
            messages = json.load(f)
            
            with conn.cursor() as cursor:
                for message in messages:
                    # Add metadata to each message
                    message['scrape_metadata'] = {
                        'scrape_date': scrape_date.isoformat(),
                        'channel_name': channel_name,
                        'source_file': os.path.basename(file_path)
                    }
                    
                    cursor.execute("""
                    INSERT INTO raw.telegram_messages 
                        (message_data, scrape_date, channel_name) 
                    VALUES (%s, %s, %s)
                    """, 
                    (json.dumps(message), scrape_date, channel_name))
                    
        return len(messages)
    except (json.JSONDecodeError, IndexError, ValueError) as e:
        print(f"Error processing {file_path}: {e}")
        return 0

def load_scraped_data(data_root):
    """Main function to load all scraped data"""
    conn = get_db_connection()
    create_raw_schema(conn)
    
    total_messages = 0
    processed_files = 0
    
    # Walk through the directory structure
    for root, _, files in os.walk(data_root):
        for file in files:
            if file.endswith('.json'):
                file_path = os.path.join(root, file)
                count = process_json_file(file_path, conn)
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