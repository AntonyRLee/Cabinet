# Launch pi gpio deamon via terminal
# sudo pigpiod

# NOTE: The import has a _ not - in the module name.
from pigpio_dht import DHT22 #, DHT11
# replace pgiozero with rpi.gpio
import RPi.GPIO as GPIO
import time
import datetime


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

def pass_sensor(sensor):
    result = sensor.read()
    return result

def pass_sensor02(sensor):
    result = pass_sensor(sensor)
    return result

# redefine on/off GPIO functions for our purposes
def pin_opp(n, type='off', test='no'):
    GPIO.setup(n, GPIO.OUT)
    if type == 'on' and test == 'yes':
        GPIO.output(n, GPIO.LOW)
        return print(f"pin {n} is on")
    elif type == 'on' and test != 'yes':
        GPIO.output(n, GPIO.LOW)
        return None;
    elif type == 'off' and test == 'yes':
        GPIO.output(n, GPIO.HIGH)
        return print(f"pin {n} is off")
    elif type == 'off' and test != 'yes':
        GPIO.output(n, GPIO.HIGH)
        return None;
    
def hum_signal(pin):
    # emulate double button press
    pin_opp(pin, 'on', 'no')
    time.sleep(0.25)
    pin_opp(pin, 'off', 'no')

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
    #hum_opp(19, 2)
    #cab_001.pin_opp(19) #IN4 - humidifier needs special switch

# tell rpi.gpio to use BCM numbering convention
GPIO.setmode(GPIO.BCM)

# sensor pins
DHT_01 = 4 # BCM Numbering
DHT_02 = 23 # BCM Numbering

#sensor = DHT11(gpio)
sensor01 = DHT22(DHT_01) #DHT22_01
sensor02 = DHT22(DHT_02) #DHT22_02

pins_off()
# humidity signal if needed
# hum_signal(19)

start = time.time()
# 
# while True:
#     
#     try:
#         result01 = sensor01.read()
#         result02 = sensor02.read()
#         
#         print(f"{time.time()-start}")
#         print(f"temp_c: {result01['temp_c']}, hum: {result01['humidity']}, valid: {result01['valid']}, sensor: 01")
#         print(f"temp_c: {result02['temp_c']}, hum: {result02['humidity']}, valid: {result02['valid']}, sensor: 02")
#         start = time.time()
# 
#     except KeyboardInterrupt:
#         print(f"You pressed Ctrl-C to terminate while statement: {datetime.datetime.now()}")
#         break
    

