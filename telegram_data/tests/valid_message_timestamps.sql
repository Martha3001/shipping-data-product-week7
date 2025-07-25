-- Returns messages with timestamps outside expected range
SELECT
    message_id,
    message_timestamp
FROM {{ ref('stg_telegram_messages') }}
WHERE 
    message_timestamp < '2020-01-01'::timestamp
    OR message_timestamp > CURRENT_TIMESTAMP + INTERVAL '1 day'