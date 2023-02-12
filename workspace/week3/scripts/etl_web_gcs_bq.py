import io
import os
import pandas as pd
import pyarrow.csv as pv
import pyarrow.parquet as pq
import pyarrow as pa
import logging
import wget
from google.cloud import storage
from google.cloud import bigquery
from prefect import flow, task
from prefect_gcp.cloud_storage import GcsBucket
from prefect_gcp import GcpCredentials

"""
Pre-reqs: 
1. `pip install pandas pyarrow google-cloud-storage`
2. Set GOOGLE_APPLICATION_CREDENTIALS to your project/service-account key
3. Set GCP_GCS_BUCKET as your bucket or change default value of BUCKET
"""

init_url = 'https://github.com/DataTalksClub/nyc-tlc-data/releases/download'

# switch out the bucketname
BUCKET = os.environ.get("GCP_GCS_BUCKET", "dez_data_lake_dez-20230113")

# Relative data directory path
relative_data_directory = '../../data'

# Absolute data directory path
absolute_path_data_directory = "/mnt/DSCRGS/data-engineering-zoomcamp/workspace/data"
    

table_schema_fhv_2019 = pa.schema(
   [
        ('dispatching_base_num', pa.string()), 
        ('pickup_datetime', pa.timestamp('s')), 
        ('dropOff_datetime', pa.timestamp('s')), 
        ('PUlocationID', pa.int64()), 
        ('DOlocationID', pa.int64()), 
        ('SR_Flag', pa.int64()), 
        ('Affiliated_base_number', pa.string())]

)

@task()
def format_to_parquet(src_file, service, year):
    if not src_file.endswith('.csv.gz'):
        logging.error("Can only accept source files in CSV format, for the moment")
        return
    
    parse_options = pv.ParseOptions(delimiter=',', invalid_row_handler=skip_comment, ignore_empty_lines=True)
    read_options = pv.ReadOptions(encoding='latin1')
    convert_options = pv.ConvertOptions(strings_can_be_null=True)
    print(src_file)
    table = pv.read_csv(src_file, parse_options=parse_options, read_options=read_options, convert_options=convert_options)

    if service == 'fhv' and year == 2019:
        table = table.cast(table_schema_fhv_2019)
    
    pq.write_table(table, src_file.replace('.csv.gz', '.parquet'), compression='gzip')

@task()
def upload_to_gcs(bucket, object_name, local_file):
    """
    Ref: https://cloud.google.com/storage/docs/uploading-objects#storage-upload-object-python
    """
    # # WORKAROUND to prevent timeout for files > 6 MB on 800 kbps upload speed.
    # # (Ref: https://github.com/googleapis/python-storage/issues/74)
    # storage.blob._MAX_MULTIPART_SIZE = 5 * 1024 * 1024  # 5 MB
    # storage.blob._DEFAULT_CHUNKSIZE = 5 * 1024 * 1024  # 5 MB

    client = storage.Client()
    bucket = client.bucket(bucket)
    blob = bucket.blob(object_name)
    blob.upload_from_filename(local_file)

@task()
def create_external_table(service, file_name):
    client = bigquery.Client()

    project = 'dez-20230113'
    dataset_id = 'nytaxi'
    table_id = "external_fhv_tripdata_flow"
    
    # Configure the external data source
    dataset_ref = bigquery.DatasetReference(project, dataset_id)
    
    schema = [
        bigquery.SchemaField("dispatching_base_num", "STRING"),
        bigquery.SchemaField("pickup_datetime", "TIMESTAMP"),
        bigquery.SchemaField("dropOff_datetime", "TIMESTAMP"),
        bigquery.SchemaField("PUlocationID", "INT64"),
        bigquery.SchemaField("DOlocationID", "INT64"),
        bigquery.SchemaField("SR_Flag", "INT64"),
        bigquery.SchemaField("Affiliated_base_number", "STRING"),
    ]
    table = bigquery.Table(dataset_ref.table(table_id), schema=schema)
    external_config = bigquery.ExternalConfig("CSV")
    external_config.source_uris = [
        f"gs://dez_data_lake_dez-20230113/data/{service}/{file_name}"
    ]
    external_config.options.skip_leading_rows = 1  # optionally skip header row
    table.external_data_configuration = external_config

    # Create a permanent table linked to the GCS file
    table = client.create_table(table)  # API request

    # Example query to find states starting with 'W'
    sql = 'SELECT COUNT(1) as count FROM `{}.{}`'.format(dataset_id, table_id)

    query_job = client.query(sql)  # API request

    results = query_job.result()
    for row in results:
        print("Count: {}".format(row.count))

@task()
def create_big_query_table():
    # Construct a BigQuery client object.
    client = bigquery.Client()

    project = 'dez-20230113'
    dataset_id = 'nytaxi'
    table_id = f"{project}.{dataset_id}.big_query_fhv_tripdata_flow"

    job_config = bigquery.QueryJobConfig(destination=table_id)

    sql = """
        SELECT * FROM `dez-20230113.nytaxi.external_fhv_tripdata_flow`;
    """

    # Start the query, passing in the extra configuration.
    query_job = client.query(sql, job_config=job_config)  # Make an API request.
    query_job.result()  # Wait for the job to complete.

    print("Query results loaded to the table {}".format(table_id))

def skip_comment(row):
    if row.text.startswith("# "):
        return 'skip'
    else:
        return 'error'

@flow(log_prints=True)
def web_to_gcs(month, year, service):

    # csv file_name 
    file_name = service + '_tripdata_' + str(year) + '-' + month + '.csv.gz'

    init_url_service = f'{init_url}/{service}/'

    # download it using requests via a pandas df
    print(init_url_service + file_name)
    request_url = init_url_service + file_name
    output_file = f"{absolute_path_data_directory}/{file_name}"
    print(output_file)
    
    # Download the csv
    wget.download(request_url, output_file)

    # read it back into a parquet file
    parquetized = format_to_parquet(output_file, service, year)

    # upload it to gcs 
    print(f"GCS: data/{service}/{file_name}")
    upload_to_gcs(BUCKET, f"data/{service}/{file_name}", output_file)

    # Create a external table
    create_external_table(service, file_name)

    # Create a external table
    create_big_query_table()



@flow(log_prints=True)
def etl_parent_flow(month: str, year: int, service: str):
    web_to_gcs(month, year, service)

if __name__ == "__main__":
    month = '01'
    year = 2019
    service = "fhv"
    etl_parent_flow(month, year, service)
