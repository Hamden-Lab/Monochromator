#importing packages 
#ipython packages 
from IPython.display import clear_output

#number handling
import pandas as pd
import numpy as np

#encoding decodning
import signal
import codecs

#file handling and OS
import os
import sys
import glob

#serial connection 
import serial
from serial import SerialException
import serial.tools.list_ports

#time and datetime package
import datetime 
from datetime import timedelta
import time
from time import sleep

#Lakehore package 
from lakeshore import Model350

#plotly and ploty exprress
import plotly
import plotly.express as px
import plotly.graph_objects as go

def start_connection(cryo_port):
    """Start Serial connection with Cryocooler at port=port"""
    def open_port(cryo_port): 
        try:
            
            ser0 = serial.Serial(port=cryo_port,
                                baudrate=9600, #9600bits/s number of data bits
                                parity=serial.PARITY_NONE, #parity checks if the bit sent is odd or even
                                stopbits=serial.STOPBITS_ONE, #signal is high or low
                                bytesize=serial.EIGHTBITS,
                                timeout=1)
        except SerialException:
            return None
        else: 
            return ser0  
    ser0=open_port(cryo_port)
    while ser0 == None: 
        print("Serial port busy. Waiting to connect")
        time.sleep(2)
        ser0=open_port(cryo_port)
    else: 
        print("Cryocooler Controller Connect")
        return(ser0)
        
#add cooler off function
def stop_connection(ser): 
    try: 
       ser.close()
       print("Connection stopped")
    except: 
       print("Something went wrong")
    return 

def cooler_status(ser0):
    """Command: COOLER=<VAL><CR>
        This command is User locked. This command sets the control mode of the controller.
            Control Modes:
            OFF – The cryocooler ramp down and powered OFF.
            ON – The cryocooler is running in temperature control mode and will attempt to maintain the temperature set using the TTARGET command.
            POWER – The cryocooler is running in power control mode and will maintain the commanded power set using the PWOUT command. 
    """
    ser0.write(b'COOLER')
    time.sleep(1)
    out = ser0.readlines()
    cmd = out[0].decode('utf-8').strip()
    out = out[1].decode('utf-8').strip()
    return cmd,out

def start_cooler_temperature_control(ser0):
    """Command: COOLER=<VAL><CR>
        This command is User locked. This command sets the control mode of the controller.
            Control Modes:
            OFF – The cryocooler ramp down and powered OFF.
            ON – The cryocooler is running in temperature control mode and will attempt to maintain the temperature set using the TTARGET command.
            POWER – The cryocooler is running in power control mode and will maintain the commanded power set using the PWOUT command. 
    """
    value='ON'
    cmdstr= 'COOLER='+str(value)+'\r'
    cmd=bytes(cmdstr,'UTF-8')
    ser0.write(cmd)
    time.sleep(1)
    out =ser0.readlines()
    cmd = out[0].decode('utf-8').strip()
    out = out[1].decode('utf-8').strip()
    print("Cooler started in Temperature mode. Set Temperature using TTARGET command")
    return cmd,out    

def stop_cooler(ser0):
    """Command: COOLER=<VAL><CR>
        This command is User locked. This command sets the control mode of the controller.
            Control Modes:
            OFF – The cryocooler ramp down and powered OFF.
            ON – The cryocooler is running in temperature control mode and will attempt to maintain the temperature set using the TTARGET command.
            POWER – The cryocooler is running in power control mode and will maintain the commanded power set using the PWOUT command. 
    """

    cmdstr= 'COOLER='+'OFF'+'\r'
    cmd=bytes(cmdstr,'UTF-8')
    ser0.write(cmd)
    time.sleep(1)
    out =ser0.readlines()
    # cmd = out[0].decode('utf-8').strip()
    # out = out[1].decode('utf-8').strip()
    print("Cooler Stopped.")
    # return cmd,out

def start_cooler_power_control(ser0): 
    """Command: COOLER=<VAL><CR>
        This command is User locked. This command sets the control mode of the controller.
            Control Modes:
            OFF – The cryocooler ramp down and powered OFF.
            ON – The cryocooler is running in temperature control mode and will attempt to maintain the temperature set using the TTARGET command.
            POWER – The cryocooler is running in power control mode and will maintain the commanded power set using the PWOUT command. 
    """
    value='POWER'
    cmdstr= 'COOLER='+str(value)+'\r'
    cmd=bytes(cmdstr,'UTF-8')
    ser0.write(cmd)
    time.sleep(1)
    out =ser0.readlines()
    cmd = out[0].decode('utf-8').strip()
    out = out[1].decode('utf-8').strip()
    print("Cooler started in Power mode. Set power using PWOUT command")
    return cmd,out

def get_commdanded_power_limits(ser0):
    """Display Current Commanded Power & Power Limits: E
        The current commanded power is current power output that the controller is commanding to be supplied to the cryocooler. The current power limits are the minimum and maximum controller power output levels that the con-troller calculates to be the appropriate limits based on the current conditions in the system.
        
        Use the E command to display the current commanded power and the power limits.
        The first line of the values returned by this command is the maximum allowable power output to the cryocooler for the current cold tip temperature. This number will be either the maximum safe power output, or the user-de-fined maximum power output, whichever is lower. (The maximum safe power output to the cryocooler is a func-tion of the cold tip temperature and increases as the cold tip temperature decreases [see figure 2-6]. The maximum safe power output at 77 K is 165 W.)
        The second line of the values returned by this command is the minimum allowable power output to the cry-ocooler. This number will be either the minimum safe power output, or the user-defined minimum power output, whichever is higher. (The minimum safe power output to the cryocooler is a function of the cold tip temperature, but is steady at 60 W over most of the operating range [see figure 2-6]. The minimum safe power output at 77 K is 60 W.)
        The third line of the values returned by this command is the current commanded power (not necessarily the target power output set for power control mode or the power the cryocooler is using as displayed by the P command). All values are in watts.
    """
    
    ser0.write(b'E\r')
    time.sleep(1)
    out =ser0.readlines()
    #print(out)
    #print("Command Sucessful")
    cmd = out[0].decode('utf-8').strip()
    out = out[1].decode('utf-8').strip()
    return cmd,out


def error_code(ser0):
    """Display Current Commanded Power & Power Limits: ERROR)
    An error code is a six-digit binary number that identifies which, if any, errors are occurring. The position of the 1 within the error code determines what error is being reported (table B-4 in the manual or below). Multiple errors are indicated by multiple 1s in the error code, each 1 representing a different error. An error code consisting of six zeros means there are no errors.
    -----------
    Error Codes: 
        10000000- Over Current
        00000010- Low reject temperature
        (not here: 000100- Serial Communication Error)
        (not here: 001000- Non-Volatile Memory Error)
        (not here: 010000- Watchdog Error)
        (not here: 100000- Temperature Sensor Error)
        00000001- high reject temperature
        11111111-invalid configuration
    """
    ser0.write(b'ERROR\r')
    time.sleep(1)
    out =ser0.readlines()
    cmd = out[0].decode('utf-8').strip()
    out = out[1].decode('utf-8').strip()
    return cmd,out
    
def set_integralconstant(ser0,value):
    """ Set Integral Constant of Temperature Control Loop: KI=<Value>
    In some applications, advanced users experienced in tuning PID control loops may want to modify the PI constants to tune the temperature control loop to better match the dynamics of their individual system. The default integral constant for the MT cryocooler is 1.0.
    
    """
    cmdstr= 'KI='+str(value)+'\r'
    cmd_b =cmdstr.encode('utf-8')
    ser0.write(cmd_b)
    time.sleep(1)
    out =ser0.readlines()
    #print(out)
    cmd = out[0].decode('utf-8').strip()
    out = out[1].decode('utf-8').strip()
    return cmd,out

def get_integralconstant(ser0):
    """Display Integral Constant of Temperature Control Loop: KI""" 
    ser0.write(b'KI\r')
    time.sleep(1)
    out =ser0.readlines()
    #print(out)
    #print("Command Sucessful")
    return out

def set_proportionalconstant(ser0,value):
    """Set Integral Constant of Temperature Control Loop: KI=<Value>
        Use the KP=<Value> command to set the proportional constant of the temperature control loop.
    """
    cmdstr= 'KP='+str(value)+'\r'
    cmd_b= cmdstr.encode(cmdstr)
    ser0.write(cmd_b)
    time.sleep(1)
    out =ser0.readlines()
    #print(out)
    #print("Command Sucessful")
    return out

def get_proportionalconstant(ser0):
    """Display Proportional Constant of Temperature Control Loop: KP
        Use the KP=<Value> command to set the proportional constant of the temperature control loop.
    """ 
    ser0.write(b'KP\r')
    time.sleep(1)
    out =ser0.readlines()
    #print(out)
    #print("Command Sucessful")
    return out

def get_LCD_state(ser0):
    """Returns the current status of the LCD (ON/OFF)
        Command is LCD<CR>
    """
    ser0.write(b'LCD\r')
    time.sleep(1)
    out = ser0.readlines()
    return out
    
def LCD_state_off(ser0):
    """Sets the status of the LCD to OFF
        This command is User locked
        LCD states:
            ON – LCD is regularly updated.
            OFF – LCD is not updated.
    """
    value='OFF'
    cmdstr= 'LCD='+str(value)+'\r'
    cmd=bytes(cmdstr,'UTF-8')
    ser0.write(cmd)
    time.sleep(1)
    out =ser0.readlines()
    cmd = out[0].decode('utf-8').strip()
    out = out[1].decode('utf-8').strip()
    print("LCD off.")
    return cmd,out

def LCD_state_on(ser0):
    """Sets the status of the LCD to ON
        This command is User locked
        LCD states:
            ON – LCD is regularly updated.
            OFF – LCD is not updated.
    """
    value='ON'
    cmdstr= 'LCD='+str(value)+'\r'
    cmd=bytes(cmdstr,'UTF-8')
    ser0.write(cmd)
    time.sleep(1)
    out =ser0.readlines()
    cmd = out[0].decode('utf-8').strip()
    out = out[1].decode('utf-8').strip()
    print("LCD on.")
    return cmd,out

def get_mode(ser0): 
    
    ser0.write(b'MODE\r')
    time.sleep(1)
    out =ser0.readlines()
    #print(out)
    #print("Command Sucessful")
    cmd = out[0].decode('utf-8').strip()
    out = out[1].decode('utf-8').strip()
    return cmd, out

def get_cooler_power(ser0):
    """Display Cooler Power as Measured by Controller: P
    Cooler power as measured by the controller is how much electrical power in watts the cryocooler is using as measured by the controller. (This is not necessarily the same as the power level that the controller is command-ing as displayed by the E command.)
    
    """
    ser0.write(b'P\r')
    time.sleep(1)
    out =ser0.readlines()
    #print(out)
    #print("Command Sucessful")
    cmd = out[0].decode('utf-8').strip()
    out = out[1].decode('utf-8').strip()
    return cmd,out

def get_target_power_output(ser0):
    """Target Power Output
        Use the PWOUT command to display the target power output setting.
        Display Target Power Output: PWOUT
        
        The target power output setting is the power level that the user has set as the target power output to send to the cryocooler when in power control mode. This setting is only a target power level: the actual power output that the controller is commanding is displayed by the E command and is subject to the power limits also displayed by the E command. The default target power output setting is 0 W.
        While any number from 0.0 to 999.99 can be entered as the target power output, the controller will not command a power level that is outside of the currently-calculated allowable operating power range of the cryocooler (as shown using the E command) regardless of the target power output set by the user. Refer to the E command sec-tion for details on how the allowable operating power range is calculated.
    
    """
    ser0.write(b'PWOUT\r')
    time.sleep(1)
    out =ser0.readlines()
    #print(out)
    #print("Command Sucessful")
    return out

def set_target_power_output(ser0,value):
    """Target Power Output
        Use the PWOUT=<Value> command to change the target power output setting.
        Display Target Power Output: PWOUT=<value>
        
        The target power output setting is the power level that the user has set as the target power output to send to the cryocooler when in power control mode. This setting is only a target power level: the actual power output that the controller is commanding is displayed by the E command and is subject to the power limits also displayed by the E command. The default target power output setting is 0 W.
        While any number from 0.0 to 999.99 can be entered as the target power output, the controller will not command a power level that is outside of the currently-calculated allowable operating power range of the cryocooler (as shown using the E command) regardless of the target power output set by the user. Refer to the E command sec-tion for details on how the allowable operating power range is calculated.
    """
    cmdstr= 'PWOUT='+str(value)+'\r'
    # cmd_b= cmdstr.encode(cmdstr)
    cmd=bytes(cmdstr,'UTF-8')
    ser0.write(cmd)
    time.sleep(1)
    out =ser0.readlines()
    #print(out)
    #print("Command Sucessful")
    return out

def get_temperature(ser0):
    import datetime
    """Cold Tip Temperature: Display Cold-Tip Temperature"""
    data = {
    'cryo_temp': [],
    'time':[]}
    #while True: 
    ser0.write(b'TC\r')
    time.sleep(1)
    out =ser0.readlines()
    #print(out)
    cmd = out[0].decode('utf-8').strip()
    temperature = out[1].decode('utf-8').strip()
    data['cryo_temp']=float(temperature)
    data['time']=datetime.datetime.now()
    return data

def get_reject_temp(ser0):
    import datetime
    """Display the reject temperature in Celcius
    Returns the current reject temperature measured at the base of the fins on the cooler.
    """
    data = {
    'reject_temp': [],
    'time':[]}
    #while True: 
    ser0.write(b'TEMP RJ\r')
    time.sleep(1)
    out =ser0.readlines()
    #print(out)
    cmd = out[0].decode('utf-8').strip()
    temperature = out[1].decode('utf-8').strip()
    data['reject_temp']=float(temperature)
    data['time']=datetime.datetime.now()
    return data

def get_target_temperature(ser0):
    
    """Target Temperature: Get Target Temperature: TTARGET
        Use the TTARGET=<Value> command to set the target temperature.
        The target temperature is the target cold tip temperature that the controller will try to attain, ±0.1 K, when the controller is in temperature control mode. The default target temperature is 77 K.
    
    """
    ser0.write(b'TTARGET\r')
    time.sleep(1)
    out =ser0.readlines()
    #print(out)
    #print("Command Sucessful")
    return out

def set_target_temperature(ser0,value):
    """Target Temperature: Set Target Temperature: TTARGET
        Use the TTARGET command to display the target temperature.
        The target temperature is the target cold tip temperature that the controller will try to attain, ±0.1 K, when the controller is in temperature control mode. The default target temperature is 77 K.
    """
    cmdstr= 'TTARGET='+str(value)+'\r'
    cmd=bytes(cmdstr,'utf-8')
    ser0.write(cmd)
    time.sleep(1)
    out =ser0.readlines()
    #print(out)
    #print("Command Sucessful")
    return out

def version(ser0): 
    ser0.write(b'VERSION\r')
    time.sleep(1)
    out =ser0.readlines();
    #print(out)
    #print("Command Sucessful")
    cmd = out[0].decode('utf-8').strip()
    out = out[1].decode('utf-8').strip()
    return cmd,str(out)



def set_password(ser0,passwd):
    """Set User Password: PASS=<Value>
        Use the PASS=<Value> command to define a user password.
        Enter an alphanumeric value between 1 and 10 characters in length. This value will replace the previous password.
        A return of 001.00 confirms that the password was successfully changed.
    """
    cmdstr= 'PASS='+str(passwd)+'\r'
    cmd_b= cmdstr.encode(cmdstr)
    ser0.write(cmd_b)
    time.sleep(1)
    out =ser0.readlines()
    #print(out)
    #print("Command Sucessful")
    return out


def cryo_temp_single_read(ser0):
    import datetime
    out = get_temperature(ser0)
    cryo_temp_df=pd.DataFrame(data=[out])
    return cryo_temp_df

def reject_temp_single_read(ser0):
    import datetime
    out = get_reject_temp(ser0)
    reject_temp_df=pd.DataFrame(data=[out])
    return reject_temp_df

def cryo_temp_log_duration(duration=5):
    #log temperature data for {duration} seconds
    import datetime
    start_log=datetime.datetime.now()
    elapsed_time=datetime.datetime.now()-start_log
    cryo_temp_df =pd.DataFrame(data=None)
    out = get_temperature()
    cryo_temp_df=cryo_temp_df.append(pd.DataFrame([out[1:]]))
    while elapsed_time.seconds<duration: 
        out = get_temperature()
        cryo_temp_df=cryo_temp_df.append(pd.DataFrame([out[1:]],columns={"time","temp_cryo"}))
        elapsed_time=datetime.now()-start_log       
    return cryo_temp_df
