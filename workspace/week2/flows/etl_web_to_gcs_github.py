from pathlib import Path
import pandas as pd
from prefect import flow, task
from prefect_gcp.cloud_storage import GcsBucket
import os

@task(retries=3)
def fetch(dataset_url: str) -> pd.DataFrame:
    """Read taxi data from web into pandas DataFrame"""

    df = pd.read_csv(dataset_url)

    return df

@task(log_prints=True)
def clean(df: pd.DataFrame) -> pd.DataFrame:
    """Fix dtype issues"""
    if 'tpep_pickup_datetime' in df.columns:
        df['tpep_pickup_datetime'] = pd.to_datetime(df['tpep_pickup_datetime'])
        df['tpep_dropoff_datetime'] = pd.to_datetime(df['tpep_dropoff_datetime'])
    else:
        df['lpep_pickup_datetime'] = pd.to_datetime(df['lpep_pickup_datetime'])
        df['lpep_dropoff_datetime'] = pd.to_datetime(df['lpep_dropoff_datetime'])
    
    print(df.head(2))
    print(f"columns: {df.dtypes}")
    print(f"rows: {len(df)}")
    
    return df

@task()
def write_gcs(path: Path, dataset_file: str) -> None:
    """Uploading local parquet file to GCS"""
    gcs_path=f"data/green/{dataset_file}.parquet"
    gcs_block = GcsBucket.load("dez-gcs")
    gcs_block.upload_from_path(from_path=f"{path}", to_path=gcs_path)
    return

@task(log_prints=True)
def write_local(df: pd.DataFrame, color: str, dataset_file: str) -> Path:
    """write Dataframe out locally as parquet file"""

    absolute_path = "/mnt/DSCRGS/data-engineering-zoomcamp/workspace/week2/data/green"
    
    path = Path(f"{absolute_path}/{dataset_file}.parquet")
    print(f"path: {path}")
    df.to_parquet(path, compression="gzip")
    return path

@flow()
def etl_web_to_gcs_github() -> None:
    """The main ETL function"""
    color = "green"
    year = 2019
    month = 4
    dataset_file = f"{color}_tripdata_{year}-{month:02}"
    dataset_url = f"https://github.com/DataTalksClub/nyc-tlc-data/releases/download/{color}/{dataset_file}.csv.gz"
    
    df = fetch(dataset_url)
    df_clean = clean(df)
    path = write_local(df_clean, color, dataset_file)
    write_gcs(path, dataset_file)

if __name__ == '__main__':
    etl_web_to_gcs_github()