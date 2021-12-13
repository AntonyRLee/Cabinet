use dht_series;

SET @max_batch = (select max(batch_id) from dht_series);

select 	
	sensor_id, 
	count(*) as num, 
	min(timestamp) as start, 
	avg(temp_c) as temp, 
	std(temp_c) as std_t, 
	avg(hum_p) as hum, 
	std(hum_p) as std_h, 
	min(hum_p) as min, 
	max(hum_p) as max 
from 	dht_series 
where 	valid = 1 and 
	batch_id = @max_batch and 
	timestamp > date_sub(now(), interval 24 hour) 
group by 
	sensor_id
;

select 	
	sensor_id, 
	count(*) as num, 
	min(timestamp) as start, 
	avg(temp_c) as temp, 
	std(temp_c) as std_t, 
	avg(hum_p) as hum, 
	std(hum_p) as std_h, 
	min(hum_p) as min, 
	max(hum_p) as max,
	date(timestamp) as date
from 	
	dht_series 
where 	
	valid = 1 
		and 
	batch_id = @max_batch
group by 
	date(timestamp),
	sensor_id
order by
	date(timestamp) desc,
	sensor_id
;
