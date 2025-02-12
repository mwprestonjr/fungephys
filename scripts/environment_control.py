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

# Initialize I2C for SHT30
i2c = busio.I2C(board.SCL, board.SDA)
sht = SHT31D(i2c)

# Initialize I2C for Arduino
bus = smbus2.SMBus(1)
arduino_address = 0x04

# Control settings
HUMIDITY_LOW = 85.0 # Humidity lower threshold
HUMIDITY_HIGH = 95.0 # Humidity upper threshold

FAN_DURATION = 120  # Duration to keep the fan on, in seconds
FAN_INTERVAL = 3600  # Interval between fan runs, in seconds


def main():
    last_fan_time = time.time() - 3600  # Ensure fan runs on startup
    while True:
        # Read temperature and humidity
        try:
            humidity = sht.relative_humidity
            temperature = sht.temperature
            print(f"Temperature: {temperature:.2f}°C, Humidity: {humidity:.2f}%")
        except Exception as e:
            print(f"Failed to read from sensor: {e}")
            continue

        # Control devices
        control_humidifier(humidity)
        control_light()
        last_fan_time = control_fan(last_fan_time)
        
        time.sleep(10)  # Delay between checks


def send_command(command):
    try:
        bus.write_byte(arduino_address, ord(command))
    except Exception as e:
        print(f"Failed to send command {command}: {e}")


def control_humidifier(humidity):
    if humidity < HUMIDITY_LOW:
        send_command('H')  # Turn ON humidifier
    elif humidity > HUMIDITY_HIGH:
        send_command('h')  # Turn OFF humidifier


def control_light():
    now = datetime.now()
    if now.hour == 8 and now.minute == 0:
        send_command('L')  # Turn ON light
    elif now.hour == 20 and now.minute == 0:
        send_command('l')  # Turn OFF light


def control_fan(last_fan_time):
    if time.time() - last_fan_time >= FAN_INTERVAL:
        send_command('F')  # Turn ON fan
        time.sleep(FAN_DURATION)  # Keep fan on for 2 minutes
        send_command('f')  # Turn OFF fan
        return time.time()  # Update last_fan_time
    return last_fan_time


if __name__ == "__main__":
    main()
