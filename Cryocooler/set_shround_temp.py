#importing packages 
from lakeshore import Model350
import pandas as pd
from IPython.display import clear_output
import numpy as np
from serial import SerialException

import signal
import codecs

import serial
import os
import sys
import time
from time import sleep
# import Cryocode
import serial.tools.list_ports
from datetime import datetime,timedelta

import plotly.express as px
import plotly.graph_objects as go

def start_connection(cryo_port):
    """Start Serial connection with Cryocooler at port=port"""
    def open_port(cryo_port): 
        try:
            
            ser0 = serial.Serial(port=cryo_port,
                                baudrate=4800, #4800bits/s number of data bits
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
        print("Connected")
        return(ser0)
    
def stop_connection(ser): 
    try: 
       ser.close()
       print("Connection stopped")
    except: 
       print("Something went wrong")
    return 

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

def version(ser0): 
    ser0.write(b'VERSION\r')
    time.sleep(1)
    out =ser0.readlines();
    #print(out)
    #print("Command Sucessful")
    cmd = out[0].decode('utf-8').strip()
    out = out[1].decode('utf-8').strip()
    return cmd,str(out)

def serial_number(ser0): 

    ser0.write(b'SERIAL\r')
    time.sleep(1)
    out =ser0.readlines()
    #print(out)
    #print("Command Sucessful")
    cmd = out[0].decode('utf-8').strip()
    out = out[1].decode('utf-8').strip()
    return cmd,out

def get_mode(): 
    """Display Configured Cryocooler Type
        Soft-Stop Control Mode: Set Soft-Stop Control Mode: SET SSTOPM=<Value>
        000.00 = Sunpower reserved mode
        001.00 = CryoTel CT
        002.00 = CryoTel GT
        003.00 = CryoTel MT
        
        For Hamden lab this is always set to 3.00 and never changed as we have only the MT cryocooler
    """
    
    ser0.write(b'MODE\r')
    time.sleep(1)
    out =ser0.readlines()
    #print(out)
    #print("Command Sucessful")
    cmd = out[0].decode('utf-8').strip()
    out = out[1].decode('utf-8').strip()
    return cmd, out

def get_pid_mode(): 
    """Display Current Control Mode: SET PID
        Use the SET PID command to display the controller control mode that is currently in use.
        A return of 000.00 indicates that power control mode is currently in use.
        A return of 002.00 indicates that temperature control mode is currently in use.
    """
    ser0.write(b'SET PID\r')
    time.sleep(1)
    out =ser0.readlines()
    #print(out)
    #print("Command Sucessful")
    cmd = out[0].decode('utf-8').strip()
    out = out[1].decode('utf-8').strip()
    return cmd,out

def set_pid_mode(value): 
    """Display Current Control Mode: SET PID = <Value>
        Use the SET PID=<Value> command to change the control mode that’s currently being used.
        Entering a value of 0 changes the control mode currently in use to the power control mode. In this mode, the controller will supply power to the cryocooler at the target power level set by the user. (You can use the SET PWROUT=<Value> command to change the target power output setting.)
        Entering a value of 2 changes the control mode currently in use to the temperature control mode. In this mode, the controller will try to maintain the cold tip at the target temperature setting. (You can use the SET TTARGET=<Value> command to change the target temperature setting.)
        The control mode will revert to the default control mode upon cycling the power. (You can use the SAVE PID command to change the default control mode to the control mode that’s currently in use.)
    """
    cmdstr= 'SET PID='+str(value)+'\r'
    cmd=bytes(cmdstr,'UTF-8')
    ser0.write(cmd)
    time.sleep(1)
    out =ser0.readlines()
    #print(out)
    #print("Command Sucessful")
    cmd = out[0].decode('utf-8').strip()
    out = out[1].decode('utf-8').strip()
    return cmd,out

def save_pid_mode(): 
    """Change Default Control Mode: SAVE PID
        Use the SAVE PID command to save the control mode that is currently in use as the new default control mode. The factory-set default control mode is temperature control mode. (You can use the SET PID command to dis-play the control mode that is currently in use, and you can use the SET PID=<Value> command to specify which control mode to use.) The control mode that you save with this command will be the control mode used after the system is power cycled.
        A return of 000.00 indicates that power control mode has been saved as the default control mode. A return of 002.00 indicates that temperature control mode has been saved as the default control mode.
    """
    ser0.write(b'SAVE PID')
    time.sleep(1)
    out =ser0.readlines()
    #print(out)
    #print("Command Sucessful")
    cmd = out[0].decode('utf-8').strip()
    out = out[1].decode('utf-8').strip()
    return cmd,out

def factory_reset():
    """Controller Parameters: Reset Controller Parameters to Factory Defaults
    Use the RESET=F command to reset the controller parameters to their factory defaults as listed in table B-3 of the manual.
    """
    ser0.write(b'RESET=F\r')
    time.sleep(1)
    out =ser0.readlines()
    cmd = out[0].decode('utf-8').strip()
    out = out[1].decode('utf-8').strip()
    return cmd,out

def get_cooler_power():
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

def get_commdanded_power_limits():
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

def error_code():
    """Display Current Commanded Power & Power Limits: ERROR)
    An error code is a six-digit binary number that identifies which, if any, errors are occurring. The position of the 1 within the error code determines what error is being reported (table B-4 in the manual or below). Multiple errors are indicated by multiple 1s in the error code, each 1 representing a different error. An error code consisting of six zeros means there are no errors.
    -----------
    Error Codes: 
        000001- Over Current
        000010- Jumper Error
        000100- Serial Communication Error
        001000- Non-Volatile Memory Error
        010000- Watchdog Error
        100000- Temperature Sensor Error
    """
    ser0.write(b'ERROR\r')
    time.sleep(1)
    out =ser0.readlines()
    cmd = out[0].decode('utf-8').strip()
    out = out[1].decode('utf-8').strip()
    return cmd,out

def set_integralconstant(value):
    """ Set Integral Constant of Temperature Control Loop: SET KI=<Value>
    In some applications, advanced users experienced in tuning PID control loops may want to modify the PI constants to tune the temperature control loop to better match the dynamics of their individual system. The default integral constant for the MT cryocooler is 1.0.
    """
    cmdstr= 'SET KI='+str(value)+'\r'
    cmd_b =cmdstr.encode('utf-8')
    ser0.write(cmd_b)
    time.sleep(1)
    out =ser0.readlines()
    #print(out)
    cmd = out[0].decode('utf-8').strip()
    out = out[1].decode('utf-8').strip()
    return cmd,out

def get_integralconstant():
    """Display Integral Constant of Temperature Control Loop: SET KI""" 
    ser0.write(b'SET KI\r')
    time.sleep(1)
    out =ser0.readlines()
    #print(out)
    #print("Command Sucessful")
    return out

def state():
    """Display Operating State:STATE
        Use the STATE command to display a list of the controller’s operating parameters (as described in table A-5) and their current values. All of the individual parameter values can also be displayed using the corresponding individual parameter display commands listed elsewhere in this appendix. This command is useful when troubleshooting the system.
            
        The operating state of the controller is defined as the current value of the controller's operating parameters which are listed and described in table A-5. The factory default values for these parameters (except TSTAT) are listed in table A-3.
        
         Cryocooler Model Designation
            TSTATM          Thermostat Mode
            TSTAT           Thermostat State
            SSTOPM          Soft-Stop Control Mode
            SSTOP           Soft-Stop State
            PID             Control Mode Currently in Use
            LOCK            User Lock State
            MAX             User-Defined Maximum Power Output
            MIN             User-Defined Minimum Power Output
            PWOUT           Target Power Output
            TTARGET         Target Temperature
            TBAND           Temperature Band
            TEMP KP         Proportional Constant of Temperature Control Loop
            TEMP KI         Integral Constant of Temperature Control Loop
    """
    ser0.write(b'STATE\r')
    time.sleep(1)
    out =ser0.readlines()
    #print(out)
    #print("Command Sucessful")
    return out

def set_proportionalconstant(value):
    """Set Integral Constant of Temperature Control Loop: SET KI=<Value>
        Use the SET KP=<Value> command to set the proportional constant of the temperature control loop.
    """
    cmdstr= 'SET KP='+str(value)+'\r'
    cmd_b= cmdstr.encode(cmdstr)
    ser0.write(cmd_b)
    time.sleep(1)
    out =ser0.readlines()
    #print(out)
    #print("Command Sucessful")
    return out

def get_proportionalconstant():
    """Display Proportional Constant of Temperature Control Loop: SET KP
        Use the SET KP=<Value> command to set the proportional constant of the temperature control loop.
    """ 
    ser0.write(b'SET KP\r')
    time.sleep(1)
    out =ser0.readlines()
    #print(out)
    #print("Command Sucessful")
    return out


"""Soft-Stop Control Mode
Set Soft-Stop Control Mode: SET SSTOPM=<Value>
Display Soft-Stop Control Mode: SET SSTOPM"""

def get_soft_stop_mode():
    """
    Use the SET SSTOPM command to display the current soft-stop control mode of the controller, i.e., which of the
    two methods of controlling the soft-stop function has been chosenn.    

    Command input: A return of 000.00 (mode 0) indicates that only the SET SSTOP=<Value> command can be used to enable
    or disable the soft-stop function.
    Only digital Input 1: A return of 001.00 (mode 1) indicates that only Digital Input 1 (pin 5 on the controller’s I/O connector) can be
    used to enable or disable the soft-stop function.
    
    The soft-stop control mode identifies the method that has been selected to enable and disable the soft-stop func-tion. There are two methods: one is to use the SET SSTOP=<Value> command; the other is to use Digital In-put 1 (pin 5 on the controller’s I/O connector). 
    
    In the Digital Input 1 method, setting the input high enables the soft-stop function. The Onboard Isolated 5 V output on pin 10 or 12 on the controller’s I/O connector can be used to set the input high. Setting the input low or disconnecting it disables the soft-stop function.
    """
    ser0.write(b'SET SSTOPM\r')
    time.sleep(1)
    out =ser0.readlines()
    #print(out)
    #print("Command Sucessful")
    return out

def set_soft_stop_mode(value=3):
    """
    Soft-Stop Control Mode
    Set Soft-Stop Control Mode" SET SSTOP=<Value>
    """
    if value==3: 
        cmdstr= 'SET SSTOPM='+str(value)+'\r'
        cmd=bytes(cmdstr,'UTF-8')
        ser0.write(cmd)
        time.sleep(1)
        out =ser0.readlines()
        #print(out)
        #print("Command Sucessful")
        cmd = out[0].decode('utf-8').strip()
        out = out[1].decode('utf-8').strip()
    else: 
        print("Are you trying to set the controller to operate with MT? Then use mode 3. For details refer to the manual")
        cmd="Error"
        out="Error"
    #print(out)
    #print("Command Sucessful")
    return cmd, out

def get_soft_stop_state():
    """Soft-Stop Control Mode
        Display Soft-Stop Control Mode: SET SSTOPM
        
        Use the SET SSTOP command to display the current soft-stop state, i.e., whether the soft-stop function is ena-bled or disabled.
        A return of 000.00 indicates that the soft-stop function is disabled.
        A return of 001.00 indicates that soft-stop function is enabled.
    """
    ser0.write(b'SET SSTOP\r')
    time.sleep(1)
    out =ser0.readlines()
    #print(out)
    #print("Command Sucessful")
    return out

def set_soft_stop_state(value):
    """
        The soft-stop state indicates whether the soft-stop function is enabled or disabled. With the soft-stop function ena-bled, the cryocooler is stopped, or is being ramped down, parked, and stopped, and will not start up when power is cycled to the controller. With the soft-stop function disabled, the cryocooler is in the process of starting up or is running, and will start up normally when power to the controller is cycled.
        Description: 
        Use the GET SSTOP=<Value> command to begin a soft stop of the cryocooler, or to start the cryocooler from its stopped state. A soft stop is the recommended shutdown method in which the controller slowly ramps down operation of the cryocooler and parks the piston against the end stop before shutting it down completely. This re-duces vibration, allows the controller to remain on, and reduces the risk of self-excitation (when turning off the cryocooler at very low temperatures–below 77 K). This command will only work if the soft-stop control mode is set to mode 0. (If set to mode 1, then Digital Input 1 is used to control the soft-stop state.)
        Usage: 
        Entering a value of 0 restarts a stopped cryocooler and disables the soft-stop function.
        Entering a value of 1 begins a soft stop of the cryocooler and enables the soft-stop function. Do not remove power from the controller until the shutdown process has been completed and the word COMPLETE is displayed on the computer screen.
    """
    
    cmdstr= 'SET SSTOP='+str(value)+'\r'
    cmd=bytes(cmdstr,'UTF-8')
    ser0.write(cmd)
    time.sleep(1)
    out =ser0.readlines()
    #print(out)
    #print("Command Sucessful")
    
    return out

def get_target_power_output():
    """Target Power Output
        Use the SET PWOUT command to display the target power output setting.
        Display Target Power Output: SET PWOUT
        
        The target power output setting is the power level that the user has set as the target power output to send to the cryocooler when in power control mode. This setting is only a target power level: the actual power output that the controller is commanding is displayed by the E command and is subject to the power limits also displayed by the E command. The default target power output setting is 0 W.
        While any number from 0.0 to 999.99 can be entered as the target power output, the controller will not command a power level that is outside of the currently-calculated allowable operating power range of the cryocooler (as shown using the E command) regardless of the target power output set by the user. Refer to the E command sec-tion for details on how the allowable operating power range is calculated.
    
    """
    ser0.write(b'SET PWOUT\r')
    time.sleep(1)
    out =ser0.readlines()
    #print(out)
    #print("Command Sucessful")
    return out

def set_target_power_output(value):
    """Target Power Output
        Use the SET PWOUT=<Value> command to change the target power output setting.
        Display Target Power Output: SET PWOUT=<value>
        
        The target power output setting is the power level that the user has set as the target power output to send to the cryocooler when in power control mode. This setting is only a target power level: the actual power output that the controller is commanding is displayed by the E command and is subject to the power limits also displayed by the E command. The default target power output setting is 0 W.
        While any number from 0.0 to 999.99 can be entered as the target power output, the controller will not command a power level that is outside of the currently-calculated allowable operating power range of the cryocooler (as shown using the E command) regardless of the target power output set by the user. Refer to the E command sec-tion for details on how the allowable operating power range is calculated.
    """
    cmdstr= 'SET PWOUT='+str(value)+'\r'
    # cmd_b= cmdstr.encode(cmdstr)
    cmd=bytes(cmdstr,'UTF-8')
    ser0.write(cmd)
    time.sleep(1)
    out =ser0.readlines()
    #print(out)
    #print("Command Sucessful")
    return out


def get_target_temperature():
    """Target Temperature: Get Target Temperature: SET TTARGET
        Use the SET TTARGET=<Value> command to set the target temperature.
        The target temperature is the target cold tip temperature that the controller will try to attain, ±0.1 K, when the controller is in temperature control mode. The default target temperature is 77 K.
    
    """
    ser0.write(b'SET TTARGET\r')
    time.sleep(1)
    out =ser0.readlines()
    #print(out)
    #print("Command Sucessful")
    return out

def set_target_temperature(value):
    """Target Temperature: Set Target Temperature: SET TTARGET
        Use the SET TTARGET command to display the target temperature.
        The target temperature is the target cold tip temperature that the controller will try to attain, ±0.1 K, when the controller is in temperature control mode. The default target temperature is 77 K.
    """
    cmdstr= 'SET TTARGET='+str(value)+'\r'
    cmd=bytes(cmdstr,'utf-8')
    ser0.write(cmd)
    time.sleep(1)
    out =ser0.readlines()
    #print(out)
    #print("Command Sucessful")
    return out

def get_target_band():
    """Get Temperature Band: SET TBAND
        Use the SET TBAND command to display the ± temperature band in kelvins.
        The temperature band is the ± tolerance band used with the target temperature to determine when the cold tip is considered to be at the target temperature (for the sole purposes of operating the controller’s LEDs and the Digital Out 4 pin on the controller’s I/O connector). For example, if the target temperature is set at 77 K, and the ± tem-perature band is set at ±0.5 K, and the controller is in temperature control mode, then the green LED will be on and the Digital Out 4 pin will be high (5 V) when the cold tip temperature is 77 K ±0.5 K. Also, the red LED will be on and the Digital Out 4 pin will be low (0 V) when the cold tip temperature is outside of that range. The de-fault ± temperature band is ±0.5 K.
    
    """
    ser0.write(b'SET TBAND\r')
    time.sleep(1)
    out =ser0.readlines()
    #print(out)
    #print("Command Sucessful")
    return out

def set_target_band(band):
    """Set Temperature Band: SET TBAND=<Value>
        Use the SET TBAND=<Value> command to set the ± temperature band in kelvins.
        The temperature band is the ± tolerance band used with the target temperature to determine when the cold tip is considered to be at the target temperature (for the sole purposes of operating the controller’s LEDs and the Digital Out 4 pin on the controller’s I/O connector). For example, if the target temperature is set at 77 K, and the ± tem-perature band is set at ±0.5 K, and the controller is in temperature control mode, then the green LED will be on and the Digital Out 4 pin will be high (5 V) when the cold tip temperature is 77 K ±0.5 K. Also, the red LED will be on and the Digital Out 4 pin will be low (0 V) when the cold tip temperature is outside of that range. The de-fault ± temperature band is ±0.5 K.
    """
    cmdstr= 'SET TBAND='+str(band)+'\r'
    cmd_b= cmdstr.encode(cmdstr)
    ser0.write(cmd_b)
    time.sleep(1)
    out =ser0.readlines()
    #print(out)
    #print("Command Sucessful")
    return out

def get_thermostat_mode():
    """Get Thermostat Mode: Display Thermostat Mode: SET TSTATM
        The thermostat mode indicates whether the controller is set to work with a thermostat (mode 1), or is set to not work with a thermostat (mode 0). When in mode 1, a thermostat connected across pin 7 (Digital Input 3) and pin 10 or 12 (Onboard Isolated 5 V Output) of the controller’s I/O connector can be used to shut down the cryocooler when the temperature is outside of a desired temperature range. (As long as pin 7 is high [thermostat closed], a running cryocooler is allowed to continue running, but anytime the thermostat becomes open, the controller shuts down the cryocooler. At that point, the thermostat must be closed before the cryocooler can be started up again. This does not generate an error and does not require a power cycle to restart.)
    """
    ser0.write(b'SET TSTATM\r')
    time.sleep(1)
    out =ser0.readlines()
    #print(out)
    #print("Command Sucessful")
    return out

def set_thermostat_mode(mode):
    """Set Thermostat Mode: SET Thermostat Mode: SET TSTATM=<Mode>
        Use the SET TSTATM=<Value> command to set the thermostat mode of the controller.

        The thermostat mode indicates whether the controller is set to work with a thermostat (mode 1), or is set to not work with a thermostat (mode 0). When in mode 1, a thermostat connected across pin 7 (Digital Input 3) and pin 10 or 12 (Onboard Isolated 5 V Output) of the controller’s I/O connector can be used to shut down the cryocooler when the temperature is outside of a desired temperature range. (As long as pin 7 is high [thermostat closed], a running cryocooler is allowed to continue running, but anytime the thermostat becomes open, the controller shuts down the cryocooler. At that point, the thermostat must be closed before the cryocooler can be started up again. This does not generate an error and does not require a power cycle to restart.)
    
        Entering a value of 0 (mode 0) disables the controller's ability to work with a thermostat.
        Entering a value of 1 (mode 1) enables the controller's ability to work with a thermostat.
    """
    cmdstr= 'SET TSTATM='+str(mode)+'\r'
    cmd_b= cmdstr.encode(cmdstr)
    ser0.write(cmd_b)
    time.sleep(1)
    out =ser0.readlines()
    #print(out)
    #print("Command Sucessful")
    return out

def get_thremostat_state():
    """Get Thermostat STATE: Display Thermostat STATE: SET TSTAT
        Use the TSTAT command to display the current state of the thermostat.

        The thermostat state indicates the current state (open or closed) of a thermostat connected across pin 7 and pin 10 or 12 of the controller’s I/O connector. This state is only meaningful if thermostat mode has been enabled (using the SET TSTATM=1 command) and a thermostat is installed.
        If the thermostat state is open, that means the cryocooler has been automatically shut down or is in the process of automatically shutting down. The thermostat must then be closed before the cryocooler can be started up again. Startup will happen automatically when the thermostat closes.

        A return of 000.00 indicates that the thermostat is open.
        A return of 001.00 indicates that the thermostat is closed.
    """
    ser0.write(b'SET TSTAT\r')
    time.sleep(1)
    out =ser0.readlines()
    #print(out)
    #print("Command Sucessful")
    return out

"""User-Defined Minimum & Maximum Power Output
Set User-Defined Minimum Power Output: SET MIN=<Value>
Display User-Defined Minimum Power Output: SET MIN
Set User-Defined Maximum Power Output: SET MAX=<Value>
Display User-Defined Maximum Power Output: SET MAX
Display User-Defined Minimum & Maximum Power Output: SHOW MX"""

def get_user_min_power():
    """Set Thermostat Mode: Display Thermostat Mode: SET TSTATM
        Use the SET MIN=<Value> command to set the user-defined minimum power output setting for the controller.
        
        The user-defined minimum power output setting for the controller is used in both the power control mode and the temperature control mode. Entering a value that is less than the minimum safe power output to the cryocooler (60 W at 77 K) will not result in damage to the cryocooler because the controller will not command a power that is less than the minimum safe power output to the cryocooler. The minimum power output to the cryocooler will either be the minimum safe power output, or the user-defined minimum power output, whichever is higher. The default user-defined minimum power output setting is 0 W.
        The user-defined maximum power output setting for the controller is used in both the power control mode and the temperature control mode. Entering a value that exceeds the maximum safe power output to the cryocooler will not result in damage to the cryocooler because the controller will not command a power that exceeds the maxi-mum safe power output to the cryocooler. The maximum safe power output to the cryocooler is a function of the cold tip temperature and increases as the cold tip temperature decreases. (It’s 165 W at 77 K.) The maximum power output to the cryocooler will be either the maximum safe power output, or the user-defined maximum power output, whichever is lower. The default user-defined maximum power output setting is 300 W.
    """
    ser0.write(b'SET MIN\r')
    time.sleep(1)
    out =ser0.readlines()
    #print(out)
    #print("Command Sucessful")
    return out

def get_user_max_power():
    """Set Thermostat Mode: Display Thermostat Mode: SET TSTATM
        Use the SET MAX command to display the user-defined maximum power output setting for the controller.
        
        The user-defined minimum power output setting for the controller is used in both the power control mode and the temperature control mode. Entering a value that is less than the minimum safe power output to the cryocooler (60 W at 77 K) will not result in damage to the cryocooler because the controller will not command a power that is less than the minimum safe power output to the cryocooler. The minimum power output to the cryocooler will either be the minimum safe power output, or the user-defined minimum power output, whichever is higher. The default user-defined minimum power output setting is 0 W.
        The user-defined maximum power output setting for the controller is used in both the power control mode and the temperature control mode. Entering a value that exceeds the maximum safe power output to the cryocooler will not result in damage to the cryocooler because the controller will not command a power that exceeds the maxi-mum safe power output to the cryocooler. The maximum safe power output to the cryocooler is a function of the cold tip temperature and increases as the cold tip temperature decreases. (It’s 165 W at 77 K.) The maximum power output to the cryocooler will be either the maximum safe power output, or the user-defined maximum power output, whichever is lower. The default user-defined maximum power output setting is 300 W.
    """
    ser0.write(b'SET MAX\r')
    time.sleep(1)
    out =ser0.readlines()
    #print(out)
    #print("Command Sucessful")
    return out

def get_user_min_max_power():
    """Set Thermostat Mode: Display Thermostat Mode: SET TSTATM
        Use the SHOW MX command to display the user-defined minimum and maximum power output settings for the controller. (You can also use the SET MIN and SET MAX commands to display the same settings individually.)
        The first line of the values returned by this command is the used-defined minimum power output setting for the controller. The second line of the values returned by this command is the used-defined maximum power output setting for the controller. All values are in watts.
    """
    ser0.write(b'SHOW MX\r')
    time.sleep(1)
    out =ser0.readlines()
    #print(out)
    #print("Command Sucessful")
    return out

"""User-Lockable Commands
Lock User-Lockable Commands: LOCK=<Password>
Unlock User-Lockable Commands: UNLOCK=<Password>
Set User Password: SET PASS=<Value>
Display User Lock State: LOCK

Commands in the user-lockable commands group (table B-1) can be locked so that the parameters associated with those commands cannot be changed. To lock the commands, you must enter a user password. In order to unlock a command, you must unlock the entire group of commands by entering the user password. The default user pass-word is STIRLING, but you can change the user password when the commands are unlocked. The controller is shipped with these commands in the unlocked state. If the commands are locked and the user password has been misplaced, the controller must be sent back to Sunpower so that we can unlock the commands.
"""

def get_lock_state():
    """Display User Lock State: LOCK
        Use the LOCK command to display the user lock state.
        A return of 000.00 indicates that the commands are unlocked.
        A return of 001.00 indicates that the commands are locked.
    """
    ser0.write(b'LOCK\r')
    time.sleep(1)
    out =ser0.readlines()
    #print(out)
    #print("Command Sucessful")
    return out

def lock_ud_commands(passwd):
    """Lock User-Lockable Commands: LOCK=<Password>
        Use the LOCK=<Password> command to lock access to the commands in the user-lockable commands group (table B-1). “<Password>” means “type the currently-set password”.
    
    """
    cmdstr= 'LOCK='+str(passwd)+'\r'
    cmd_b= cmdstr.encode(cmdstr)
    ser0.write(cmd_b)
    time.sleep(1)
    out =ser0.readlines()
    #print(out)
    #print("Command Sucessful")
    return out

def unlock_ud_commands(passwd):
    """UNLock User-Lockable Commands: UNLOCK=<Password>
        Use the UNLOCK=<Password> command to unlock access to the commands in the user-lockable commands group (table B-1). “<Password>” means “type the currently-set password”.
        A return of 000.00 confirms that the commands are unlocked.
    """
    cmdstr= 'UNLOCK='+str(passwd)+'\r'
    cmd_b= cmdstr.encode(cmdstr)
    ser0.write(cmd_b)
    time.sleep(1)
    out =ser0.readlines()
    #print(out)
    #print("Command Sucessful")
    return out

def set_password(passwd):
    """Set User Password: SET PASS=<Value>
        Use the SET PASS=<Value> command to define a user password.
        Enter an alphanumeric value between 1 and 10 characters in length. This value will replace the previous password.
        A return of 001.00 confirms that the password was successfully changed.
    """
    cmdstr= 'SET PASS='+str(passwd)+'\r'
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
def cryo_temp_log_duration(duration=5):
    #log temperature data for {duration} seconds
    import datetime
    start_log=datetime.datetime.now()
    elapsed_time=datetime.now()-start_log
    cryo_temp_df =pd.DataFrame(data=None)
    out = get_temperature()
    cryo_temp_df=cryo_temp_df.append(pd.DataFrame([out[1:]]))
    while elapsed_time.seconds<duration: 
        out = get_temperature()
        cryo_temp_df=cryo_temp_df.append(pd.DataFrame([out[1:]],columns={"time","temp_cryo"}))
        elapsed_time=datetime.now()-start_log       
    return cryo_temp_df

def lakeshore_initialize():
    try: 
        myinstrument = Model350()
        print("connection successful")
        return(myinstrument)
    except: 
        print("Device not found")
        

def get_temp_data():
    import datetime
    data = {
        'tempA_log': [],
        'tempB_log': [],
        'tempC_log': [],
        
        'tempD_log': [],
        'time':[]
        }
        
    # data['tempA_log'].append(np.float32(myinstrument.query('KRDG? A')))
    time.sleep(0.1)
    data['tempA_log'].append(np.float32(myinstrument.query('KRDG? A')))
    time.sleep(0.1)
    data['tempB_log'].append(np.float32(myinstrument.query('KRDG? B')))
    time.sleep(0.1)
    data['tempC_log'].append(np.float32(myinstrument.query('KRDG? C')))
    time.sleep(0.1)
    data['tempD_log'].append(np.float32(myinstrument.query('KRDG? D')))
    data['time'].append(datetime.datetime.now())
    return data
def log_temp_data_step_duration(step,duration):
    import datetime
    start_time = datetime.datetime.now()
    log_duration = float(duration) #seconds
    log_step = float(step) #seconds 
    df = pd.DataFrame(get_temp_data())
    while datetime.datetime.now()-start_time<datetime.timedelta(seconds=log_duration):
        # print("its true")
        df2 = pd.DataFrame(get_temp_data())
        df = df.append(df2,ignore_index = True)
        sleep(log_step)
    return df
def log_temp_data_step_duration(step,duration):
    import datetime
    start_time = datetime.datetime.now()
    log_duration = float(duration) #seconds
    log_step = float(step) #seconds 
    df = pd.DataFrame(get_temp_data())
    while datetime.datetime.now()-start_time<datetime.timedelta(seconds=log_duration):
        # print("its true")
        df2 = pd.DataFrame(get_temp_data())
        df = df.append(df2,ignore_index = True)
        sleep(log_step)
    return df

def stop_cryocooler(cryo_port='COM7'):
    import datetime
    """Stop the cryocooler"""
    ser0=start_connection(cryo_port)
    set_soft_stop_state(1)
    stop_connection(ser0)
    stoptime=datetime.datetime.now()
    print(f"Cryocooler stopped at {stoptime}")
    
def warmup_detector(temperature=290,heaterrange=5): 
    """Warm up with heater to 290 K"""
    myinstrument=lakeshore_initialize()
    myinstrument.command(f'SETP 1,{temperature}')
    time.sleep(1)
    myinstrument.device_serial.close()
    myinstrument.device_serial.open()
    myinstrument.command(f'RANGE 1,{heaterrange}')
    myinstrument.device_serial.close()
    print(f"CF1 target temperature set to {temperature} K. Heater on CF2 started with range = {heaterrange}")
    
def start_cryocooler_pwmode(cryo_port='COM7', cooldown_power=30): 
    import datetime
    pidmode=0
    soft_stop_state=0
    cooldown_power=30 #W
    """To Start the cryocooler"""
    
    cryo_port='COM7'
    ser0=start_connection(cryo_port)
    set_pid_mode(0)
    set_target_power_output(cooldown_power)
    set_soft_stop_state(0)
    stop_connection(ser0)
    start_time=datetime.datetime.now()
    print(f"Cryocooler started on {start_time}")
    return start_time



        

if __name__ == "__main__":
    """ RUN THIS TO SETUP THE PORT"""
    global cryo_port
    cryo_port='COM7'
        # shroud_temp =input("Input Shroud setpoint:")
    shroud_setpoint=300
    print(f"Setting shroud setpoint to {shroud_setpoint} K")
    myinstrument=lakeshore_initialize()
    myinstrument.command(f'SETP 2,{shroud_setpoint}')
    time.sleep(1)

    print("Setting shroud heater range to Range5")
    myinstrument.device_serial.close()
    myinstrument.device_serial.open()
    myinstrument.command(f'RANGE 4,1')
    myinstrument.device_serial.close()
    time.sleep(1)


