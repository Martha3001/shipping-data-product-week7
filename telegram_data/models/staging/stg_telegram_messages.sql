{{
  config(
    materialized='view',
    schema='staging'
  )
}}

SELECT
    message_data->>'message_id' AS message_id,
    (message_data->>'timestamp')::TIMESTAMP AS message_timestamp,
    scrape_date,
    channel_name,
    message_data->>'message_content' AS message_text,
    message_data->>'sender_id' AS sender_id,
    (message_data->>'views')::INTEGER AS view_count,
    message_data->>'image_path' AS image_path,
    CASE WHEN message_data->>'image_path' IS NOT NULL THEN TRUE ELSE FALSE END AS has_image,
    LENGTH(message_data->>'message_content') AS message_length,
    loaded_at
FROM {{ source('raw', 'telegram_messages') }}