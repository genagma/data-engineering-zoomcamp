-- Create an external table using the fhv 2019 data
CREATE OR REPLACE EXTERNAL TABLE `dez-20230113.nytaxi.external_fhv_tripdata`
OPTIONS (
  format = 'csv',
  uris = ['gs://dez_data_lake_dez-20230113/data/fhv/fhv_tripdata_2019-*.csv.gz']
);


-- Create a table in BQ using the fhv 2019 data (do not partition or cluster this table)
CREATE OR REPLACE TABLE `dez-20230113.nytaxi.fhv_tripdata_non_partitioned_clustered` AS
SELECT * FROM `dez-20230113.nytaxi.external_fhv_tripdata`;

-- What is the count for fhv vehicle records for year 2019?
SELECT COUNT(1) FROM `dez-20230113.nytaxi.fhv_tripdata_non_partitioned_clustered`;

-- Write a query to count the distinct number of affiliated_base_number for the entire dataset on both the tables.
-- What is the estimated amount of data that will be read when this query is executed on the External Table and the Table?
SELECT COUNT(DISTINCT affiliated_base_number) FROM `dez-20230113.nytaxi.external_fhv_tripdata`;

SELECT COUNT(DISTINCT affiliated_base_number) FROM `dez-20230113.nytaxi.fhv_tripdata_non_partitioned_clustered`;

-- How many records have both a blank (null) PUlocationID and DOlocationID in the entire dataset?
SELECT COUNT(1) 
FROM `dez-20230113.nytaxi.fhv_tripdata_non_partitioned_clustered` 
WHERE PUlocationID IS NULL
AND DOlocationID IS NULL;

-- What is the best strategy to optimize the table if query always filter by pickup_datetime and order by affiliated_base_number?
-- Partition by pickup_datetime Cluster on affiliated_base_number
-- Creating a partition and cluster table
CREATE OR REPLACE TABLE `dez-20230113.nytaxi.fhv_tripdata_partitoned_clustered`
PARTITION BY DATE(pickup_datetime)
CLUSTER BY affiliated_base_number AS
SELECT * FROM `dez-20230113.nytaxi.fhv_tripdata_non_partitioned_clustered`;

-- Implement the optimized solution you chose for question 4. 
-- Write a query to retrieve the distinct affiliated_base_number between pickup_datetime 2019/03/01 and 2019/03/31 (inclusive).
-- Use the BQ table you created earlier in your from clause and note the estimated bytes. 
SELECT DISTINCT affiliated_base_number
FROM `dez-20230113.nytaxi.fhv_tripdata_non_partitioned_clustered`
WHERE CAST(pickup_datetime AS DATE) >= CAST('2019/03/01' AS DATE FORMAT 'YYYY/MM/DD')
AND CAST(pickup_datetime AS DATE) <= CAST('2019/03/31' AS DATE FORMAT 'YYYY/MM/DD');

SELECT DISTINCT affiliated_base_number
FROM `dez-20230113.nytaxi.fhv_tripdata_partitoned_clustered`
WHERE CAST(pickup_datetime AS DATE) >= CAST('2019/03/01' AS DATE FORMAT 'YYYY/MM/DD')
AND CAST(pickup_datetime AS DATE) <= CAST('2019/03/31' AS DATE FORMAT 'YYYY/MM/DD');
