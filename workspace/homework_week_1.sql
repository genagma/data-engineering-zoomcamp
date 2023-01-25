-- Question 3. Count records 
select count(*)
from green_taxi_data
where lpep_pickup_datetime::date = date '2019-01-15'
and lpep_dropoff_datetime::date = date '2019-01-15';

-- Question 4. Largest trip for each day 
select lpep_pickup_datetime::date as day,
        max(trip_distance) as max_trip_distance
from green_taxi_data
group by  lpep_pickup_datetime::date
order by max_trip_distance desc;

-- Question 5. The number of passengers 
select passenger_count,
       count(*)
from green_taxi_data
where lpep_pickup_datetime::date = date '2019-01-01'
and passenger_count in (2, 3)
group by passenger_count;

-- Question 6. Largest tip 
select t2."Zone" pickup_zone, 
       t3."Zone" dropoff_zone
	   , max(tip_amount) max_tip_amount
from green_taxi_data t1
    join zones t2
 		on t1."PULocationID" = t2."LocationID"
	join zones t3
		on t1."DOLocationID" = t3."LocationID"
where t2."Zone"='Astoria'
group by t2."Zone", t3."Zone"
order by max_tip_amount desc;


