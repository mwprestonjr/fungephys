"""
Record data from PiEEG-16 and write to CSV

"""


# ========================== Settings ==========================

FNAME_OUT = 'data/recordings/pieeg_test_data.csv'
DURATION = 60 * 60  # seconds
FS = 100  # Hz
GAIN = 24 # signal gain (1, 2, 4, 6, 8, 12, or 24)

# ========================== Setup ==========================

# imports
import numpy as np
import spidev
from datetime import datetime
from RPi import GPIO
GPIO.setwarnings(False) 
GPIO.setmode(GPIO.BOARD)
import gpiod
from time import sleep

# print status
print("\nSetting up recording device...")

# GPIO settings
chip = gpiod.Chip("gpiochip4")

cs_line = chip.get_line(19)  # GPIO19
cs_line.request(consumer="SPI_CS", type=gpiod.LINE_REQ_DIR_OUT)
cs_line.set_value(1)  # Set CS high initially

# Initialize spidev
spi = spidev.SpiDev()

spi.open(0,0)
spi.max_speed_hz  = 4000000
spi.lsbfirst=False
spi.mode=0b01
spi.bits_per_word = 8

spi_2 = spidev.SpiDev()

spi_2.open(0,1)
spi_2.max_speed_hz=4000000
spi_2.lsbfirst=False
spi_2.mode=0b01
spi_2.bits_per_word = 8

# Register Commands
who_i_am=0x00
config1=0x01
config2=0X02
config3=0X03

reset=0x06
stop=0x0A
start=0x08
sdatac=0x11
rdatac=0x10
wakeup=0x02
rdata = 0x12

ch1set=0x05
ch2set=0x06
ch3set=0x07
ch4set=0x08
ch5set=0x09
ch6set=0x0A
ch7set=0x0B
ch8set=0x0C

data_test = 0x7FFFFF
data_check = 0xFFFFFF


# ========================== Functions ==========================

# SPI Read/Write Functions
def read_byte(register):
    write=0x20
    register_write=write|register
    data = [register_write,0x00,register]
    spi.xfer(data)
 
def send_command(command):
    send_data = [command]
    spi.xfer(send_data)
 
def write_byte(register,data):
    write=0x40
    register_write=write|register
    data = [register_write,0x00,data]
    spi.xfer(data)

def read_byte_2(register):
    write=0x20
    register_write=write|register
    data = [register_write,0x00,register]
    cs_line.set_value(0)
    spi.xfer(data)
    cs_line.set_value(1)
 
def send_command_2(command):
    send_data = [command]
    cs_line.set_value(0)
    spi_2.xfer(send_data)
    cs_line.set_value(1)
 
def write_byte_2(register,data):
    write=0x40
    register_write=write|register
    data = [register_write,0x00,data]
    cs_line.set_value(0)
    spi_2.xfer(data)
    cs_line.set_value(1)

def get_voltage(output, a, data_check, data_test):
    voltage=(output[a]<<8) | output[a+1]
    voltage=(voltage<<8) | output[a+2]
    convert_voltage = voltage | data_test
    if convert_voltage==data_check:
        voltage = (voltage - 16777214)
    voltage = round(1000000*4.5*(voltage/16777215),2)

    return voltage

def convert_gain(value):
# convert to bits
    if value == 1:
        return 0b000
    elif value == 2:
        return 0b001
    elif value == 4:
        return 0b010
    elif value == 6:
        return 0b011
    elif value == 8:
        return 0b100
    elif value == 12:
        return 0b101
    elif value == 24:
        return 0b110
    else:
        raise ValueError("Invalid gain value. Please use 1, 2, 4, 6, 8, 12, or 24.")


# ========================== Init ==========================

# device initialization and configuration - first 8 channels
send_command (wakeup)
send_command (stop)
send_command (reset)
send_command (sdatac)

write_byte (0x14, 0x80) #GPIO 80
write_byte (config1, 0x96)
write_byte (config2, 0xD4)
write_byte (config3, 0xFF)
write_byte (0x04, 0x00)
write_byte (0x0D, 0x00)
write_byte (0x0E, 0x00)
write_byte (0x0F, 0x00)
write_byte (0x10, 0x00)
write_byte (0x11, 0x00)
write_byte (0x15, 0x20)

write_byte (0x17, 0x00)
gain = convert_gain(GAIN)
write_byte (ch1set, gain)
write_byte (ch2set, gain)
write_byte (ch3set, gain)
write_byte (ch4set, gain)
write_byte (ch5set, gain)
write_byte (ch6set, gain)
write_byte (ch7set, gain)
write_byte (ch8set, gain)

send_command (rdatac)
send_command (start)

# device initialization and configuration - last 8 channels
send_command_2 (wakeup)
send_command_2 (stop)
send_command_2 (reset)
send_command_2 (sdatac)

write_byte_2 (0x14, 0x80) #GPIO 80
write_byte_2 (config1, 0x96)
write_byte_2 (config2, 0xD4)
write_byte_2 (config3, 0xFF)
write_byte_2 (0x04, 0x00)
write_byte_2 (0x0D, 0x00)
write_byte_2 (0x0E, 0x00)
write_byte_2 (0x0F, 0x00)
write_byte_2 (0x10, 0x00)
write_byte_2 (0x11, 0x00)
write_byte_2 (0x15, 0x20)

write_byte_2 (0x17, 0x00)
write_byte_2 (ch1set, gain)
write_byte_2 (ch2set, gain)
write_byte_2 (ch3set, gain)
write_byte_2 (ch4set, gain)
write_byte_2 (ch5set, gain)
write_byte_2 (ch6set, gain)
write_byte_2 (ch7set, gain)
write_byte_2 (ch8set, gain)

send_command_2 (rdatac)
send_command_2 (start)


# ========================== Main ==========================

# print status
print("Recording data...")

# initialize csv
columns = "time,chan_1,chan_2,chan_3,chan_4,chan_5,chan_6,chan_7,chan_8,chan_9,chan_10,chan_11,chan_12,chan_13,chan_14,chan_15,chan_16\n"
with open(FNAME_OUT, 'w') as f:
    f.write(columns)

# start clock
start_time = datetime.now()

# main loop
for i_sample in range(DURATION * FS):
    # wait for sample time
    if (datetime.now()-start_time).total_seconds() < (i_sample/FS):
        sleep((i_sample/FS)-(datetime.now()-start_time).total_seconds())
    timepoint = (datetime.now()-start_time).total_seconds()

    # read data
    output_1=spi.readbytes(27)
    cs_line.set_value(0)
    output_2=spi_2.readbytes(27)
    cs_line.set_value(1)

    data = np.zeros(16)
    for a in range (3, 25, 3):
        data[int(a/3)-1] = get_voltage(output_1, a, data_check, data_test)
        data[int(a/3)+7] = get_voltage(output_2, a, data_check, data_test)

    # write data
    with open(FNAME_OUT, 'a') as f:
        f.write(f"{timepoint}, {data[0]}, {data[1]}, {data[2]}, {data[3]}, {data[4]}, {data[5]}, {data[6]}, {data[7]}, {data[8]}, {data[9]}, {data[10]}, {data[11]}, {data[12]}, {data[13]}, {data[14]}, {data[15]}\n")
        
print(f"Data saved to {FNAME_OUT}")
