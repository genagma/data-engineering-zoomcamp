import io
import os
import pandas as pd
import pyarrow.csv as pv
import pyarrow.parquet as pq
import pyarrow as pa
import logging
from google.cloud import storage
import wget

"""
Pre-reqs: 
1. `pip install pandas pyarrow google-cloud-storage`
2. Set GOOGLE_APPLICATION_CREDENTIALS to your project/service-account key
3. Set GCP_GCS_BUCKET as your bucket or change default value of BUCKET
"""

# services = ['fhv','green','yellow']
init_url = 'https://github.com/DataTalksClub/nyc-tlc-data/releases/download'

# switch out the bucketname
BUCKET = os.environ.get("GCP_GCS_BUCKET", "dez_data_lake_dez-20230113")

# Relative data directory path
relative_data_directory = '../../data'

table_schema_green = pa.schema(
    [
        ('VendorID',pa.string()),
        ('lpep_pickup_datetime',pa.timestamp('s')),
        ('lpep_dropoff_datetime',pa.timestamp('s')),
        ('store_and_fwd_flag',pa.string()),
        ('RatecodeID',pa.int64()),
        ('PULocationID',pa.int64()),
        ('DOLocationID',pa.int64()),
        ('passenger_count',pa.int64()),
        ('trip_distance',pa.float64()),
        ('fare_amount',pa.float64()),
        ('extra',pa.float64()),
        ('mta_tax',pa.float64()),
        ('tip_amount',pa.float64()),
        ('tolls_amount',pa.float64()),
        ('ehail_fee',pa.float64()),
        ('improvement_surcharge',pa.float64()),
        ('total_amount',pa.float64()),
        ('payment_type',pa.int64()),
        ('trip_type',pa.int64()),
        ('congestion_surcharge',pa.float64()),
    ]
)

table_schema_yellow = pa.schema(
   [
        ('VendorID', pa.string()), 
        ('tpep_pickup_datetime', pa.timestamp('s')), 
        ('tpep_dropoff_datetime', pa.timestamp('s')), 
        ('passenger_count', pa.int64()), 
        ('trip_distance', pa.float64()), 
        ('RatecodeID', pa.string()), 
        ('store_and_fwd_flag', pa.string()), 
        ('PULocationID', pa.int64()), 
        ('DOLocationID', pa.int64()), 
        ('payment_type', pa.int64()), 
        ('fare_amount',pa.float64()), 
        ('extra',pa.float64()), 
        ('mta_tax', pa.float64()), 
        ('tip_amount', pa.float64()), 
        ('tolls_amount', pa.float64()), 
        ('improvement_surcharge', pa.float64()), 
        ('total_amount', pa.float64()), 
        ('congestion_surcharge', pa.float64())]

)

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

table_schema_fhv_2020 = pa.schema(
   [
        ('dispatching_base_num', pa.string()), 
        ('pickup_datetime', pa.timestamp('s')), 
        ('dropoff_datetime', pa.timestamp('s')), 
        ('PUlocationID', pa.int64()), 
        ('DOlocationID', pa.int64()), 
        ('SR_Flag', pa.int64()), 
        ('Affiliated_base_number', pa.string())]

)

def format_to_parquet(src_file, service, year):
    if not src_file.endswith('.csv.gz'):
        logging.error("Can only accept source files in CSV format, for the moment")
        return
    
    parse_options = pv.ParseOptions(delimiter=',', invalid_row_handler=skip_comment, ignore_empty_lines=True)
    read_options = pv.ReadOptions(encoding='latin1')
    convert_options = pv.ConvertOptions(strings_can_be_null=True)
    print(src_file)
    table = pv.read_csv(src_file, parse_options=parse_options, read_options=read_options, convert_options=convert_options)

    if service == 'yellow':
        table = table.cast(table_schema_yellow)
    
    elif service == 'green':
        table = table.cast(table_schema_green)

    elif service == 'fhv' and year == 2019:
        table = table.cast(table_schema_fhv_2019)
    
    elif service == 'fhv' and year == 2020:
        table = table.cast(table_schema_fhv_2020)

    pq.write_table(table, src_file.replace('.csv.gz', '.parquet'), compression='gzip')

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

def skip_comment(row):
    if row.text.startswith("# "):
        return 'skip'
    else:
        return 'error'

def web_to_gcs(year, service):
    for i in range(12):
        
        # sets the month part of the file_name string
        month = '0'+str(i+1)
        month = month[-2:]

        # csv file_name 
        file_name = service + '_tripdata_' + year + '-' + month + '.csv.gz'

        init_url_service = f'{init_url}/{service}/'

        # download it using requests via a pandas df
        print(init_url_service + file_name)
        request_url = init_url_service + file_name
        output_file = f"{relative_data_directory}/{file_name}"
        print(output_file)
        # Download the csv
        #os.system(f'wget {request_url} -O {output_file}')
        #wget.download(request_url, output_file)

        # read it back into a parquet file
        #df = pd.read_csv(output_file, low_memory=False, encoding='latin1')
        #print(df.head())
        #parquetized = format_to_parquet(output_file, service, year)

        # upload it to gcs 
        upload_to_gcs(BUCKET, f"data/{service}/{file_name}", output_file) #file_name)
        print(f"GCS: data/{service}/{file_name}")


#web_to_gcs('2019', 'green')
#web_to_gcs('2020', 'green')
#web_to_gcs('2019', 'yellow')
#web_to_gcs('2020', 'yellow')
web_to_gcs('2019', 'fhv')
#web_to_gcs('2020', 'fhv')
