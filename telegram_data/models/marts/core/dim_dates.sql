-- models/marts/core/dim_dates.sql

{{ config(
    materialized = 'table',
    schema = 'mart'
) }}

WITH dates AS (
    SELECT DISTINCT
        DATE(message_timestamp) AS date
    FROM {{ ref('stg_telegram_messages') }}
)

SELECT
    date,
    EXTRACT(YEAR FROM date) AS year,
    EXTRACT(MONTH FROM date) AS month,
    EXTRACT(DAY FROM date) AS day,
    TO_CHAR(date, 'Day') AS day_of_week,
    TO_CHAR(date, 'Month') AS month_name,
    CASE WHEN EXTRACT(ISODOW FROM date) < 6 THEN TRUE ELSE FALSE END AS is_weekday
FROM dates
