-- Query public available table
--SELECT station_id, name
--FROM bigquery-public-data.new_york_citibike.citibike_stations
--limit 100;

-- Creating external table referring to gcs path
CREATE OR REPLACE EXTERNAL TABLE `dez-20230113.nytaxi.external_yellow_tripdata`
OPTIONS (
  format = 'parquet',
  uris = ['gs://dez_data_lake_dez-20230113/data/yellow/yellow_tripdata_2019-*.parquet', 'gs://dez_data_lake_dez-20230113/data/yellow/yellow_tripdata_2020-*.parquet']
);

-- Check yellow trip data
SELECT * 
FROM `dez-20230113.nytaxi.external_yellow_tripdata` 
LIMIT 10;

-- Create a non partitioned table from external table
CREATE OR REPLACE TABLE `dez-20230113.nytaxi.external_yellow_tripdata_non_partitioned` AS
SELECT * FROM `dez-20230113.nytaxi.external_yellow_tripdata`;

-- Create a partitioned table from external table
CREATE OR REPLACE TABLE `dez-20230113.nytaxi.external_yellow_tripdata_partitioned`
PARTITION BY
  DATE(tpep_pickup_datetime) AS
SELECT * FROM `dez-20230113.nytaxi.external_yellow_tripdata`;


