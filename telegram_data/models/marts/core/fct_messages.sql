-- models/marts/core/fct_messages.sql

{{ config(
    materialized = 'table',
    schema = 'mart'
) }}

WITH base AS (
    SELECT *
    FROM {{ ref('stg_telegram_messages') }}
)

SELECT
    message_id,
    message_timestamp,
    scrape_date,
    channel_name AS channel_id,
    sender_id,
    message_text,
    view_count,
    has_image,
    message_length,
    loaded_at
FROM base
