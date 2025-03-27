"""
This script controls the environmental conditions. It is designed to run on a
Raspberry Pi with an SHT30 sensor and an Arduino connected via I2C. The script
reads temperature and humidity from an SHT30 sensor and controls a 
humidifier, light, and fan using the Arduino. The behavior of the devices is:

- Light: Turns ON at 8:00 and OFF at 20:00

NOTE: the script was originally written to control a fan and humidifier also,
but these features have been commented out.

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
arduino_address = 0x10

# Control settings
PATH_OUT = "data/environment/"  # Output folder for data

LIGHT_ON_TIME = 8  # Light ON time (24-hour format)
LIGHT_OFF_TIME = 20  # Light OFF time (24-hour format)

HUMIDITY_LOW = 85.0 # Humidity lower threshold
HUMIDITY_HIGH = 95.0 # Humidity upper threshold
BACKUP_HUMIDITY_LOW = 80.0 # Backup humidity lower threshold

FAN_INTERVAL = 600  # Interval between fan runs, in seconds

UPDATE_INTERVAL = 60 # Time between sensor readings, in seconds


def main():
    # print status
    print("======= Starting environment control script =======")

    # init sensors and devices
    light_status = init_light()
    fan_status = init_fan()
    humidifer_status = init_humidifier()

    # create data log files
    if not os.path.exists(PATH_OUT):
        os.makedirs(PATH_OUT)
    if not os.path.exists(f"{PATH_OUT}/datalog.csv"):
        with open(f"{PATH_OUT}/datalog.csv", 'w') as f:
            f.write("time,temperature,humidity,light\n")
    if not os.path.exists(f"{PATH_OUT}/eventlog.csv"):
        with open(f"{PATH_OUT}/eventlog.csv", 'w') as f:
            f.write("time,command\n")

    # print settings
    print("\nEnvironment control settings:")
    print(f"  Light ON time: {LIGHT_ON_TIME}:00")
    print(f"  Light OFF time: {LIGHT_OFF_TIME}:00")
    print(f"  Humidity range: [{HUMIDITY_LOW}%, {HUMIDITY_HIGH}%]")
    print(f"  Fan interval: {FAN_INTERVAL} seconds")

    # print status
    print(f"\nDevices initialized:")
    print(f"  Light: {'ON' if light_status else 'OFF'}")
    print(f"  Fan: {'ON' if fan_status['status'] else 'OFF'}")
    print(f"  Humidifier: {'ON' if humidifer_status else 'OFF'}")
    print(f"\nData log files created at '{PATH_OUT}'")

    # print status
    print("\n======= Environment control script started =======")

    try:
        while True:
            # Read temperature and humidity
            maintenance_sensor()
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
            df.to_csv(f"{PATH_OUT}/datalog.csv", mode='a', header=False, index=False)

            # Control devices
            humidifer_status = control_humidifier(humidifer_status, humidity)
            humidifer_status = control_backup_humidifier(humidifer_status, humidity)
            fan_status, humidifer_status = control_fan(fan_status, humidifer_status)
            light_status = control_light(light_status)
            
            # Delay between checks
            time.sleep(UPDATE_INTERVAL)

    # if keyboard interrupt, save data
    except KeyboardInterrupt:
        print("\n========= Keyboard interrupt detected =========")
        # shutdown()
        print(f"Find data in '{PATH_OUT}'")
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
    df.to_csv(f"{PATH_OUT}/eventlog.csv", mode='a', header=False, index=False)


def init_light():
    # Initialize light control
    now = datetime.now()
    if now.hour >= LIGHT_ON_TIME and now.hour < LIGHT_OFF_TIME:
        send_command('L')
        light_status = True
    else:
        light_status = False

    return light_status


def init_fan():
    # Initialize fan control
    send_command('F')
    fan_status = dict({
        'status': True,
        'last_run_time': time.time()
    })

    return fan_status


def init_humidifier():
    # Initialize humidifier control
    send_command('H')
    humidifer_status = True

    return humidifer_status


def maintenance_sensor():
    # Turn on heater breifly to evaporate condensation
    sht.heater = True
    time.sleep(1)
    sht.heater = False


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


def control_backup_humidifier(humidifer_status, humidity):
    if humidity < BACKUP_HUMIDITY_LOW and not humidifer_status:
        send_command('J')  # Turn ON humidifier
        humidifer_status = True
        print("Humidifier ON")
    elif humidity > HUMIDITY_HIGH and humidifer_status:
        send_command('j')  # Turn OFF humidifier
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


def control_fan(fan_status, humidifer_status):
    if time.time() - fan_status['last_run_time'] >= FAN_INTERVAL:
        print("Fan interval reached")
        if not fan_status['status']:
            send_command('F')  # Turn ON fan
            send_command('H')  # Turn ON humidifier
            print("Fan ON")
            print("Humidifier ON")
            fan_status['status'] = True
            fan_status['last_run_time'] = time.time()
            humidifer_status = True
        else:
            send_command('f')
            send_command('h')
            print("Fan OFF")
            print("Humidifier OFF")
            fan_status['status'] = False
            fan_status['last_run_time'] = time.time()
            humidifer_status = False
    
    return fan_status, humidifer_status


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
