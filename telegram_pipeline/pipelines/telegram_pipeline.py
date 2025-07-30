from dagster import op
from dagster import job
from dagster import Definitions
import subprocess

@op
def scrape_telegram_data():
    subprocess.run(["python", "scripts/data_scraping.py"], check=True)
    return "done"

@op
def load_raw_to_postgres(_scrape_output):
    subprocess.run(["python", "scripts/load_raw_data.py"], check=True)
    return "loaded"

@op
def run_dbt_transformations(_load_output):
    subprocess.run(["dbt", "run"], cwd="telegram_data", check=True)
    return "dbt run complete"

@op
def run_yolo_enrichment(_dbt_output):
    subprocess.run(["python", "scripts\image_detection.py"], check=True)
    return "yolo enriched"

@op
def load_detected_object_to_postgres(_yolo_output):
    subprocess.run(["python", "scripts\load_detected_objects.py"], check=True)
    return "loaded detected"

@job
def telegram_pipeline_job():
    # define dependency order
    scrape = scrape_telegram_data()
    load = load_raw_to_postgres(scrape)
    dbt = run_dbt_transformations(load)
    yolo = run_yolo_enrichment(dbt)
    load_detected_object_to_postgres(yolo)

defs = Definitions(
    jobs=[telegram_pipeline_job]
)