from dagster import op, job, Definitions, ScheduleDefinition
import subprocess
import sys
python_executable = sys.executable

@op
def scrape_telegram_data():
    subprocess.run([python_executable, r".\scripts\data_scraping.py"], check=True)
    return "done"

@op
def run_yolo_enrichment(_dbt_output):
    subprocess.run([python_executable, r".\scripts\image_detection.py"], check=True)
    return "yolo enriched"

@op
def load_raw_to_postgres(_scrape_output):
    subprocess.run([python_executable, r".\scripts\load_raw_data.py"], check=True)
    return "loaded"

@op
def load_detected_object_to_postgres(_yolo_output):
    subprocess.run([python_executable, r".\scripts\load_detected_objects.py"], check=True)
    return "loaded detected"

@op
def run_dbt_transformations(_load_output):
    subprocess.run(["dbt", "run"], cwd="telegram_data", check=True)
    return "dbt run complete"

@job
def telegram_pipeline_job():
    # define order
    scrape = scrape_telegram_data()
    yolo = run_yolo_enrichment(scrape)
    load = load_raw_to_postgres(yolo)
    load_detect = load_detected_object_to_postgres(load)
    run_dbt_transformations(load_detect)

daily_pipeline_schedule = ScheduleDefinition(
    job=telegram_pipeline_job,
    cron_schedule="15 23 * * *",  
    name="daily_data_pipeline_schedule"
)

defs = Definitions(
    jobs=[telegram_pipeline_job],
    schedules=[daily_pipeline_schedule]
)
