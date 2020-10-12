import pandas as pd
import numpy as np
import os
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

def ver3_create_graphs(data_folder, patient,save_path,events,with_events):

    fig = plt.figure(figsize=(20,10))
    for i,eye in enumerate(['R', 'L'],0):
        ver3_table = pd.read_excel(os.path.join(data_folder, patient, 'Analysis',
                                                '{}_ver3_class_data.xlsx'.format(patient )),sheet_name=eye)  # read excel file
        ver3_table = ver3_table[0:-2]
        time_table = ver3_table[ver3_table['VG_output'] != 0]  # only succesful scans
        class1=time_table['# Class 1']
        class2 = time_table['# Class 2']
        class3 = time_table['# Class 3']
        time_axis = pd.to_datetime(time_table['Date - Time'],format='%Y-%m-%d-%H-%M-%S')
        time_axis=pd.DatetimeIndex(time_axis).date
        ax=fig.add_subplot(2,1,i+1)
        plt.subplots_adjust(hspace = 0.3)
        formatter = mdates.DateFormatter('%m-%d')
        ax.plot(time_axis,class1,color='dodgerblue',marker='o')
        ax.plot(time_axis,class2,color='lightseagreen',marker='o')
        ax.plot(time_axis,class3,color='mediumslateblue',marker='o')
        if eye=='L':
            plt.title('LEFT EYE - Classes 1,2,3',fontsize=16)
        if eye=='R':
            plt.title('RIGHT EYE - Classes 1,2,3',fontsize=16)
        ax.set_xlabel('Date')

        ax.xaxis.set_major_formatter(formatter)
        ax.set_ylabel('# B-scans')
        plt.ylim((0, 100))
        ax.axhline(y=88, xmin=0, xmax=1, color='r', linestyle='--')
        ax.xaxis.set_ticks(time_axis)
        plt.xticks(rotation=45)
        plt.legend(['Class 1', 'Class 2','Class 3'])
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

    plt.savefig(save_path+'/ver3_classes.png')