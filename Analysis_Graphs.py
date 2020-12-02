import pandas as pd
import numpy as np
import os
from os import path
from datetime import date
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
#from Utils import DecreasingMSI

def load_events(events_path):
    try:
        events=pd.read_excel(events_path)
        with_events=True
        return events,with_events
    except:
        with_events = False
        return [],with_events

def analysis_graphs(data_folder, patient,save_path,events,with_events):
    if not os.path.isdir(save_path):
        os.mkdir(save_path)
    full_table = pd.read_excel(os.path.join(data_folder,patient ,'Analysis','{}_DB.xlsx'.format(patient))) #read excel file
    full_table=full_table[full_table['VG_output']==1] #only succesful scans

    #plot adjustment and total time
    fig = plt.figure(figsize=(20,10))
    for i,eye in enumerate(['R', 'L'],0):
        time_table = full_table[full_table['Eye'] == eye]
        if time_table.empty:
            continue
        adjustment_time=time_table['AdjustmentTime']
        total_time=time_table['TotalScanTime']
        raster_time=time_table['RasterTime']
        time_axis = pd.to_datetime(time_table['Date - Time'],format='%Y-%m-%d-%H-%M-%S')
        time_axis=pd.DatetimeIndex(time_axis).date
        ax=fig.add_subplot(2,1,i+1)
        plt.subplots_adjust(hspace = 0.3)
        formatter = mdates.DateFormatter('%m-%d')
        ax.plot(time_axis,adjustment_time,marker='o')
        ax.plot(time_axis,total_time,marker='o')
        ax.plot(time_axis,raster_time,marker='o')
        if eye=='L':
            plt.title('LEFT EYE - Adjustment,Raster,Total time',fontsize=16)
        if eye=='R':
            plt.title('RIGHT EYE - Adjustment,Raster, Total time',fontsize=16)
        ax.set_xlabel('Date')

        ax.xaxis.set_major_formatter(formatter)
        ax.set_ylabel('Time [sec]')
        plt.ylim((0, 100))
        ax.xaxis.set_ticks(time_axis)
        plt.xticks(fontsize=8)
        plt.xticks(rotation=45)
        plt.legend(['Adjustment Time', 'Total Time','Raster Time'])
        # Get events
        if with_events==True:
            installation = pd.to_datetime(events['Installation'],format='%d_%m_%Y')
            injections=pd.to_datetime(events['Injection_{}'.format(eye)],format='%d_%m_%Y-%H')
            visits = pd.to_datetime(events['Visit'], format='%d_%m_%Y')
            rep = pd.to_datetime(events['Device Replaced'], format='%d_%m_%Y')
            events_list = [installation, injections, visits, rep]
            for event in events_list:
                ax.annotate(event.name,xy=(event.T,0),xytext=(event.T,6),arrowprops=dict(facecolor='black', shrink=0.01))
        plt.grid()

    plt.savefig(save_path+'/Adjustment and Total time.png')

    #plot scan quality
    fig = plt.figure(figsize=(20, 10))
    for i, eye in enumerate(['R', 'L'], 0):
        scan_quality_table=full_table[full_table['Eye'] == eye]
        if scan_quality_table.empty:
            continue
        MSI=scan_quality_table['MSI']
        Vmsi=scan_quality_table['Vmsi']
        time_axis = pd.to_datetime(scan_quality_table['Date - Time'], format='%Y-%m-%d-%H-%M-%S')
        time_axis = pd.DatetimeIndex(time_axis).date
        ax=fig.add_subplot(2,1,i+1)
        plt.subplots_adjust(hspace=0.3)
        ax.plot(time_axis, MSI, marker='o')
        ax.plot(time_axis, Vmsi, marker='o')
        if eye == 'L':
            plt.title('LEFT EYE - MSI and Vmsi',fontsize=16)
        if eye == 'R':
            plt.title('RIGHT EYE - MSI and Vmsi',fontsize=16)
        ax.set_xlabel('Date')
        formatter = mdates.DateFormatter('%m-%d')
        ax.xaxis.set_major_formatter(formatter)
        ax.set_ylabel('MSI / Vmsi')
        plt.ylim((0, 10))
        ax.xaxis.set_ticks(time_axis)
        plt.xticks(fontsize=8)
        plt.xticks(rotation=45)
        plt.legend(['MSI','Vmsi'])
        # Get events
        if with_events == True:
            installation = pd.to_datetime(events['Installation'], format='%d_%m_%Y')
            injections = pd.to_datetime(events['Injection_{}'.format(eye)], format='%d_%m_%Y-%H')
            visits = pd.to_datetime(events['Visit'], format='%d_%m_%Y')
            rep = pd.to_datetime(events['Device Replaced'], format='%d_%m_%Y')
            events_list = [installation, injections, visits, rep]
            for event in events_list:
                ax.annotate(event.name, xy=(event.T, 0), xytext=(event.T, 0.5),
                            arrowprops=dict(facecolor='black', shrink=0.005))
        plt.grid()
    plt.savefig(save_path + '/MSI and Vmsi.png')

    # plot max_MSI
    fig = plt.figure(figsize=(20, 10))
    for i, eye in enumerate(['R', 'L'], 0):
        scan_quality_table = full_table[full_table['Eye'] == eye]
        if scan_quality_table.empty:
            continue
        max_bmsi_raw = scan_quality_table['Max_BMSIAllRaw']
        time_axis = pd.to_datetime(scan_quality_table['Date - Time'], format='%Y-%m-%d-%H-%M-%S')
        time_axis = pd.DatetimeIndex(time_axis).date
        ax = fig.add_subplot(2, 1, i + 1)
        plt.subplots_adjust(hspace=0.3)
        ax.plot(time_axis, max_bmsi_raw, marker='o')
        if eye == 'L':
            plt.title('LEFT EYE - Max Raw BMSI', fontsize=16)
        if eye == 'R':
            plt.title('RIGHT EYE - Max Raw BMSI', fontsize=16)
        ax.set_xlabel('Date')
        formatter = mdates.DateFormatter('%m-%d')
        ax.xaxis.set_major_formatter(formatter)
        ax.set_ylabel('MSI')
        plt.ylim((0, max(10,max(max_bmsi_raw))))
        ax.xaxis.set_ticks(time_axis)
        plt.xticks(fontsize=8)
        plt.xticks(rotation=45)

        plt.grid()
    plt.savefig(save_path + '/Max_MSI.png')

    # plot % MSI <2
    fig = plt.figure(figsize=(20, 10))
    for i, eye in enumerate(['R', 'L'], 0):
        scan_quality_table = full_table[full_table['Eye'] == eye]
        if scan_quality_table.empty:
            continue
        msi_less_than2 = scan_quality_table['% MSI<2']
        time_axis = pd.to_datetime(scan_quality_table['Date - Time'], format='%Y-%m-%d-%H-%M-%S')
        time_axis = pd.DatetimeIndex(time_axis).date
        ax = fig.add_subplot(2, 1, i + 1)
        plt.subplots_adjust(hspace=0.3)
        ax.plot(time_axis, msi_less_than2, marker='o')
        if eye == 'L':
            plt.title('LEFT EYE - % of BScans with MSI lower than 2', fontsize=16)
        if eye == 'R':
            plt.title('RIGHT EYE - % of BScans with MSI lower than 2', fontsize=16)
        ax.set_xlabel('Date')
        formatter = mdates.DateFormatter('%m-%d')
        ax.xaxis.set_major_formatter(formatter)
        ax.set_ylabel('% of Bscans')
        plt.ylim((0, 100))
        ax.xaxis.set_ticks(time_axis)
        plt.xticks(fontsize=8)
        plt.xticks(rotation=45)
        #plt.legend(['MSI', 'Vmsi', 'Max Raw BMSI'])
        # Get events

        plt.grid()
    plt.savefig(save_path + '/MSI lower than 2.png')


    #plot NumValid Lines
    fig = plt.figure(figsize=(20, 10))
    for i, eye in enumerate(['R', 'L'], 0):
        scan_quality_table=full_table[full_table['Eye'] == eye]
        if scan_quality_table.empty:
            continue
        NumValidLines=scan_quality_table['NumValidLines']
        above_88=round((sum(NumValidLines>=88))/len(NumValidLines)*100,2)
        time_axis = pd.to_datetime(scan_quality_table['Date - Time'], format='%Y-%m-%d-%H-%M-%S')
        time_axis = pd.DatetimeIndex(time_axis).date
        ax=fig.add_subplot(2,1,i+1)
        plt.subplots_adjust(hspace=0.3)
        ax.plot( time_axis, NumValidLines, marker='o')
        if eye == 'L':
            plt.title('LEFT EYE - #Valid  ({}% Above 88)'.format(above_88),fontsize=16)
        if eye == 'R':
            plt.title('RIGHT EYE - #Valid Lines  ({}% Above 88)'.format(above_88),fontsize=16)
        ax.set_xlabel('Date')
        formatter = mdates.DateFormatter('%m-%d')
        ax.xaxis.set_major_formatter(formatter)
        ax.set_ylabel('#Valid Lines')
        plt.ylim((0,110))
        ax.axhline(y=88, xmin=0, xmax=1,color='r',linestyle='--')
        ax.xaxis.set_ticks(time_axis)
        plt.xticks(fontsize=8)
        plt.xticks(rotation=45)

        # Get events
        if with_events == True:
            installation = pd.to_datetime(events['Installation'], format='%d_%m_%Y')
            injections = pd.to_datetime(events['Injection_{}'.format(eye)], format='%d_%m_%Y-%H')
            visits = pd.to_datetime(events['Visit'], format='%d_%m_%Y')
            rep = pd.to_datetime(events['Device Replaced'], format='%d_%m_%Y')
            events_list = [installation, injections, visits, rep]
            for event in events_list:
                ax.annotate(event.name, xy=(event.T, 0), xytext=(event.T, 8),
                            arrowprops=dict(facecolor='black', shrink=0.01))
        plt.grid()
    plt.savefig(save_path + '/NumValidLines.png')


    #RegSTDX RegSTDY
    fig = plt.figure(figsize=(20, 10))
    for i, eye in enumerate(['R', 'L'], 0):
        scan_quality_table=full_table[full_table['Eye'] == eye]
        if scan_quality_table.empty:
            continue
        RegStdX=scan_quality_table['RegStdX']
        RegStdY = scan_quality_table['RegStdY']
        time_axis = pd.to_datetime(scan_quality_table['Date - Time'], format='%Y-%m-%d-%H-%M-%S')
        time_axis = pd.DatetimeIndex(time_axis).date
        ax=fig.add_subplot(2,1,i+1)
        plt.subplots_adjust(hspace=0.3)
        ax.plot(time_axis, RegStdX, marker='o')
        ax.plot(time_axis, RegStdY, marker='o')
        if eye == 'L':
            plt.title('LEFT EYE - RegStdX & RegStdY',fontsize=16)
        if eye == 'R':
            plt.title('RIGHT EYE - RegStdX & RegStdY ',fontsize=16)
        ax.set_xlabel('Date')
        formatter = mdates.DateFormatter('%m-%d')
        ax.xaxis.set_major_formatter(formatter)
        ax.set_ylabel('RegStdX/RegStdY [um]')
        plt.ylim((0,max(350,max(RegStdY),max(RegStdX))))
        ax.xaxis.set_ticks(time_axis)
        plt.xticks(fontsize=8)
        plt.xticks(rotation=45)
        # Get events
        if with_events == True:
            installation = pd.to_datetime(events['Installation'], format='%d_%m_%Y')
            injections = pd.to_datetime(events['Injection_{}'.format(eye)], format='%d_%m_%Y-%H')
            visits = pd.to_datetime(events['Visit'], format='%d_%m_%Y')
            rep=pd.to_datetime(events['Device Replaced'], format='%d_%m_%Y')
            events_list = [installation, injections, visits,rep]
            for event in events_list:
                ax.annotate(event.name, xy=(event.T, 0), xytext=(event.T, 20),
                            arrowprops=dict(facecolor='black', shrink=0.01))
        plt.legend(['RegStdX','RegStdY'])
        plt.grid()
    plt.savefig(save_path + '/Regx_Regy.png')

    # Clipped
    fig = plt.figure(figsize=(20, 10))
    for i, eye in enumerate(['R', 'L'], 0):
        scan_quality_table = full_table[full_table['Eye'] == eye]
        if scan_quality_table.empty:
            continue
        Clipped_0 = scan_quality_table['# of bscans clipped>0']
        Clipped_5 = scan_quality_table['# of bscans clipped>5']
        time_axis = pd.to_datetime(scan_quality_table['Date - Time'], format='%Y-%m-%d-%H-%M-%S')
        time_axis = pd.DatetimeIndex(time_axis).date
        ax = fig.add_subplot(2, 1, i + 1)
        plt.subplots_adjust(hspace=0.3)
        ax.plot(time_axis, Clipped_0, marker='o')
        ax.plot(time_axis, Clipped_5, marker='o')
        if eye == 'L':
            plt.title('LEFT EYE - # Clipped Bscans', fontsize=16)
        if eye == 'R':
            plt.title('RIGHT EYE - # Clipped Bscans ', fontsize=16)
        ax.set_xlabel('Date')
        formatter = mdates.DateFormatter('%m-%d')
        ax.xaxis.set_major_formatter(formatter)
        ax.set_ylabel('# of Clipped BScans')
        plt.ylim((0, 100))
        ax.xaxis.set_ticks(time_axis)
        plt.xticks(fontsize=8)
        plt.xticks(rotation=45)
        plt.legend(['# Clipped', '# Clipped > 5%'])
        # Get events
        if with_events == True:
            installation = pd.to_datetime(events['Installation'], format='%d_%m_%Y')
            injections = pd.to_datetime(events['Injection_{}'.format(eye)], format='%d_%m_%Y-%H')
            visits = pd.to_datetime(events['Visit'], format='%d_%m_%Y')
            rep = pd.to_datetime(events['Device Replaced'], format='%d_%m_%Y')
            events_list = [installation, injections, visits, rep]
            for event in events_list:
                ax.annotate(event.name, xy=(event.T, 0), xytext=(event.T, 20),
                            arrowprops=dict(facecolor='black', shrink=0.01))
        plt.grid()
    plt.savefig(save_path + '/Clipped.png')

    plt.close('all')







