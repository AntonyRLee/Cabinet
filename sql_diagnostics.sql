select 	sensor_id, 
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
	batch_id = 145 and 
	timestamp > date_sub(now(), interval 24 hour) group by sensor_id
;

// needs formatting
select sensor_id, count(*) as num, min(timestamp) as start, avg(temp_c) as temp,std(temp_c) as std_t, min(temp_c) as min_t, max(temp_c) as max_t, avg(hum_p) as hum, std(hum_p) as std_h, min(hum_p) as min_h, max(hum_p) as max_h from dht_series where valid = 1 and batch_id = 145 and timestamp > date_sub(now(), interval 24 hour) group by sensor_id;
