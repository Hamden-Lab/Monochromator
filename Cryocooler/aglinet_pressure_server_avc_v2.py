#!/usr/bin/python

import signal
import shutil
import serial
import os
import sys
import time
from tqdm.auto import tqdm
from datetime import datetime,timedelta
import logging



"""stop_dict = {'window' : bytearray([0x30, 0x30, 0x30]), 'CRC' : bytearray([0x42, 0x32])}
soft_start_on_dict = {'window' : bytearray([0x31, 0x30, 0x30]), 'CRC' : bytearray([0x42, 0x32])}
soft_start_off_dict = {'window' : bytearray([0x31, 0x30, 0x30]), 'CRC' : bytearray([0x42, 0x33])}
pump_status_dict = {'window' : bytearray([0x32, 0x30, 0x35]), 'CRC' : bytearray([0x38, 0x37]), 'DATA' = bytearray([0x30, 0x30, 0x30, 0x30, 0x30, 0x30])}
serial_type_dict = {'window' : bytearray([0x35, 0x30, 0x34]), 'CRC' : bytearray([0x38, 0x31])}
"""

""" "Constants" Definitions """
STX = 0x02
WR = 0x31
ON = 0x31
RD = 0x30
OFF = 0x30
ETX = 0x03
ACK = 0x06
global Turboport
Turboport= 'COM4'
SAMPLE_TIME = 60 # Number of seconds between each sampling
data_dir=''
window = {'start': bytearray([0x30, 0x30, 0x30]), 'stop': bytearray([0x30, 0x30, 0x30]), 'soft_start_on': bytearray([0x31, 0x30, 0x30]), 'soft_start_off': bytearray([0x31, 0x30, 0x30]), 'pump_status': bytearray([0x32, 0x30, 0x35]), 'serial_type' : bytearray([0x35, 0x30, 0x34])}
CRC = {'start': bytearray([0x42, 0x33]), 'stop': bytearray([0x42, 0x32]), 'soft_start_on': bytearray([0x42, 0x32]), 'soft_start_off': bytearray([0x42, 0x33]), 'pump_status': bytearray([0x38, 0x37]), 'serial_type': bytearray([0x38, 0x31]), "toPC_start_stop": bytearray([0x38, 0x35]), "toPC_read_pump": bytearray([0x38, 0x37]), "toPC_serial_type": bytearray([0x42, 0x30])}
ADDR = {'start': 0x80, 'stop' : 0x80, 'soft_start_on': 0x80, 'soft_start_off': 0x80, 'pump_status' : 0x83, 'serial_type': 0x83}

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

		# Construct start command to agilent controller
		start = bytearray()
		start.append(STX)
		start.append(ADDR['start'])
		start.extend(window['start'])
		start.append(WR)
		start.append(ON)
		start.append(ETX)
		start.extend(CRC['start'])
		"""# Append CRC
		crc = compute_CRC(start)
		start.extend(crc)"""
		# print(message.hex())

		# Construct stop command to agilent controller
		stop = bytearray()
		stop.append(STX)
		stop.append(ADDR['stop'])
		stop.extend(window['stop'])
		stop.append(WR)
		stop.append(OFF)
		stop.append(ETX)
		stop.extend(CRC['stop'])

		# Construct soft_start_on command to agilent controller
		soft_start_on = bytearray()
		soft_start_on.append(STX)
		soft_start_on.append(ADDR['soft_start_on'])
		soft_start_on.extend(window['soft_start_on'])
		soft_start_on.append(WR)
		soft_start_on.append(ON)
		soft_start_on.append(ETX)
		soft_start_on.extend(CRC['soft_start_on'])

		# Construct soft_start_off command to agilent controller
		soft_start_off = bytearray()
		soft_start_off.append(STX)
		soft_start_off.append(ADDR['soft_start_off'])
		soft_start_off.extend(window['soft_start_off'])
		soft_start_off.append(WR)
		soft_start_off.append(OFF)
		soft_start_off.append(ETX)
		soft_start_off.extend(CRC['soft_start_off'])

		# Construct pump_status command to agilent controller
		pump_status = bytearray()
		pump_status.append(STX)
		pump_status.append(ADDR['pump_status'])
		pump_status.extend(window['pump_status'])
		pump_status.append(RD)
		pump_status.append(ETX)
		pump_status.extend(CRC['pump_status'])

		# Construct serial_type command to agilent controller
		serial_type = bytearray()
		serial_type.append(STX)
		serial_type.append(ADDR['serial_type'])
		serial_type.extend(window['serial_type'])
		serial_type.append(RD)
		serial_type.append(ETX)
		serial_type.extend(CRC['serial_type'])

		"controller -> PC commands? not sure if this is the right setup"

		#Construct start command to PC
		startC = bytearray()
		startC.append(STX)
		startC.append(ADDR['start'])
		startC.append(ACK)
		startC.append(ETX)
		startC.extend(CRC['toPC_start_stop'])

		#Construct stop command to PC
		stopC = bytearray()
		stopC.append(STX)
		stopC.append(ADDR['stop'])
		stopC.append(ACK)
		stopC.append(ETX)
		stopC.extend(CRC['toPC_start_stop'])		
		
		#Construct pump_status command to PC
		stopC = bytearray()
		stopC.append(STX)
		stopC.append(ADDR['pump_status'])
		stopC.append(ACK)
		stopC.append(ETX)
		stopC.extend(CRC['toPC_read_pump'])	

		#Construct serial_type command to PC
		stopC = bytearray()
		stopC.append(STX)
		stopC.append(ADDR['start'])
		stopC.append(ACK)
		stopC.append(ETX)
		stopC.extend(CRC['toPC_serial_type'])			
		
		

		"alternatively, can you use loggers to capture the messages that the controller is sending back to the pc?"

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
  		

