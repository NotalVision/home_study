# This script generates an analysis of the data of all the patients in the study
import pandas as pd
import os
import matplotlib.pyplot as plt
import numpy as np

def Bscan_Class_Distributio_per_Eye_analysis(data_folder,save_path,patients):
    data=[]
    labels=[]
    for patient in patients:
        DB=pd.read_excel(os.path.join(data_folder,'DB',patient+'_DB.xlsx'))
        for eye in ['R','L']:
            eye_DB=DB[DB['Eye']==eye]
            class1=eye_DB['# Class 1']
            class2 = eye_DB['# Class 2']
            class3 = eye_DB['# Class 3']
            sum_class1=sum(class1[class1!=-1])
            sum_class2 = sum(class2[class2 != -1])
            sum_class3 = sum(class3[class3 != -1])
            data.append([sum_class1,sum_class2,sum_class3])
            labels.append('{}_{}'.format(patient, eye))

    idx = np.asarray([i for i in range(len(data))])

    fig,ax = plt.subplots(figsize = (10,4))
    for i in range(len(data)):
        ax.bar(i + 0.00, data[i][0], color='cornflowerblue', width=0.25)
        ax.bar(i + 0.25, data[i][1], color='m', width=0.25)
        ax.bar(i + 0.50, data[i][2], color='mediumseagreen', width=0.25)
    ax.set_xticks(idx)
    ax.set_xticklabels(labels, rotation=65)
    ax.set_xlabel('Patient')
    ax.set_ylabel('# of Bscans')
    ax.legend(labels=['Class 1', 'Class 2', 'Class 3'])
    plt.title('Bscan Class Distribution per Eye')
    fig.tight_layout()
    plt.savefig(save_path + '/Bscan Distribution per Eye analysis.png')
    plt.show()

def Scan_Class_Distribution_per_Eye_analysis(data_folder,save_path,patients):
    data=[]
    labels=[]
    for patient in patients:
        DB=pd.read_excel(os.path.join(data_folder,'DB',patient+'_DB.xlsx'))
        for eye in ['R','L']:
            eye_DB=DB[DB['Eye']==eye]
            class1_only = 0
            class1_2 = 0
            class1_2_3 = 0
            class1_3 = 0
            for ind, row in eye_DB.iterrows():
                if row['# Class 1'] > 0 and row['# Class 2'] <= 0 and row['# Class 3'] <= 0:
                    class1_only += 1
                if row['# Class 1'] > 0 and row['# Class 2'] > 0 and row['# Class 3'] <= 0:
                    class1_2 += 1
                if row['# Class 1'] > 0 and row['# Class 2'] > 0 and row['# Class 3'] > 0:
                    class1_2_3 += 1
                if row['# Class 1'] > 0 and row['# Class 2'] <= 0 and row['# Class 3'] > 0:
                    class1_3 += 1
            data.append([class1_only,class1_2,class1_3,class1_2_3,])
            labels.append('{}_{}'.format(patient, eye))

    idx = np.asarray([i for i in range(len(data))])

    fig,ax = plt.subplots(figsize = (10,4))
    for i in range(len(data)):
        ax.bar(i + 0.00, data[i][0], color='cornflowerblue', width=0.2)
        ax.bar(i + 0.2, data[i][1], color='mediumorchid', width=0.2)
        ax.bar(i + 0.4, data[i][2], color='sandybrown', width=0.2)
        ax.bar(i + 0.6, data[i][3], color='mediumaquamarine', width=0.2)
    ax.set_xticks(idx)
    ax.set_xticklabels(labels, rotation=65)
    ax.set_xlabel('Patient')
    ax.set_ylabel('# of Scans')
    ax.legend(labels=['Class 1', 'Class 1&2','Class 1&3','Class 1&2&3'])
    plt.title('Scan Class Distribution per Eye')
    fig.tight_layout()
    plt.savefig(save_path + '/Scan Class Distribution per Eye analysis.png')
    plt.show()

def compliance_analysis(data_folder,save_path,patients):
    data = []
    labels = []
    for patient in patients:
        DB=pd.read_excel(os.path.join(data_folder,'DB',patient+'_DB.xlsx'))
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
            total = pd.date_range(start=first_date, end=dates[-1])
            missing = pd.date_range(start=first_date, end=dates[-1]).difference(dates)
            comp=100-len(missing)/len(total)*100

            no_vg_output = full_table[full_table['VG_output'] !=1]
            no_vg_output = no_vg_output[no_vg_output['TimeOut'] == 0]
            no_88_table = ver3_table[ver3_table['Full Scan(88)'] == 0]
            timeout_table = ver3_table[ver3_table['TimeOut'] == 1]
            timeout_table = timeout_table[timeout_table['VG_output'] == 1]
            vg_and_to = full_table[full_table['VG_output'] != 1]
            vg_and_to=vg_and_to[vg_and_to['TimeOut'] == 1]


            dates = pd.to_datetime(no_vg_output['Date - Time'], format='%Y-%m-%d-%H-%M-%S')
            dates = set(pd.DatetimeIndex(dates).date)
            no_vg_output = len(dates) / len(total) * 100
            no_88_dates = pd.to_datetime(no_88_table['Date - Time'], format='%Y-%m-%d-%H-%M-%S')
            no_88_dates = set(pd.DatetimeIndex(no_88_dates).date)
            no_88 = len(no_88_dates) / len(total) * 100
            timeout_dates = pd.to_datetime(timeout_table['Date - Time'], format='%Y-%m-%d-%H-%M-%S')
            timeout_dates = set(pd.DatetimeIndex(timeout_dates).date)
            timeout = len(timeout_dates) / len(total) * 100
            vg_and_to_dates = pd.to_datetime(vg_and_to['Date - Time'], format='%Y-%m-%d-%H-%M-%S')
            vg_and_to = set(pd.DatetimeIndex(vg_and_to_dates).date)
            vg_and_to = len(vg_and_to) / len(total) * 100



            data.append([comp,no_88,vg_and_to,no_vg_output,timeout] )
            labels.append('{}_{}'.format(patient, eye))

    idx = np.asarray([i for i in range(len(data))])
    fig, ax = plt.subplots(figsize=(10, 4))
    for i in range(len(data)):
        ax.bar(i + 0.00, data[i][0], color='cornflowerblue', width=0.15)
        ax.bar(i + 0.15, data[i][1], color='sandybrown', width=0.15)
        ax.bar(i + 0.3, data[i][2], color='mediumorchid', width=0.15)
        ax.bar(i + 0.45, data[i][3], color='mediumaquamarine', width=0.15)
        ax.bar(i + 0.6, data[i][4], color='coral', width=0.15)
    ax.set_xticks(idx)
    ax.set_xticklabels(labels, rotation=65)
    ax.set_xlabel('Patient')
    ax.set_ylabel('% of All Scans')
    ax.legend(labels=['Compliance','Less than 88 Bscans','No VG + TimeOut','No VG Output',  'TimeOut'],bbox_to_anchor=(1.05, 1))
    plt.title('Compliance per Eye')
    fig.tight_layout()
    plt.savefig(save_path + '/Compliance.png')
    plt.show()

if __name__ =="__main__":
    network = '172.17.102.175'  # 'nv -nas01'
    data_folder = r'\\{}\Home_OCT_Repository\Clinical_studies\Notal-Home_OCT_study-box3.0\Study_at_home\Data'.format(network)
    save_path=os.path.join(data_folder,'Analysis')
    patients = ['NH01001','NH01002', 'NH01005', 'NH01006', 'NH02001', 'NH02002', 'NH02003']
    compliance_analysis(data_folder,save_path,patients)
    Bscan_Class_Distributio_per_Eye_analysis(data_folder,save_path,patients)
    Scan_Class_Distribution_per_Eye_analysis(data_folder,save_path,patients)