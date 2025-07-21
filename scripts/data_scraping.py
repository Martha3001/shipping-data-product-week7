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


# Function to scrape data and images from a single channel
async def scrape_channel(client, channel_username, scrape_date):
    logging.info(f"Starting to retrieve messages from channel: {channel_username}")
    channel_clean = channel_username.lstrip('@')
    out_dir = os.path.join('data', 'raw', 'telegram_messages', scrape_date, channel_clean)
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, f'{channel_clean}.json')
    # If JSON file exists, skip scraping
    if os.path.exists(out_path):
        logging.info(f"Skipping channel {channel_username} for {scrape_date}: already scraped.")
        return
    all_messages = []
    image_dir = os.path.join(out_dir, 'images')
    try:
        async for message in client.iter_messages(channel_username, limit=200):
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
                os.makedirs(image_dir, exist_ok=True)
                image_path = os.path.join(image_dir, f"{message.id}.jpg")
                if os.path.exists(image_path):
                    message_data['image_path'] = image_path
                    logging.info(f"Image for message {message.id} in channel {channel_username} already exists. Skipping download.")
                else:
                    try:
                        await client.download_media(message, image_path)
                        message_data['image_path'] = image_path
                        logging.info(f"Downloaded image for message {message.id} in channel {channel_username}")
                    except Exception as img_err:
                        logging.error(f"Failed to download image for message {message.id} in channel {channel_username}: {img_err}")
            all_messages.append(message_data)
        # Write JSON only if messages were scraped
        with open(out_path, 'w', encoding='utf-8') as f:
            json.dump(all_messages, f, ensure_ascii=False, indent=2)
        logging.info(f"Successfully scraped and stored data for channel: {channel_username} on {scrape_date}")
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