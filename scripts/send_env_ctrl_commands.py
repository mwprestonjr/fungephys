"""
This script controls the environmental conditions based on keyboard inputs from the command line

Commands:
    H : Humidifier ON
    h : Humidifier OFF

    F : Fan ON
    f : Fan OFF

    L : Light ON
    l : Light OFF
"""

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
PATH_OUT = "data/environment/"  # Output folder for data


def main():

    # create data log files
    if not os.path.exists(PATH_OUT):
        os.makedirs(PATH_OUT)
    with open(f"{PATH_OUT}/commandlog.csv", 'w') as f:
        f.write("time,command\n")

    # print status
    print("\n======== Starting environment control script ========")
    print_prompt()

    # Main loop
    while True:
        try:
            # Check for keyboard input
            command = input("Enter command: ").strip()
            if command in ['F', 'f', 'H', 'h', 'L', 'l']:
                send_command(command)
            else:
                print("\nInvalid command. Please try again.")
                print_prompt()


        except KeyboardInterrupt:
            print("\n============ Keyboard interrupt detected ============")
            print(f"Data saved to '{PATH_OUT}/commandlog.csv'")
            print("\n======================= END ========================")
            break

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
    df.to_csv(f"{PATH_OUT}/commandlog.csv", mode='a', header=False, index=False)


def print_prompt():
    print("\nPlease enter one of the following commands:")
    print("  H/h : Humidifier ON/OFF")
    print("  F/f : Fan ON/OFF")
    print("  L/l : Light ON/OFF\n")


if __name__ == "__main__":
    main()