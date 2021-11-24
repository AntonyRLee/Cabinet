# Launch pi gpio deamon via terminal
# sudo pigpiod

# Module Imports
import mariadb
import sys
import time

# module for timestamps
import datetime

# NOTE: The import has a _ not - in the module name.
from pigpio_dht import DHT22 #, DHT11

# replace pgiozero with rpi.gpio
import RPi.GPIO as GPIO

# target
T0 = 15.5 # MASTER 15
H0 = 65 # MASTER 70

#threshold
epsilon = 0.5 # MASTER 0.5
delta = 4 # MASTER 0.5

# response constants
k = 0.014
h = 0.025
m = 0.008
n = 0.045

pin_map = {
  "sensor001": 4,
  "sensor002": 23,
  "compressor": 16,
  "fan": 6,
  "heater001": 22,
  "heater002": 12,
  "dehumidifier": 5,
  "humidifier": 19,
  "spare": 25,
  "not_connected": 20
}

# log profiles
profile_on = {"profile": "control profile", "type": "control", "d": 0, "test": "no", "component": "control", "time_type": "start"}
profile_off = {"profile": "control profile", "type": "control", "d": 0, "test": "no", "component": "control", "time_type": "off"}

# redefine on/off GPIO functions for our purposes
def pin_opp(num, type='off', test='no'):
    GPIO.setup(num, GPIO.OUT)
    if type == 'on' and test == 'yes':
        GPIO.output(num, GPIO.LOW)
        return print(f"pin {num} is on")
    elif type == 'on' and test != 'yes':
        GPIO.output(num, GPIO.LOW)
        return None;
    elif type == 'off' and test == 'yes':
        GPIO.output(num, GPIO.HIGH)
        return print(f"pin {num} is off")
    elif type == 'off' and test != 'yes':
        GPIO.output(num, GPIO.HIGH)
        return None;
    
def hum_opp(pin=0, t=0, test='no'):
    # first button press
    pin_opp(pin, 'on', 'no')
    time.sleep(0.25)
    pin_opp(pin, 'off', 'no')
    
    # duration to emit water for, t seconds
    time.sleep(t)
    
    # second button press
    pin_opp(pin, 'on', 'no')
    time.sleep(0.25)
    pin_opp(pin, 'off', 'no')
    
def hum_opp2(pin=0, action='continue', test='no'):
    
    # convert action in case incomptiable action command is passed
    if action == 'off' or action == 'on':
        action = 'continue'
    
    # what to do with humidifier pins
    # 0.25 second pulse used to switch humidifer on and off
    if action != 'continue':
        pin_opp(pin, 'on', 'no')
        time.sleep(0.25)
        pin_opp(pin, 'off', 'no')        
    
def component_switch(component, type='off', test = 'no'):
    # combine humidifier function with other pins
    
    # test variable not used currently
    
    if component == f"humidifier":
        hum_opp2(pin_map[component], type, test)
    else:
        pin_opp(pin_map[component], type, test)
    
def fan_opp(num=0, opp='off'):
    GPIO.setup(num, GPIO.OUT)
    if opp == 'on':
        GPIO.output(num, GPIO.LOW) #on
    else:
        GPIO.output(num, GPIO.HIGH) #off
        
def pins_off():

    # initialise off - could automate this with the pin_map dictionary
    # bank A
    pin_opp(25) #IN1
    pin_opp(5) #IN2
    pin_opp(6) #IN3
    pin_opp(16) #IN4

    # initialise off - could automate this with the pin_map dictionary
    # bank B
    pin_opp(22) #IN1
    pin_opp(12) #IN2
    pin_opp(20) #IN3
    #hum_opp(19, 2) # humidifier can get tripped up if not careful
    #cab_001.pin_opp(19) #IN4 - humidifier needs special switch

def database_connect():
    # Connect to MariaDB Platform
    try:
        conn = mariadb.connect(
            user="root",
            password="SaraOriana123",
            host="localhost",
            #port=3306,
            database="dht_series")

    except mariadb.Error as e:
        print(f"Error connecting to MariaDB Platform: {e}")
        sys.exit(1)

    # Get Cursor
    cur = conn.cursor()
    
    return conn, cur

def read_sensors(sensors):
    try:
        results = dict()

        for sensor in sensors:
            results[sensor] = sensors[sensor].read()

        return results

    except:
        print(f"read_sensors error")        

def get_next_batch_id(cursor):  
    cursor.execute(f"SELECT MAX(batch_id) FROM dht_profiles")
    result = cursor.fetchall() 
    if result[0][0] is None:
        return 1
    else:
        return result[0][0] + 1

def get_next_profile_id(cursor):
    cursor.execute(f"SELECT MAX(profile_id) FROM dht_profiles")
    result = cursor.fetchall()
    if result[0][0] is None:
        return 1
    else:
        return result[0][0] + 1
    
def get_parameters(cursor):
    batch_id = get_next_batch_id(cursor)
    profile_id = get_next_profile_id(cursor)
    parameters = {"batch_id": batch_id, "profile_id": profile_id}
    return parameters

def record_results(conn, cur, database_parameters, results, test = True):
    
    try:
        for result in results:
            a = results[result]
            sql_string = f"INSERT INTO dht_series VALUES (DEFAULT, {a['temp_c']}, {a['humidity']}, {a['valid']}, '{datetime.datetime.now()}', '{result}', '{database_parameters['profile_id']}', {database_parameters['batch_id']})"
            
            if test == True:
                print(sql_string)
            else:
                cur.execute(sql_string)
                conn.commit()
        
    except mariadb.Error as e:
        # how to catch the sensor errors???
        cur.execute(f"INSERT INTO dht_errors VALUES (DEFAULT, {e}, '{datetime.datetime.now()}')")
        conn.commit()
        conn.close()
            
        print(f"ERROR 01")
        sys.exit(1) # could just repeat the loop
        #continue;
        
    except:
        print("string error")

def log_profile(connection, cursor, database_parameters, profile, timestamp, test = True):
    
    sql_string = (f"INSERT INTO dht_profiles VALUES (DEFAULT, " +
          f"{database_parameters['profile_id']}, " +
          f"'{profile['profile']}', " +
           f"{database_parameters['batch_id']}, " +
          f"'{profile['type']}', " +
           f"{profile['d']}, " +
          f"'{profile['component']}', " +
          f"'{profile['test']}', " +
          f"'{profile['time_type']}', " +
          f"'{timestamp}')")
    
    if test == True:
        print(sql_string)
    else:
        cursor.execute(sql_string)
        connection.commit()

def compressor_pause(connection, cursor, database_parameters, sensors, test):
    
    start = time.time()
    mins = 5

    while time.time() - start < 60*mins:
        local_results = read_sensors(sensors)
        record_results(connection, cursor, database_parameters, local_results, test)
        del local_results

# this function is unfinished
def state_estimate(results):
    try:
        temps = []
        hums = []
        
        for result in results:
            if results[result]['valid'] == True:
                temps.append(results[result]['temp_c'])
                hums.append(results[result]['humidity'])
        
        if len(temps) == 0:
            return tuple((2, "[state_estimate]: no valid measurements", tuple((None, None)), results))
        else:
            return tuple((0, "OK", tuple((sum(temps)/len(temps), sum(hums)/len(hums))), results))
        
    except Exception as error:
        return tuple((1, "[state_estimate]: {error}", tuple((None, None)), None))
    
def first_reading(sensors):
    try:
        results = read_sensors(sensors)
        value_estimates = state_estimate(results)
        
        while value_estimates[0] != 0:
            results = read_sensors(sensors)
            value_estimates = state_estimate(results)
            
        return tuple((0, "OK", value_estimates))
        
    except:
        print("first reading error")
        return tuple((1, "[first_reading]: error", None))

def initialise_sensors():
    
    # tell rpi.gpio to use BCM numbering convention
    GPIO.setmode(GPIO.BCM)

    # sensor pins 
    DHT_01 = pin_map['sensor001'] # BCM Numbering
    DHT_02 = pin_map['sensor002'] # BCM Numbering

    #sensor = DHT11(gpio)
    sensor01 = DHT22(DHT_01) #DHT22_01
    sensor02 = DHT22(DHT_02) #DHT22_02
    
    sensors = {"sensor01": sensor01, "sensor02": sensor02}
    return sensors

def intialise_system():
    
    # new code
    sensors = initialise_sensors()

    # log start of control
    connection, cursor = database_connect()

    # initialise dataparameters
    database_parameters = get_parameters(cursor)
    
    return sensors, connection, cursor, database_parameters
    
def humidity_tracker(hum_track, H):
        
    try:
        # check and change humidity tracking
        if (H > H0 + delta) and hum_track == 'off':
            local_action = 'continue'
            local_hum_track = 'off'
        elif (H < H0 - delta) and hum_track == 'off':
            local_action = 'change'
            local_hum_track = 'on'
        elif (H > H0 + delta) and hum_track == 'on':
            local_action = 'change'
            local_hum_track = 'off'
        elif (H < H0 - delta) and hum_track == 'on':
            local_action = 'continue'
            local_hum_track = 'on'
        else:
            local_action = 'continue'
            local_hum_track = hum_track  
            
        return local_action, local_hum_track
    
    except Exception as humidity_tracker_exception:
        print(f"[humidity_tracker error]: {humidity_tracker_exception}")
        print(f"H: {H}, H0: {H0}, delta: {delta}")
        return local_action, local_hum_track
    
### new code
def time_q(start):
    
    # check if 60*N seconds has elapsed
    if time.time() - start < 60*5:
        return False
    # return True if 60 seconds has elapsed
    else:
        return True
    
def temp_q(T):
    if T > T0 + epsilon:
        return 'TU'
    elif T < T0 - epsilon:
        return 'TL'
    else:
        return None

def temp_flag_check(flag, T, time_start):
    
    try:
        new_start = time_start
        
        # heating + T in TU => rest, otherwise heating
        if flag == 'T01' and temp_q(T) == 'TU':
            flag = 'T03'
            new_start = time.time()
            
        # cooling + T in TL => rest, otherwise cooling
        elif flag == 'T02' and temp_q(T) == 'TL':
            flag = 'T03'
            new_start = time.time()

        # rest + time OK => OK, otherwise rest
        elif flag == 'T03' and time_q(time_start) == True:
            flag = 'T00'
           
        # OK + T in TU => cooling, otherwise OK
        elif flag == 'T00' and temp_q(T) == 'TU':
            flag = 'T02'
            
        # OK + T in TL => heating, otherwise, OK
        elif flag == 'T00' and temp_q(T) == 'TL':
            flag = 'T01'
        
        return flag, new_start
    
    except Exception as flag_check_error:
        print(f"[temp_flag_check error: {flag_check_error}")
        return None, None

def temp_control(flag, test = 'no'):
    
    # temperature low
    if flag == 'T01':
        component_switch('heater001', 'on', test)
        component_switch('heater002', 'on', test)
        component_switch('compressor', 'off', test)
    
    # temperature high
    elif flag == 'T02':
        component_switch('heater001', 'off', test)
        component_switch('heater002', 'off', test)
        component_switch('compressor', 'on', test)
    
    # OK or pause
    elif flag == 'T00' or flag == 'T03':
        component_switch('heater001', 'off', test)
        component_switch('heater002', 'off', test)
        component_switch('compressor', 'off', test)
        
    print(f"[temp_control]: profile used: {flag}")

def hum_q(H):
    if H > H0 + delta:
        return 'HU'
    elif H < H0 - delta:
        return 'HL'
    else:
        return None

def hum_flag_check(flag, H, time_start):
    
    try:
        
        new_start = time_start
        
        # heating + T in TU => rest, otherwise heating
        if flag == 'H01' and hum_q(H) == 'HU':
            flag = 'H03'
            new_start = time.time()
            
        # cooling + T in TL => rest, otherwise cooling
        elif flag == 'H02' and hum_q(H) == 'HL':
            flag = 'H03'
            new_start = time.time()

        # rest + time OK => OK, otherwise rest
        elif flag == 'H03' and time_q(time_start) == True:
            flag = 'H00'
           
        # OK + H in HU => dehumidifying, otherwise OK
        elif flag == 'H00' and hum_q(H) == 'HU':
            flag = 'H02'
            
        # OK + H in HL => humidifying, otherwise, OK
        elif flag == 'H00' and hum_q(H) == 'HL':
            flag = 'H01'
        
        return flag, new_start
    
    except Exception as flag_check_error:
        print(f"[hum_flag_check error: {flag_check_error}")
        return None, None

def humidity_tracker2(tracker, target):
    
    try:
        if tracker == target:
            return 'continue', tracker
        elif tracker != target:
            return 'change', target
        
    except Exception as hum_track2_error:
        print(f"[humidity_tracker2 error]: {hum_track2_error}")
    
def hum_control(flag, hum_track, test = 'no'):
    
    # humidity low
    if flag == 'H01':
        action, hum_track = humidity_tracker2(hum_track, 'on')
        
        component_switch('humidifier', action, test)
        component_switch('dehumidifier', 'off', test)
    
    # humidity high
    elif flag == 'H02':
        action, hum_track = humidity_tracker2(hum_track, 'off')
        
        component_switch('humidifier', action, test)
        component_switch('dehumidifier', 'on', test)
    
    # OK or pause
    elif flag == 'H00' or flag == 'H03':
        action, hum_track = humidity_tracker2(hum_track, 'off')
        
        component_switch('humidifier', action, test)
        component_switch('dehumidifier', 'off', test)
        
    print(f"[hum_control]: profile used: {flag}\n")
        
    return hum_track
### end code
    
def control_system(estimate_values, test, hum_track, temp_flag, hum_flag, temp_start, hum_start):
    
    try:
        
        if estimate_values[0] == 0:
            
            T = estimate_values[2][0]
            H = estimate_values[2][1]
            #action, hum_track = humidity_tracker(hum_track, H)
            
            if test == True:
                
                print(f"[control_system 01]: hum_track: {hum_track}, temp_flag: {temp_flag}, hum_flag: {hum_flag}, temp_start: {temp_start}, hum_start: {hum_start}\n")
                
            else:
                
                ### new code
                # check if flag needs to change
                temp_flag, temp_start = temp_flag_check(temp_flag, T, temp_start)
                hum_flag, hum_start = hum_flag_check(hum_flag, H, hum_start)
                
                print(f"temp_flag: {temp_flag} | temp_start: {temp_start} | T: {T} | TU: {T0+epsilon} | TL: {T0-epsilon} | T in: {temp_q(T)}")
                print(f"hum_flag: {hum_flag} | hum_start: {hum_start} | H: {H} | HU: {H0+delta} | HL: {H0-delta} | H in: {hum_q(H)} | hum_track: {hum_track}\n")
                
                # control system
                temp_control(temp_flag)
                hum_track = hum_control(hum_flag, hum_track)
                ### end code
        
#             elif (T > T0 + epsilon) and (H > H0 + delta):
#                 
#                 # compressor + dehumidifier
#                 profile = 1
#                 
#                 component_switch('heater001', 'off', test)
#                 component_switch('heater002', 'off', test)
#                 component_switch('compressor', 'on', test)
#                 component_switch('humidifier', action, test)
#                 component_switch('dehumidifier', 'on', test)
#                 
#             elif (T > T0 + epsilon) and (H < H0 - delta):
#                 
#                 # compressor + humidifier
#                 profile = 2
# 
#                 component_switch('heater001', 'off', test)
#                 component_switch('heater002', 'off', test)
#                 component_switch('compressor', 'on', test)
#                 component_switch('humidifier', action, test)
#                 component_switch('dehumidifier', 'off', test)
#                 
#             elif (T < T0 - epsilon) and (H > H0 + delta):
#                 
#                 # heater + dehumidifier
#                 profile = 3
# 
#                 component_switch('heater001', 'on', test)
#                 component_switch('heater002', 'on', test)
#                 component_switch('compressor', 'off', test)
#                 component_switch('humidifier', action, test)
#                 component_switch('dehumidifier', 'on', test)
#                 
#             elif (T < T0 - epsilon) and (H < H0 - delta):
#                 
#                 # heater + humidifier
#                 profile = 4
# 
#                 component_switch('heater001', 'on', test)
#                 component_switch('heater002', 'on', test)
#                 component_switch('compressor', 'off', test)
#                 component_switch('humidifier', action, test)
#                 component_switch('dehumidifier', 'off', test)
            
            del T, H #, action
        
#         else:
#             #do not change profile (profile 0)
#             profile = 0
        
        #print(f"temp_flag: {temp_flag} | hum_flag: {hum_flag}")
        return hum_track, temp_flag, hum_flag, temp_start, hum_start
    
    except Exception as humidity_tracker_exception:
        print(f"[humidity_tracker error]: {humidity_tracker_exception}")
        return hum_track, temp_flag, hum_flag, temp_start, hum_start

def start_control():
    
    # test keys
    # test values - True/ False - controls when database values are written
    log_test = False;
    record_test = False;
    control_test = False;
    
    # initialise
    sensors, connection, cursor, database_parameters = intialise_system();
    
    # initialise flags
    temp_flag = 'T00';
    hum_flag = 'H00';

    # initilaise start times
    temp_start = None;
    hum_start = None;
    
    # log start of control
    log_profile(connection, cursor, database_parameters, profile_on, datetime.datetime.now(), log_test);

    # turn fan on
    fan_opp(pin_map['fan'], 'on');
    
    # humidifer tracker
    hum_track = 'off';
    print(f"initial humiditiy setting: {hum_track}");
    
    # start timings
    start = time.time();

    # start monitoring
    while True:
        

        
        try:
            
            results = read_sensors(sensors)
            record_results(connection, cursor, database_parameters, results, record_test)
            estimate_values = state_estimate(results)
            
            hum_track, temp_flag, hum_flag, temp_start, hum_start = control_system(
                                       estimate_values,
                                       control_test,
                                       hum_track,
                                       temp_flag,
                                       hum_flag,
                                       temp_start,
                                       hum_start)

            del results
            
        except Exception as control_error:
            
            # switch off humidifier using tracker
            if hum_track == 'on':
                component_switch('humidifier', 'change', control_test)
                hum_track = 'off'
                pins_off()
            else:
                pins_off()

            print(f"error main monitoring loop: {control_error}")
            break
                     
#             if (time.time()-start) > 60*60*3:
#                 # need function to swtich everything off
#                 if hum_track == 'on':
#                     print("loop exit pins_off() + switching humidifier off")
#                     component_switch('humidifier', 'change', control_test)
#                     hum_track = 'off'
#                     pins_off()
#                 else:
#                     print(f"loop exit pins_off()")
#                     pins_off()
#                     
#                 break
    
    # clean up
    print(f"hum track 02: {hum_track}")
    fan_opp(pin_map['fan'], 'off')
    pins_off()

    # log end of control
    log_profile(connection, cursor, database_parameters, profile_off, datetime.datetime.now(), log_test)
    connection.close()

######################################################
######################################################

# start of control loop

try:
    start_control()
    
except KeyboardInterrupt:
    print(f"You pressed Ctrl-C to terminate while statement: {datetime.datetime.now()}")
    sys.exit(0)

