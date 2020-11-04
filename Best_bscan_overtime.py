import os
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

if __name__ =="__main__":
    data_folder = r'\\nv-nas01\Home_OCT_Repository\Clinical_studies\Notal-Home_OCT_study-box3.0\Study_at_home\Data\NH02003'
    full_table = pd.read_excel(
        os.path.join(r'\\nv-nas01\Home_OCT_Repository\Clinical_studies\Notal-Home_OCT_study-box3.0\Study_at_home\Data\DB\NH02003_DB.xlsx'))  # read excel file
    #full_table = full_table[full_table['VG_output'] == 1]  # only succesful scans

    fig = plt.figure(figsize=(20, 10))
    max_msi=[[],[]]
    for i,eye in enumerate(['R', 'L'],0):
        scans_list = os.listdir(data_folder + '/' +eye + '/Hoct') #check for scans
        for scan in scans_list:
            if 'TST' in scan:
                file_path = data_folder + '/' + eye + '/Hoct/' + scan +'/VolumeGenerator_4\DB_Data/VG_Scan.csv'
                curr_csv = pd.read_csv(file_path)
                max_msi[i].append(curr_csv['MaxBMsiAll'])

        time_table = full_table[full_table['Eye'] == eye]
        time_axis = pd.to_datetime(time_table['Date - Time'], format='%Y-%m-%d-%H-%M-%S')
        time_axis = pd.DatetimeIndex(time_axis).date
        ax = fig.add_subplot(2, 1, i + 1)
        plt.subplots_adjust(hspace=0.5)
        formatter = mdates.DateFormatter('%m-%d')
        ax.plot(time_axis, max_msi[i], marker='o')
        if eye=='L':
            plt.title('LEFT EYE - Max B-scan MSI vs Time',fontsize=16)
        if eye=='R':
            plt.title('RIGHT EYE - Max B-scan MSI vs Time',fontsize=16)
        ax.set_xlabel('Date')
        ax.xaxis.set_major_formatter(formatter)
        ax.set_ylabel('Time [sec]')
        ax.xaxis.set_ticks(time_axis)
        plt.ylim((0, 8))
        plt.xticks(fontsize=8)
        plt.xticks(rotation=45)

    plt.savefig(data_folder + '/Max B-scan MSI vs time.png')
    plt.show()