import pandas as pd
import numpy as np
import os
from os import path
from datetime import date
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from DB_connection import check_if_downloaded
import scipy.io as sio


def long_shift_DB(patientID,path):
    env = os.environ._data['COMPUTERNAME']
    if 'V-S-G' in env:
        network = 'V-S-G-RNDSTORE'
        host = 'Cloud'
    else:
        network = '172.17.102.175'#'nv-nas01'
        host = 'Local Host'
    columns_new_row=['Patient','Scan','Date - Time','Eye','x_long_shift','y_long_shift']
    total_DB=[]
    for eye in ['R','L']:
        db_path = os.path.join(path,patientID, 'Analysis', 'long_shift_DB.xlsx')
        if os.path.isfile(db_path):
            DB = pd.read_excel(db_path,sheet_name=eye)
        else:
            DB = pd.DataFrame(columns=columns_new_row)
        scans_path=os.path.join(path, patientID,eye ,'Hoct')
        scans_list=os.listdir(scans_path)
        for scan in scans_list:
            if 'TST' in scan:
                scan_path = os.path.join(scans_path,scan)
                data_sum = scan_path + '/DataSummary.txt'  ##get session_id and scan_id
                try:
                    with open(data_sum, 'r') as f:
                        session_ID = f.readline()
                        scan_ID = f.readline()
                except:
                    continue
                isDownloaded=check_if_downloaded(host)
                if int(session_ID[12:-1]) in isDownloaded:
                    new_row = pd.DataFrame(columns=columns_new_row)
                    new_row.loc[0, 'Scan'] = scan_path
                    new_row.loc[0, 'Patient'] = patientID
                    new_row.loc[0, 'Eye'] = eye
                    date_time = scan[10:29]
                    try:
                        if date_time in DB['Date - Time'].array:
                            continue
                    except:
                        pass

                    new_row.loc[0, 'Date - Time'] = date_time

                    VG_Scan_path = scan_path + r'\VolumeGenerator_4\DB_Data\VG_Scan.csv'
                    if not os.path.isfile(VG_Scan_path):
                        continue

                    try:
                        VG_Scan = pd.read_csv(VG_Scan_path)
                        new_row.loc[0, 'x_long_shift'] = VG_Scan['LongiRegShiftX'].values[0]
                        new_row.loc[0, 'y_long_shift'] = VG_Scan['LongiRegShiftY'].values[0]
                    except:
                        print ('Cant get long shift data')
                        continue

                    DB = pd.concat([DB, new_row])
        DB = DB.sort_values(by='Date - Time')
        total_DB.append(DB)
    try:
        writer = pd.ExcelWriter(db_path , engine='xlsxwriter')
        total_DB[1].to_excel(writer, sheet_name='L')
        total_DB[0].to_excel(writer, sheet_name='R')
        writer.save()
    except:
        print ('Cant save DB - open by another user')


    fig = plt.figure(figsize=(20, 10))
    for i, eye in enumerate(['R', 'L'], 0):
        scan_quality_table = pd.read_excel(db_path,sheet_name=eye)
        x_shift = scan_quality_table['x_long_shift']
        y_shift = scan_quality_table['y_long_shift']
        time_axis = pd.to_datetime(scan_quality_table['Date - Time'], format='%Y-%m-%d-%H-%M-%S')
        time_axis = pd.DatetimeIndex(time_axis).date
        ax = fig.add_subplot(2, 1, i + 1)
        plt.subplots_adjust(hspace=0.3)
        ax.plot(time_axis, x_shift, marker='o')
        ax.plot(time_axis, y_shift, marker='o')
        if eye == 'L':
            plt.title('LEFT EYE - Longitudinal shift', fontsize=16)
        if eye == 'R':
            plt.title('RIGHT EYE - Longitudinal shift ', fontsize=16)
        ax.set_xlabel('Date')
        formatter = mdates.DateFormatter('%m-%d')
        ax.xaxis.set_major_formatter(formatter)
        ax.set_ylabel('Shift [um]')
        #plt.ylim((min(min(x_shift),min(y_shift)),max(max(x_shift),max(y_shift))))
        ax.xaxis.set_ticks(time_axis)
        plt.xticks(rotation=45)
        plt.xticks(fontsize=8)
        # Get events
        # if with_events == True:
        #     installation = pd.to_datetime(events['Installation'], format='%d_%m_%Y')
        #     injections = pd.to_datetime(events['Injection_{}'.format(eye)], format='%d_%m_%Y-%H')
        #     visits = pd.to_datetime(events['Visit'], format='%d_%m_%Y')
        #     rep = pd.to_datetime(events['Device Replaced'], format='%d_%m_%Y')
        #     events_list = [installation, injections, visits, rep]
        #     for event in events_list:
        #         # ax.annotate(event.name, xy=(event.T, -530), xytext=(event.T, -460),
        #         #             arrowprops=dict(facecolor='black', shrink=0.01))
        #         ax.annotate(event.name, xy=(event.T, -500), xytext=(event.T, -430),
        #                     arrowprops=dict(facecolor='black', shrink=0.01))
        plt.legend(['x-axis', 'y-axis'])
        plt.grid()
    plt.savefig(os.path.join(path,patientID, 'Analysis','Plots', 'Long_shift.png'))

long_shift_DB('NH02003',r'\\nv-nas01\Home_OCT_Repository\Clinical_studies\Notal-Home_OCT_study-box3.0\Study_at_home\Data')