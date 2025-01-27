#importing packages 
#ipython packages 
from IPython.display import clear_output

#number handling
import pandas as pd
import numpy as np

#encoding decodning
import signal
import codecs
from tqdm.auto import tqdm
#file handling and OS
import os
import sys
import glob

#serial connection 
import serial
from serial import SerialException
import serial.tools.list_ports

# time and datetime package
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
#from cryocooler_api import *
import sys, signal
from cryocooler_avc_api import *
global verbose 
verbose=0

def signal_handler(signal, frame):
    print("\nprogram exiting gracefully")
    sys.exit(0)


def lakeshore_initialize():
    try: 
        myinstrument =Model350()
        print("Lakeshore controller initalized")
        return(myinstrument)
    except: 
        print("Lakeshore controller not found")
        

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
    start_time=datetime.datetime.now()
    log_duration = float(duration) #seconds
    log_step=float(step) #seconds 
    df = pd.DataFrame(get_temp_data())
    while datetime.datetime.now()-start_time<datetime.timedelta(seconds=log_duration):
        # print("its true")
        df2=pd.DataFrame(get_temp_data())
        df=df.append(df2,ignore_index = True)
        sleep(log_step)
    return df

def run_server(): 

    global myinstrument,cryo_port,detector,ser0
    cryo_port='COM7'
    detector='w18d10'
    myinstrument=lakeshore_initialize()
    myinstrument.device_serial.close()
    # cooling =True
    today=datetime.datetime.now()
    #Raise flag if the logging is being restarted and the data in the exisiting dataframe must not be re written
    Restart=0
    Sensor_map={'LSA':'LS Input A: EMCCD Detector',
                'LSB':'LS Input B: Cold Finger 1',
                'LSC':'LS Input C: Cold Finger 2',
                'LSD':'LS Input D: Thermal Shroud',
                'Cryo':'Cryo Cold Tip',
                'Reject':'Reject Temperature'
                }

    Color_map={'LSA':px.colors.qualitative.Safe[0], 
                'LSB':px.colors.qualitative.Safe[1],
                'LSC':px.colors.qualitative.Safe[2],
                'LSD':px.colors.qualitative.Safe[3],
                'Cryo':px.colors.qualitative.Safe[4],
                'Reject':px.colors.qualitative.Safe[5],
                }

    if Restart==0: #if the logging is not being restarted .
        #Get Lakeshore temperature data for the first time
        filename_base=today.strftime("%m_%d_%Y")
        myinstrument.device_serial.open()
        df_read_lakeshore=pd.DataFrame(get_temp_data())
        myinstrument.device_serial.close()    
        #Get cryo temperature data for the first time
        ser0=start_connection(cryo_port)
        df_cryo = cryo_temp_single_read(ser0)
        df_reject=reject_temp_single_read(ser0)
        stop_connection(ser0)

    start_time=datetime.datetime.now()
    cryo_path=f"D:\OneDrive - University of Arizona\optical sciences\Research\Erika Hamden Group\Code\Cryocooler_Control_software\Final_code\temperature_log\Cryocooler_Templog_{filename_base}.csv"
    reject_path=f"D:\OneDrive - University of Arizona\optical sciences\Research\Erika Hamden Group\Code\Cryocooler_Control_software\Final_code\temperature_log\Reject_Templog_{filename_base}.csv"
    lakeshore_path=f"D:\OneDrive - University of Arizona\optical sciences\Research\Erika Hamden Group\Code\Cryocooler_Control_software\Final_code\temperature_log\Lakeshore_Templog_{filename_base}.csv"
    webpath =f"D:\OneDrive - University of Arizona\optical sciences\Research\Erika Hamden Group\Code\Cryocooler_Control_software\Final_code\temperature_log\Exp_Templog_{filename_base}.html"
    # Use this function to search for any files which match your filename
    files_present = len(glob.glob(cryo_path))*len(glob.glob(lakeshore_path))*len(glob.glob(reject_path))
    
    # if no matching files, write to csv, if there are matching files, print statement
    if files_present:
        df_cryo=pd.read_csv(cryo_path)
        df_read_lakeshore=pd.read_csv(lakeshore_path)
        df_reject=pd.read_csv(reject_path)

    log_duration = 24*100*60 #seconds
    log_step=120#seconds 
    time_check_state=start_time

    while datetime.datetime.now()-start_time<timedelta(seconds=log_duration):
        # print("its true")
        timer_save_data=datetime.datetime.now()
        timer_plot_data=timer_save_data
        
        while datetime.datetime.now()-timer_save_data<timedelta(seconds=log_step):
                
            myinstrument=lakeshore_initialize()
            dftemp=pd.DataFrame(get_temp_data())
            myinstrument.device_serial.close() 
            
            ser0=start_connection(cryo_port)
            dftemp_cryo=cryo_temp_single_read(ser0)
            dftemp_reject=reject_temp_single_read(ser0)
            stop_connection(ser0)

            df_read_lakeshore=df_read_lakeshore.append(dftemp,ignore_index = True)
            df_cryo=df_cryo.append(dftemp_cryo,ignore_index = True)
            df_reject=df_reject.append(dftemp_reject,ignore_index=True)
            #display(df[-5:])
            df_cryo.to_csv(cryo_path)
            df_read_lakeshore.to_csv(lakeshore_path)
            df_reject.to_csv(reject_path)
            print(f"{Sensor_map['LSA']} @ {dftemp.tempA_log.values[-1]:.2f} K")
            print(f"{Sensor_map['LSB']} @ {dftemp.tempB_log.values[-1]:.2f} K")
            print(f"{Sensor_map['LSC']} @ {dftemp.tempC_log.values[-1]:.2f} K")
            print(f"{Sensor_map['LSD']} @ {dftemp.tempD_log.values[-1]:.2f} K")
            print(f"{Sensor_map['Cryo']} @ {dftemp_cryo.cryo_temp.values[-1]:.2f} K")
            print(f"{Sensor_map['Reject']} @ {273.00+dftemp_reject.reject_temp.values[-1]:.2f} K")
            
            desc=f'Reading Temperature in:'
            for i in tqdm(range(log_step),desc=desc):
                sleep(1)
            #clear_output(wait=True)    
        
        if datetime.datetime.now()-timer_plot_data>timedelta(seconds=log_step):
            clear_output(wait=True)
            df_read_cryo=pd.read_csv(cryo_path)
            df_read_lakeshore=pd.read_csv(lakeshore_path)
            df_reject=pd.read_csv(reject_path)
            # df=df.append(df_read_lakeshore,ignore_index=True)

        fig = plotly.subplots.make_subplots(rows=1, cols=1, vertical_spacing=0.1)
        fig['layout']['margin'] = {'l': 40, 'r': 20, 'b': 40, 't': 100}
        # fig['layout']['legend'] = {'x': 0, 'y': -0.25, 'xanchor': 'left','orientation':"h"}

        fig.append_trace({
            'x': df_read_lakeshore.time,
            'y': df_read_lakeshore.tempA_log,
            'name': f"{Sensor_map['LSA']} @ {np.round(df_read_lakeshore.tempA_log.values[-1],3)} K",
            'type': 'scatter',
            'legendgroup' : 1, 
            'line':dict(color=Color_map['LSA']),
            'hovertemplate':
                f"<b>{Sensor_map['LSA']}</b><br><br>" +
                "Temperature: %{y} K<br>" +
                "Time: %{x}<br>" +
                "<extra></extra>",
        }, 1, 1)

        fig.append_trace({
            'x': df_read_lakeshore.time,
            'y': df_read_lakeshore.tempB_log,
            'name': f"{Sensor_map['LSB']} @ {np.round(df_read_lakeshore.tempB_log.values[-1],3)} K",
            'type': 'scatter',
            'line':dict(color=Color_map['LSB']),  
            'legendgroup' : 1,
            'hovertemplate':
                f"<b>{Sensor_map['LSB']}</b><br><br>" +
                "Temperature: %{y} K<br>" +
                "Time: %{x}<br>" +
                "<extra></extra>",    

        }, 1, 1)

        fig.append_trace({
            'x': df_read_lakeshore.time,
            'y': df_read_lakeshore.tempC_log,
            'name': f"{Sensor_map['LSC']} @ {np.round(df_read_lakeshore.tempC_log.values[-1],3)} K",
            'type': 'scatter',
            'legendgroup' : 2,
            'line':dict(color=Color_map['LSC']),
            'hovertemplate':
                f"<b>{Sensor_map['LSC']}</b><br><br>" +
                "Temperature: %{y} K<br>" +
                "Time: %{x}<br>" +
                "<extra></extra>",  
        }, 1, 1)

        fig.append_trace({
            'x': df_read_lakeshore.time,
            'y': df_read_lakeshore.tempD_log,
            'name': f"{Sensor_map['LSD']} @ {np.round(df_read_lakeshore.tempD_log.values[-1],3)} K",
            'type': 'scatter',
            'legendgroup' : 2,
            'line':dict(color=Color_map['LSD']),
            'hovertemplate':
                f"<b>{Sensor_map['LSD']}</b><br><br>" +
                "Temperature: %{y} K<br>" +
                "Time: %{x}<br>" +
                "<extra></extra>",
        }, 1, 1)

        fig.append_trace({
            'x': df_read_cryo.time,
            'y': df_read_cryo.cryo_temp,
            'name': f"{Sensor_map['Cryo']} @ {np.round(df_read_cryo.cryo_temp.values[-1],3)} K",
            'type': 'scatter',
            'legendgroup' : 3,
            'line':dict(color=Color_map['Cryo']),
            'hovertemplate':
                f"<b>{Sensor_map['Cryo']}</b><br><br>" +
                "Temperature: %{y} K<br>" +
                "Time: %{x}<br>" +
                "<extra></extra>",
        }, 1, 1)
        
        fig.append_trace({
            'x': df_reject.time,
            'y': df_reject.reject_temp+273.,
            'name': f"{Sensor_map['Reject']} @ {np.round(df_reject.reject_temp.values[-1],3)+273.00} K",
            'type': 'scatter',
            'legendgroup' : 3,
            'line':dict(color=Color_map['Reject']),
            'hovertemplate':
                f"<b>{Sensor_map['Reject']}</b><br><br>" +
                "Temperature: %{y} K<br>" +
                "Time: %{x}<br>" +
                "<extra></extra>",
        }, 1, 1)
        fig.update_layout(width=1000,height=800)
        xmin=100
        xmax=320
        fig.update_yaxes(range=[xmin,xmax],row=1,col=1)

        t0=datetime.datetime.strptime(df_read_lakeshore.time[0],"%Y-%m-%d %H:%M:%S.%f")
        tstring=t0.strftime("%m/%d/%Y, %H:%M:%S")
        tnow=datetime.datetime.now()
        tnowstr=tnow.strftime("%m/%d/%Y, %H:%M:%S")
        # tnow=time.now()
        fig.update_layout(
            title={
                'text':f"Detector Cooling Log: {detector}, Date:{tstring} \n Last Update: {tnowstr} ",
                'y':0.95,
                'x':0.5,
                'xanchor': 'center',
                'yanchor': 'top'},
            
            yaxis_title = 'Temperature (K)',
            xaxis_title='Time (MST)'

            )

        fig.layout.template='simple_white'
        fig.update_xaxes(showgrid=True,mirror=True)
        fig.update_yaxes(showgrid=True,mirror=True)
        fig.update_layout(legend=dict(  
                                        #title=r"Sensor lables (Click to toggle visiblity)<br>",
                                        groupclick="toggleitem",
                                        orientation="h",
                                        yanchor="top",
                                        y=-0.5,
                                        xanchor="left",
                                        x=0.0
                                    )
                        )
        fig.update_xaxes(ticks="outside", tickwidth=1.5, tickcolor='grey', ticklen=10)
        fig.update_yaxes(ticks="outside", tickwidth=1.5, tickcolor='grey', ticklen=10)
        fig.update_layout(
            xaxis=dict(
                rangeselector=dict(
                    buttons=list([
                        dict(count=15,
                            label="15 mins",
                            step="minute",
                            stepmode="backward"),
                        dict(count=1,
                            label="1 hour",
                            step="hour",
                            stepmode="backward"),
                        dict(count=5,
                            label="5 hours",
                            step="hour",
                            stepmode="backward"),
                        dict(count=10,
                            label="10 hours",
                            step="hour",
                            stepmode="backward"),
                        dict(step="all")
                    ])
                ),
                rangeslider=dict(
                    visible=True
                ),
                type="date"
            )
        )
        fig.update_xaxes(rangeslider_bordercolor='grey',rangeslider_borderwidth=1)
        fig.update_xaxes(showspikes=True,spikethickness=1)
        fig.update_yaxes(showspikes=True,spikethickness=1)
        fig.update_layout(
            yaxis = dict(
                tickmode = 'linear',
                dtick = 25
            ))
        #fig.show()
        tsave=t0.strftime("%m%d%Y")
        path=r'D:\OneDrive - University of Arizona\optical sciences\Research\Erika Hamden Group\Code\Cryocooler_Control_software\Final_code\temperature_log'
        html_path=os.path.join(path,f"Detector_cooling_{detector}_{tsave}.html")
        runtime_html_path=os.path.join(path,f"runtime.html")
        #print(f"The realtime udpates will be saved in {runtime_html_path}")
        png_path=os.path.join(path,f"Detector_cooling_{detector}_{tsave}.png")
        fig.write_html(html_path)
        fig.write_html(runtime_html_path)
        fig.write_image(png_path)
        
def main():
    
    try: 
        run_server()
    except KeyboardInterrupt:
        print("Tempertaure log server stopped.")
        

if __name__ == "__main__":

    main()