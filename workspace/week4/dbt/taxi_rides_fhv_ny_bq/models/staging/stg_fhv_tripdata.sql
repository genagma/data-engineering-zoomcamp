{{ config(materialized='view') }}

select 
     -- identifiers
    dispatching_base_num,
    Affiliated_base_number,
    cast(PUlocationID as integer) as  pickup_locationid,
    cast(DOlocationID as integer) as dropoff_locationid,
        
    -- timestamps
    cast(pickup_datetime as timestamp) as pickup_datetime,
    cast(dropOff_datetime as timestamp) as dropoff_datetime,
    
    -- trip info
    SR_Flag
    
from {{ source('staging','fhv_tripdata_non_partitioned_clustered') }}
where CAST(pickup_datetime AS DATE) >= CAST('2019/01/01' AS DATE FORMAT 'YYYY/MM/DD')
and CAST(pickup_datetime AS DATE) <= CAST('2019/12/31' AS DATE FORMAT 'YYYY/MM/DD')

-- dbt build --m <model.sql> --var 'is_test_run: false'
{% if var('is_test_run', default=true) %}

  limit 100

{% endif %}