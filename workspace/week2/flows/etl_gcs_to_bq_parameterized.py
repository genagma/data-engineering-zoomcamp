from pathlib import Path
import pandas as pd
from prefect import flow, task
from prefect_gcp.cloud_storage import GcsBucket
from prefect_gcp import GcpCredentials

@task(retries=3)
def extract_from_gcs(color: str, year: int, month: list) -> Path:
    """Download trip data from GCS"""
    gcs_path = f"{color}/{color}_tripdata_{year}-{month:02}.parquet"
    gcs_block = GcsBucket.load("dez-gcs")
    gcs_block.get_directory(from_path=gcs_path, local_path=f"data/")
    return Path(f"data/{gcs_path}")

@task()
def write_bq(df: pd.DataFrame) -> None:
    """Write DataFrame to BigQuery"""

    gcp_credentials_block = GcpCredentials.load("dez-gcp-creds")

    df.to_gbq(
        destination_table="dez-20230113.dezoomcamp.rides",
        project_id="dez-20230113",
        credentials=gcp_credentials_block.get_credentials_from_service_account(),
        chunksize=500_000,
        if_exists="append"
    )

@flow(log_prints=True)
def el_gcs_to_bq(year: int, month: int, color: str) -> int:
    """Main ETL flow to load data into Big Query"""
    
    path = extract_from_gcs(color, year, month)
    df = pd.read_parquet(path)
    
    write_bq(df)
    return len(df)

@flow(log_prints=True)
def el_parent_flow(
    months: list[int] = [2, 3], year: int = 2019, color: str = "yellow"
):
    total_rows = 0

    for month in months:
        total_rows += el_gcs_to_bq(year, month, color)
    
    print(f"Total number of rows: {total_rows}")

if __name__==  "__main__":
    months = [2, 3]
    year = 2019
    color = "yellow"
    el_parent_flow(months, year, color)