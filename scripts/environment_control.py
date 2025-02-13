"""
This script controls the environmental conditions. It is designed to run on a
Raspberry Pi with an SHT30 sensor and an Arduino connected via I2C. The script
reads temperature and humidity from an SHT30 sensor and controls a 
humidifier, light, and fan using the Arduino. The behavior of the devices is:

- Humidifier: Turns ON when humidity is outside the range [85%, 95%]
- Light: Turns ON at 8:00 and OFF at 20:00
- Fan: Turns ON every hour for 2 minutes

"""

# imports
import os
import numpy as np
import pandas as pd 

import smbus2
import time
from datetime import datetime
from adafruit_sht31d import SHT31D
import board
import busio

# Initialize I2C for SHT30
i2c = busio.I2C(board.SCL, board.SDA)
sht = SHT31D(i2c)

# Initialize I2C for Arduino
bus = smbus2.SMBus(1)
arduino_address = 0x04

# Control settings
FNAME_DATALOG = "data/environment/datalog.csv" # Output file name for environmental data
FNAME_EVENTLOG = "data/environment/eventlog.csv" # Output file name for event log

LIGHT_ON_TIME = 8  # Light ON time (24-hour format)
LIGHT_OFF_TIME = 20  # Light OFF time (24-hour format)

HUMIDITY_LOW = 85.0 # Humidity lower threshold
HUMIDITY_HIGH = 95.0 # Humidity upper threshold

FAN_DURATION = 120  # Duration to keep the fan on, in seconds
FAN_INTERVAL = 3600  # Interval between fan runs, in seconds


def main():
    # print status
    print("======= Starting environment control script =======")

    # init sensors and devices
    light_status = init_light()
    last_fan_time = time.time() - 3600  # Ensure fan runs on startup
    fan_status, fan_ran = False, False
    humidifer_status = False

    # create data log files
    if not os.path.exists('data/environment'):
        os.makedirs('data/environment')
    if not os.path.exists(FNAME_DATALOG):
        with open(FNAME_DATALOG, 'w') as f:
            f.write("time,temperature,humidity,light\n")
    if not os.path.exists(FNAME_EVENTLOG):
        with open(FNAME_EVENTLOG, 'w') as f:
            f.write("time,command\n")

    # print status
    print("======= Environment control script started =======")

    try:
        while True:
            # Read temperature and humidity
            try:
                humidity = sht.relative_humidity
                temperature = sht.temperature
                temperature_f = celcius_to_fahrenheit(temperature)
                print(f"\nEnvironmental conditions:\n\tTemperature: {temperature:.2f}°C ({temperature_f:.2f}°F) \n\tHumidity: {humidity:.2f}%\n")
            except Exception as e:
                print(f"Failed to read from sensor: {e}")
                continue

            # write data to CSV
            data_time = datetime.now()
            data_log = {
                'time': data_time,
                'temperature': temperature,
                'humidity': humidity,
                'light': light_status
            }
            df = pd.DataFrame([data_log])
            df.to_csv(FNAME_DATALOG, mode='a', header=False, index=False)

            # Control devices
            humidifer_status = control_humidifier(humidifer_status, humidity)
            light_status = control_light(light_status)
            fan_status, fan_ran, last_fan_time = control_fan(fan_status, fan_ran, last_fan_time)
            
            time.sleep(10)  # Delay between checks

    # if keyboard interrupt, save data
    except KeyboardInterrupt:
        print("\n========= Keyboard interrupt detected =========")
        shutdown()
        print("\n==================== END =====================")
        exit(0)


def send_command(command):
    # Send command to Arduino
    try:
        bus.write_byte(arduino_address, ord(command))
    except Exception as e:
        print(f"Failed to send command {command}: {e}")

    # Log event
    event_time = datetime.now()
    event_log = {
        'time': event_time,
        'command': command
    }
    df = pd.DataFrame([event_log])
    df.to_csv(FNAME_EVENTLOG, mode='a', header=False, index=False)


def init_light():
    # Initialize light control
    now = datetime.now()
    if now.hour >= LIGHT_ON_TIME and now.hour < LIGHT_OFF_TIME:
        send_command('L')  # Turn ON light
        light_status = True
    else:
        light_status = False

    return light_status


def control_humidifier(humidifer_status, humidity):
    if humidity < HUMIDITY_LOW and not humidifer_status:
        send_command('H')  # Turn ON humidifier
        humidifer_status = True
        print("Humidifier ON")
    elif humidity > HUMIDITY_HIGH and humidifer_status:
        send_command('h')  # Turn OFF humidifier
        humidifer_status = False
        print("Humidifier OFF")

    return humidifer_status


def control_light(light_status):
    now = datetime.now()
    if now.hour >= LIGHT_ON_TIME and now.hour < LIGHT_OFF_TIME and not light_status:
        send_command('L')
        light_status = True
        print("Light ON")
    elif now.hour >= LIGHT_OFF_TIME and light_status:
        send_command('l')
        light_status = False
        print("Light OFF")

    return light_status


def control_fan(fan_status, fan_ran, last_fan_time):
    if time.time() - last_fan_time >= FAN_INTERVAL and not fan_status and not fan_ran:
        send_command('F')  # Turn ON fan
        send_command('H')  # Turn ON humidifier
        print("Fan ON")
        print("Humidifier ON")
        fan_status = True
        fan_ran = True
        last_fan_time = time.time()

    if time.time() - last_fan_time >= FAN_DURATION and fan_status:
        send_command('f')
        send_command('h')
        print("Fan OFF")
        print("Humidifier OFF")
        fan_status = False
    
    return fan_status, fan_ran, last_fan_time


def shutdown():
    # turn off all devices
    print("Shutting down all devices...")
    send_command('h')  # Turn OFF humidifier
    send_command('f')  # Turn OFF fan
    send_command('l')  # Turn OFF light


def celcius_to_fahrenheit(celsius):
    return (celsius * 9/5) + 32


if __name__ == "__main__":
    main()
