https://pimylifeup.com/raspberry-pi-mysql/
https://raspberrytips.com/install-mariadb-raspberry-pi/

CREATE DATABASE dht_series;

CREATE TABLE `dht_series` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `temp_c` decimal(6,3) DEFAULT NULL,
  `hum_p` decimal(6,3) DEFAULT NULL,
  `valid` varchar(10) NOT NULL,
  `timestamp` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp(),
  `sensor_id` varchar(20) NOT NULL,
  `profile` varchar(20) NOT NULL,
  `batch_id` bigint(20) NOT NULL,
  PRIMARY KEY (`id`)
);

CREATE TABLE `dht_errors` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `error` varchar(5000) NOT NULL,
  `timestamp` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp(),
  PRIMARY KEY (`id`)
);

CREATE TABLE `dht_batch`(
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `batch_id` int(11) NOT NULL,
  `profile_id` NOT NULL, 
  `timestamp` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp(),
  PRIMARY KEY (`id`)
);
