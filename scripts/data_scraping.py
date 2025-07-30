import os
import json
import logging
from datetime import datetime
from dotenv import load_dotenv
from telethon import TelegramClient
from telethon.tl.types import MessageMediaPhoto

load_dotenv('.env')
api_id = os.getenv('TG_API_ID')
api_hash = os.getenv('TG_API_HASH')

# Setup logging
logging.basicConfig(
    filename='scraping.log',
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(message)s'
)


# Function to scrape data and images
async def scrape_channel(client, channel_username, scrape_date):
    logging.info(f"Starting to retrieve messages from channel: {channel_username}")
    channel_clean = channel_username.lstrip('@')
    out_dir = os.path.join('data', 'raw', 'telegram_messages', scrape_date, channel_clean)
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, f'{channel_clean}.json')
    image_dir = os.path.join(out_dir, 'images')
    os.makedirs(image_dir, exist_ok=True)

    # Load previously scraped message IDs from all dates for this channel
    scraped_ids = set()
    existing_messages = []
    raw_dir = os.path.join('data', 'raw', 'telegram_messages')
    if os.path.exists(raw_dir):
        for date_folder in os.listdir(raw_dir):
            date_path = os.path.join(raw_dir, date_folder)
            channel_path = os.path.join(date_path, channel_clean, f'{channel_clean}.json')
            if os.path.exists(channel_path):
                try:
                    with open(channel_path, 'r', encoding='utf-8') as f:
                        msgs = json.load(f)
                        scraped_ids.update(msg['message_id'] for msg in msgs)
                        # If this is today's file, keep the messages for later append
                        if channel_path == out_path:
                            existing_messages = msgs
                except Exception as e:
                    logging.warning(f"Could not load JSON {channel_path} for {channel_username}: {e}")
    logging.info(f"Loaded {len(scraped_ids)} total previously scraped messages from all dates for {channel_username}")

    new_messages = []

    try:
        async for message in client.iter_messages(channel_username, limit=200):
            if message.id in scraped_ids:
                continue  # Skip already scraped messages

            message_data = {
                'channel': channel_username,
                'message_id': message.id,
                'sender_id': message.sender_id,
                'message_content': message.text,
                'timestamp': message.date.isoformat(),
                'views': message.views
            }

            # Download images if present
            if message.media and isinstance(message.media, MessageMediaPhoto):
                image_path = os.path.join(image_dir, f"{message.id}.jpg")
                if os.path.exists(image_path):
                    message_data['image_path'] = image_path
                    logging.info(f"Image for message {message.id} in channel {channel_username} already exists.")
                else:
                    try:
                        await client.download_media(message, image_path)
                        message_data['image_path'] = image_path
                        logging.info(f"Downloaded image for message {message.id} in channel {channel_username}")
                    except Exception as img_err:
                        logging.error(f"Failed to download image for message {message.id} in channel {channel_username}: {img_err}")

            new_messages.append(message_data)

        # Only save if there are new messages
        if new_messages:
            all_messages = existing_messages + new_messages
            # Remove duplicates by message_id
            unique_msgs = {msg['message_id']: msg for msg in all_messages}
            with open(out_path, 'w', encoding='utf-8') as f:
                json.dump(list(unique_msgs.values()), f, ensure_ascii=False, indent=2)
            logging.info(f"Saved {len(new_messages)} new messages for {channel_username}")
        else:
            logging.info(f"No new messages found for {channel_username}")

    except Exception as e:
        logging.error(f"Error scraping channel {channel_username} on {scrape_date}: {e}")


client = TelegramClient('scraping_session', api_id, api_hash)


async def main():
    await client.start()
    # List of channels to scrape
    channels = [
        '@CheMed123',
        '@lobelia4cosmetics',
        '@tikvahpharma'
    ]
    scrape_date = datetime.now().strftime('%Y-%m-%d')
    for channel in channels:
        await scrape_channel(client, channel, scrape_date)

if __name__ == "__main__":
    with client:
        client.loop.run_until_complete(main())