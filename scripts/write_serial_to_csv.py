"""
This scripts reads data from a serial port and writes it to a csv file. The value and timestamp is recorded in the csv.

"""

# imports
import os
import serial
import time

# settings
SERIAL_DEVICE = '/dev/ttyACM0'
BAUD_RATE = 9600 # must match Arduino buad rate
TIMEOUT = 1 # seconds
FILENAME = 'data/temp.csv' # for output file

if __name__ == '__main__':
	# initialize Serial communication
	ser = serial.Serial(SERIAL_DEVICE, BAUD_RATE, timeout=TIMEOUT)
	ser.reset_input_buffer()
	
	# open csv
	if os.path.exists(FILENAME):
		os.remove(FILENAME)
	data = open(FILENAME, 'w')
	
	# write header
	data.write('time,value\n')

	# record start time
	start_time = time.time()

	# read Serial input and write to file
	while True:
		# read serial
		value = ser.readline().decode('utf-8').strip()
		if value:
			# write to file
			time_now = time.time() - start_time
			data.write(f'{time_now}, {value}\n')
			data.flush()
			print(f'{time_now:0.2f}, {value}')


