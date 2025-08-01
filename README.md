# Ethiopian Medical Business Data Platform

## Overview

This project implements an end-to-end data pipeline for analyzing Ethiopian medical business data from public Telegram channels. The platform extracts, processes, and enriches Telegram data to provide insights about medical product trends, channel activity, and visual content patterns.

## Key Features

- **Data Collection**: Scrapes messages and images from multiple Telegram channels
- **Data Processing**: Transforms raw data into a structured star schema using dbt
- **Image Analysis**: Detects medical products in images using YOLOv8
- **Analytical API**: Provides business insights through FastAPI endpoints
- **Orchestration**: Manages the complete pipeline with Dagster

## Technical Stack

- **Data Extraction**: Telethon (Telegram API)
- **Data Storage**: PostgreSQL (Data Warehouse)
- **Data Transformation**: dbt (Data Build Tool)
- **Object Detection**: YOLOv8
- **API Framework**: FastAPI
- **Orchestration**: Dagster
- **Infrastructure**: Docker, Docker Compose

## Project Structure

```
shipping-data-product-week7
├── data/                   
│   └── raw/                    # Raw scraped data (JSON, images)
├── telegram_data/              # dbt project
│   ├── models/                 # Data models
│   ├── tests/                  # Data tests
│   └── ...                     # Other dbt files
├── scripts/                    # Processing scripts
│   ├── data_scraping.py        # Telegram scraper
│   ├── image_detection.py      # YOLO object detection
│   ├── load_raw_data.py
│   └── load_detected_objects.py
├── api/                        # FastAPI application
│   ├── main.py                 # API endpoints
│   ├── crud.py                 # Database operations
│   ├── database.py  
│   ├── models.py  
│   └── schemas.py                
├── telegram_pipeline/          # Orchestration
│   └── telegram_pipeline.py    # Dagster job definitions
├── .gitignore  
├── .dockerignore             
├── Dockerfile                  # Container configuration
├── docker-compose.yml          # Service definitions
├── requirements.txt            # Python dependencies
└── .env                        # Environment variables 
```

## Setup Instructions

### Prerequisites

- Docker and Docker Compose
- Python 3.8+
- Telegram API credentials

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/Martha3001/shipping-data-product-week7.git
   cd shipping-data-product-week7
   ```

2. Build and start containers:
   ```bash
   docker-compose up -d --build
   ```

### Accessing the API

The FastAPI service runs on http://localhost:8000 with these endpoints:

- `GET /api/reports/top-products` - Top mentioned medical products
- `GET /api/channels/{channel_name}/activity` - Channel posting activity
- `GET /api/search/messages` - Search messages by keyword

API documentation available at http://localhost:8000/docs

## Configuration

Key configuration options in `.env`:

```ini
# Telegram API
TG_API_ID=your_api_id
TG_API_HASH=your_api_hash

# Database
POSTGRES_USER=admin
POSTGRES_PASSWORD=secret
POSTGRES_DB=medical_data

```
