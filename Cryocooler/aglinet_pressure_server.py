#!/usr/bin/python

import signal
import shutil
import serial
import os
import sys
import time
from tqdm.auto import tqdm
from datetime import datetime,timedelta

""" "Constants" Definitions """
STX = 0x02
ETX = 0x03
ADDR = 0x80 # 0x80 for rs232 0x83 for rs485
RD = 0X30
WR = 0X31
global Turboport
#Turboport= 'COM4'#For Fs80 for dewar
Turboport='COM3'

SAMPLE_TIME = 60 # Number of seconds between each sampling
data_dir=''

def press_cmd(ser0, cmd):

	ser0.write(cmd)
	time.sleep(1)

	reply = ''
	reply = ser0.readline()
	"""
	while ser0.inWaiting() > 0:
		rtd=ser0.read(1)
		reply+=rtd.decode("ascii")
		if rtd == '\n':
		   break
	"""
	return(reply)

def compute_CRC(message):
	crc = 0x0
	for x in range(1,len(message)):
		crc = crc ^ message[x]
	str_crc = '{:x}'.format(crc).upper()
	crc_byte_array = bytearray()
	crc_byte_array.extend(map(ord, str_crc))
	return crc_byte_array
#---------------------------------------------------------------------------
# The main function starts here
#-----------------------------------------------------------------------------
if __name__ == "__main__":
	try:
	# open the serial device
		ser0  = serial.Serial(port=Turboport,
							  baudrate=9600,
							  parity=serial.PARITY_NONE,
							  stopbits=serial.STOPBITS_ONE,
							  bytesize=serial.EIGHTBITS)
		ser0.timeout = 1.5
		ser0.xonxoff = False
		ser0.rtscts = False
		ser0.dsrdtr = False

		# Construct message to agilent controller
		window = bytearray([0x32, 0x32, 0x34])
  
		cmd = bytearray([RD])
		message = bytearray()
		message.append(STX)
		message.append(ADDR)
		message.extend(window)
		message.extend(cmd)
		message.append(ETX)

		# Append CRC
		crc = compute_CRC(message)
		message.extend(crc)
		
		log_dir_path=r"D:\OneDrive - University of Arizona\optical sciences\Research\Erika Hamden Group\Code\Cryocooler_Control_software\Final_code\pressure_log"
		filename    = f'pressure_log_{datetime.now().strftime("%Y%m%d")}.csv'
		dir   = log_dir_path
		fn=os.path.join(log_dir_path,filename)
		print(f'Data will be saved in {fn}')

		if not os.path.exists(dir):
			os.makedirs(dir)

		# if not os.path.exists(html):# copy index.html?
		# 	shutil.copyfile(htmsrc, html)

		# if not os.path.exists(dylink):# create symlink to dygraph?
		# 	os.symlink(dysrc, dylink)

		if not os.path.exists(fn): # write a header?
				writeheader = True
		else:
				writeheader = False

		fp = open(fn, 'a') # open file for append/write
		if writeheader:
			fp.write('time,pressure[mbar]\n')# header

		fp.close()

		while (True):
			fp = open(fn, 'a') # open file for append/write

			output = press_cmd(ser0, message)
			press = ""
			if not output == '':
				# if output is not empty, set press
				press = str(output[6:-6], "utf-8")
			curr_time  = datetime.now().strftime("%D %T")
			dat   = [curr_time, ",", press, "\n"]     # put data in list
			fp.write('{0}, {1}\n'.format(curr_time, press))

			fp.close()
			print('{0}, {1}\n'.format(curr_time, press))
			for i in tqdm(range(SAMPLE_TIME),desc='Reading Pressure in:'):time.sleep(1)

	except KeyboardInterrupt:
		print("Pressure measurement server stopped by Keyboard Interupt. Closing serial Connection.")
	finally:
		ser0.close()
  		

