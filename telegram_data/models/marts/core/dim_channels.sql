-- models/marts/core/dim_channels.sql

{{ config(
    materialized = 'table',
    schema = 'mart'
) }}

SELECT DISTINCT
    channel_name AS channel_id
FROM {{ ref('stg_telegram_messages') }}
