import pandas as pd
import numpy as np
import os
from os import path
from datetime import date
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

def load_events(data_folder,patient):
    try:
        events=pd.read_excel(os.path.join(data_folder,patient, 'CRF/Injections.xlsx'))
        return events
    except:
        return []

def compliance(data_folder, patient,save_path,events):
    with_events=False
    fig = plt.figure(figsize=(20, 10))
    for e,eye in enumerate(['R', 'L'],0):
        full_table = pd.read_excel(os.path.join(data_folder, patient, 'Analysis',
                                                '{}_DB.xlsx'.format(patient)))  # read excel file
        full_table=full_table[full_table['Eye']==eye]

        ver3_table = pd.read_excel(os.path.join(data_folder, patient, 'Analysis',
                                                '{}_ver3_class_data.xlsx'.format(patient)),sheet_name=eye)  # read excel file
        ver3_table=ver3_table[0:-2]
        dates=pd.to_datetime(full_table['Date - Time'], format='%Y-%m-%d-%H-%M-%S')

        dates=pd.DatetimeIndex(dates).date
        first_date=dates[0]
        total=pd.date_range(start=first_date, end=date.today())
        #total = pd.date_range(start=first_date, end=dates[-1])
        missing = pd.date_range(start=first_date, end=date.today()).difference(dates)
        #missing = pd.date_range(start=first_date, end=dates[-1]).difference(dates)

        comp=[1]*len(total)
        for i in range(len(comp)):
            if total[i] in missing:
                comp[i]=0

        time_axis = pd.DatetimeIndex(total).date
        ax = fig.add_subplot(2, 1, e + 1)
        plt.subplots_adjust(hspace=0.3)
        formatter = mdates.DateFormatter('%m-%d')
        ax.plot(time_axis, comp, color='royalblue',marker='o',zorder=1)


        success_table = full_table[full_table['VG_output'] != 0]  # only succesful scans
        no_vg_output = full_table[full_table['VG_output'] == 0]
        no_88_table=ver3_table[ver3_table['Full Scan(88)']==0]
        timeout_table = ver3_table[ver3_table['TimeOut'] == 1]

        dates = pd.to_datetime(no_vg_output['Date - Time'], format='%Y-%m-%d-%H-%M-%S')
        dates = pd.DatetimeIndex(dates).date
        no_88_dates=pd.to_datetime(no_88_table['Date - Time'], format='%Y-%m-%d-%H-%M-%S')
        no_88_dates = pd.DatetimeIndex(no_88_dates).date
        timeout_dates = pd.to_datetime(timeout_table['Date - Time'], format='%Y-%m-%d-%H-%M-%S')
        timeout_dates = pd.DatetimeIndex(timeout_dates).date

        ax.scatter(dates, [1 for i in range(len(dates))], s=35, c='red', zorder=2, label='No VG output')
        ax.scatter(no_88_dates, [1 for i in range(len(no_88_dates))], s=35, c='orange', zorder=2,
                   label='Less than 88 bscans')
        ax.scatter(timeout_dates, [1 for i in range(len(timeout_dates))], s=35, c='black', zorder=3, label='TimeOut')
        ax.scatter
        if with_events==True:
            installation = pd.to_datetime(events['Installation'], format='%d_%m_%Y')
            injections = pd.to_datetime(events['Injection_{}'.format(eye)], format='%d_%m_%Y')
            visits = pd.to_datetime(events['Visit'], format='%d_%m_%Y')
            rep = pd.to_datetime(events['Device Replaced'], format='%d_%m_%Y')
            events_list = [installation, injections, visits, rep]
            for event in events_list:
                ax.annotate(event.name, xy=(event.T, 0), xytext=(event.T, 0.1),
                            arrowprops=dict(facecolor='black', shrink=0.01))
                ax.annotate('Visit', xy=(pd.to_datetime('02_07_2020',format='%d_%m_%Y'), 0), xytext=(pd.to_datetime('02_07_2020',format='%d_%m_%Y'), 0.1),
                            arrowprops=dict(facecolor='black', shrink=0.01))
        ax.xaxis.set_major_formatter(formatter)
        ax.set_ylabel('Compliance')
        plt.ylim((0, 1.1))
        ax.xaxis.set_ticks(time_axis)
        plt.xticks(fontsize=8)
        plt.xticks(rotation=45)
        if eye=='L':
            plt.title('LEFT EYE - Compliance and Success',fontsize=16)
        if eye=='R':
            plt.title('RIGHT EYE - Compliance and Success',fontsize=16)
        ax.set_xlabel('Date')
        leg=ax.legend()
        # leg=plt.legend(['Compliance', 'TimeOut','No VG output','Less than 88 bscans'],loc=4)
        # leg.legendHandles[0].set_color('royalblue')
        # leg.legendHandles[1].set_color('black')
        # leg.legendHandles[2].set_color('red')
        # leg.legendHandles[3].set_color('orange')

    plt.savefig(save_path + '/Compliance.png')



