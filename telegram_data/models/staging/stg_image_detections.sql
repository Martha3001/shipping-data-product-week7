{{
  config(
    materialized='view',
    schema='staging'
  )
}}

SELECT
    id AS detection_id,
    message_id,
    detected_object_class,
    confidence_score,
    image_filename,
    relative_path,
    processed_at,
    loaded_at
FROM {{ source('raw', 'image_detections') }}
