{{
  config(
    materialized='table',
    schema='mart'
  )
}}

SELECT
    detections.message_id,
    detections.detected_object_class,
    detections.confidence_score,
    detections.image_filename,
    detections.relative_path,
    detections.processed_at,
    detections.loaded_at

FROM {{ ref('stg_image_detections') }} AS detections
-- Optional join if you want to ensure message exists in fct_messages
INNER JOIN {{ ref('fct_messages') }} AS messages
  ON CAST(detections.message_id AS integer) = CAST(messages.message_id AS integer)
