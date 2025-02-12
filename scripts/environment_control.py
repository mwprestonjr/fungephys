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
import smbus2
import time
from datetime import datetime
from adafruit_sht31d import SHT31D
import board
import busio

import numpy as np
import pandas as pd 

# Initialize I2C for SHT30
i2c = busio.I2C(board.SCL, board.SDA)
sht = SHT31D(i2c)

# Initialize I2C for Arduino
bus = smbus2.SMBus(1)
arduino_address = 0x04

# Control settings
FILENAME = "data/environment/temp.csv"

LIGHT_ON_TIME = 8  # Light ON time (24-hour format)
LIGHT_OFF_TIME = 20  # Light OFF time (24-hour format)

HUMIDITY_LOW = 85.0 # Humidity lower threshold
HUMIDITY_HIGH = 95.0 # Humidity upper threshold

FAN_DURATION = 120  # Duration to keep the fan on, in seconds
FAN_INTERVAL = 3600  # Interval between fan runs, in seconds


def main():
    # print status
    print("======= Starting environment control script =======")

    # init
    light_status = init_light()
    last_fan_time = time.time() - 3600  # Ensure fan runs on startup
    fan_status, fan_ran = False, False

    data_times = []
    temperature_log = []
    humidity_log = []
    light_log = []

    try:
        while True:
            # Read temperature and humidity
            try:
                data_time = datetime.now()
                humidity = sht.relative_humidity
                temperature = sht.temperature
                temperature_f = celcius_to_fahrenheit(temperature)
                print(f"\nEnvironmental conditions:\n\tTemperature: {temperature:.2f}°C ({temperature_f:.2f}°F) \n\tHumidity: {humidity:.2f}%\n")
            except Exception as e:
                print(f"Failed to read from sensor: {e}")
                continue

            # collect data
            data_times.append(data_time)
            temperature_log.append(temperature)
            humidity_log.append(humidity)
            light_log.append(light_status)

            # Control devices
            control_humidifier(humidity)
            light_status = control_light(light_status)
            last_fan_time, fan_status, fan_ran = control_fan(last_fan_time, fan_status, fan_ran)
            
            time.sleep(10)  # Delay between checks

    # if keyboard interrupt, save data
    except KeyboardInterrupt:
        save_data(data_time, temperature_log, humidity_log, light_log)
        print("\n======= Stopping environment control script =======")
        exit(0)


def send_command(command):
    try:
        bus.write_byte(arduino_address, ord(command))
    except Exception as e:
        print(f"Failed to send command {command}: {e}")


def init_light():
    # Initialize light control
    now = datetime.now()
    if now.hour >= LIGHT_ON_TIME and now.hour < LIGHT_OFF_TIME:
        send_command('L')  # Turn ON light
        light_status = True

    return light_status


def control_humidifier(humidity):
    if humidity < HUMIDITY_LOW:
        send_command('H')  # Turn ON humidifier
        print("Humidifier ON")
    elif humidity > HUMIDITY_HIGH:
        send_command('h')  # Turn OFF humidifier
        print("Humidifier OFF")


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


def control_fan(last_fan_time, fan_status, fan_ran):
    if time.time() - last_fan_time >= FAN_INTERVAL and not fan_status and not fan_ran:
        send_command('F')  # Turn ON fan
        send_command('H')  # Turn ON humidifier
        print("Fan ON")
        print("Humidifier ON")
        last_fan_time = time.time()
        fan_status = True
        fan_ran = True
    
    if time.time() - last_fan_time >= FAN_DURATION and fan_status:
        send_command('f')
        print("Fan OFF")        
    
    return last_fan_time, fan_status, fan_ran


def save_data(data_times, temperature_log, humidity_log, light_log):
    print("\nSaving data...")

    # save data to CSV
    data = {
        'Time': data_times,
        'Temperature (°C)': temperature_log,
        'Humidity (%)': humidity_log,
        'Light Status': light_log
    }
    df = pd.DataFrame(data)
    df.to_csv(FILENAME, index=False)
    print(f"Data saved to {FILENAME}")


def celcius_to_fahrenheit(celsius):
    return (celsius * 9/5) + 32


if __name__ == "__main__":
    main()
