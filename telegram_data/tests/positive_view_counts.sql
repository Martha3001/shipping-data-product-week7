-- Returns messages with invalid view counts
SELECT
    message_id,
    view_count
FROM {{ ref('stg_telegram_messages') }}
WHERE view_count < 0