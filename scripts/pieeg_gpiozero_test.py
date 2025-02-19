import spidev
import time
from matplotlib import pyplot as plt
from scipy.ndimage import gaussian_filter1d
from scipy import signal
from gpiozero import Button, DigitalOutputDevice

# Define GPIO Pins
button_pin_1 = 26
button_pin_2 = 13
cs_pin = 19

# Initialize Button Inputs
button_1 = Button(button_pin_1, pull_up=True)  # Button connected to GPIO 26
button_2 = Button(button_pin_2, pull_up=True)  # Button connected to GPIO 13

# Initialize Chip Select (CS) Line as Output
cs_line = DigitalOutputDevice(cs_pin, active_high=False, initial_value=True)  # CS initially high

# Initialize SPI
spi = spidev.SpiDev()
spi.open(0, 0)  # Use SPI bus 0, device 0
spi.max_speed_hz = 4000000  # 4 MHz
spi.lsbfirst = False
spi.mode = 0b01
spi.bits_per_word = 8

spi_2 = spidev.SpiDev()
spi_2.open(0, 1)  # Use SPI bus 0, device 1
spi_2.max_speed_hz = 4000000  # 4 MHz
spi_2.lsbfirst = False
spi_2.mode = 0b01
spi_2.bits_per_word = 8

# Register Commands
who_i_am = 0x00
config1 = 0x01
config2 = 0x02
config3 = 0x03

reset = 0x06
stop = 0x0A
start = 0x08
sdatac = 0x11
rdatac = 0x10
wakeup = 0x02

ch1set = 0x05
ch2set = 0x06
ch3set = 0x07
ch4set = 0x08
ch5set = 0x09
ch6set = 0x0A
ch7set = 0x0B
ch8set = 0x0C

data_test = 0x7FFFFF
data_check = 0xFFFFFF

# SPI Read/Write Functions
def read_byte(register):
    write = 0x20
    register_write = write | register
    data = [register_write, 0x00, register]
    read_reg = spi.xfer(data)
    print("data", read_reg)

def send_command(command):
    send_data = [command]
    spi.xfer(send_data)

def write_byte(register, data):
    write = 0x40
    register_write = write | register
    data = [register_write, 0x00, data]
    print(data)
    spi.xfer(data)

def read_byte_2(register):
    write = 0x20
    register_write = write | register
    data = [register_write, 0x00, register]
    cs_line.off()  # CS LOW
    read_reg = spi.xfer(data)
    cs_line.on()  # CS HIGH
    print("data", read_reg)

def send_command_2(command):
    send_data = [command]
    cs_line.off()  # CS LOW
    spi_2.xfer(send_data)
    cs_line.on()  # CS HIGH

def write_byte_2(register, data):
    write = 0x40
    register_write = write | register
    data = [register_write, 0x00, data]
    print(data)
    cs_line.off()  # CS LOW
    spi_2.xfer(data)
    cs_line.on()  # CS HIGH

# Device Initialization
send_command(wakeup)
send_command(stop)
send_command(reset)
send_command(sdatac)

write_byte(0x14, 0x80)  # GPIO 80
write_byte(config1, 0x96)
write_byte(config2, 0xD4)
write_byte(config3, 0xFF)
write_byte(0x04, 0x00)
write_byte(ch1set, 0x01)
write_byte(ch2set, 0x00)
write_byte(ch3set, 0x00)
write_byte(ch4set, 0x00)
write_byte(ch5set, 0x00)
write_byte(ch6set, 0x00)
write_byte(ch7set, 0x00)
write_byte(ch8set, 0x00)

send_command(rdatac)
send_command(start)

send_command_2(wakeup)
send_command_2(stop)
send_command_2(reset)
send_command_2(sdatac)

write_byte_2(0x14, 0x80)  # GPIO 80
write_byte_2(config1, 0x96)
write_byte_2(config2, 0xD4)
write_byte_2(config3, 0xFF)
write_byte_2(0x04, 0x00)
write_byte_2(ch1set, 0x01)
write_byte_2(ch2set, 0x00)
write_byte_2(ch3set, 0x00)
write_byte_2(ch4set, 0x00)
write_byte_2(ch5set, 0x00)
write_byte_2(ch6set, 0x00)
write_byte_2(ch7set, 0x00)
write_byte_2(ch8set, 0x01)

send_command_2(rdatac)
send_command_2(start)

# Main Loop
while True:
    if button_1.is_pressed:
        print("Button 1 pressed, reading data...")
        output = spi.readbytes(27)

        cs_line.off()  # CS LOW
        output_2 = spi_2.readbytes(27)
        cs_line.on()  # CS HIGH

        if output_2[0] == 192 and output_2[1] == 0 and output_2[2] == 8:
            for a in range(3, 25, 3):
                voltage_1 = (output[a] << 8) | output[a + 1]
                voltage_1 = (voltage_1 << 8) | output[a + 2]
                convert_voltage = voltage_1 | data_test
                if convert_voltage == data_check:
                    voltage_1_after_convert = (voltage_1 - 16777214)
                else:
                    voltage_1_after_convert = voltage_1
                channel_num = (a // 3)
                result = round(1000000 * 4.5 * (voltage_1_after_convert / 16777215), 2)

                print(f"Channel {channel_num}: {result} µV")

    time.sleep(0.1)  # Prevent high CPU usage

# Cleanup
spi.close()
spi_2.close()
