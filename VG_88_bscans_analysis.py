import pandas as pd
import numpy as np
import os
import matplotlib.pyplot as plt
from Utils import merge_eye_excels

def class_ditrib1(data_folder,patient):
    patientID=patient.patient_ID
    vg_88_path=patient.analysis_folder
    save_fig_path=(vg_88_path+'/Plots')
    fig, (ax1, ax2) = plt.subplots(1, 2,figsize=(12, 7))
    for eye in ['R','L']:
        class_table = pd.read_excel(os.path.join(data_folder, patientID, 'Analysis',
                                                '{}_ver3_class_data.xlsx'.format(patientID)),sheet_name=eye)  # read excel file
        save_excel_path = (vg_88_path + '/{}_{}_ver3_class_analysis.xlsx'.format(patientID, eye))
        class_table=class_table[:-2]
        class_table=class_table[class_table['Full Scan(88)']>0]
        class1 = class_table['# Class 1'].array
        class1=[val for val in class1 if val > 0]
        class_1_num = len(class1)
        mean_class1=np.mean(class1)
        STD_class1=np.std(class1)


        class2=class_table['# Class 2'].array
        class2 = [val for val in class2 if val > 0]
        class_2_num = len(class2)
        mean_class2 = np.mean(class2)
        STD_class2 = np.std(class2)

        class3 = class_table['# Class 3'].array
        class3 = [val for val in class3 if val > 0]
        class_3_num = len(class3)
        mean_class3 = np.mean(class3)
        STD_class3 = np.std(class3)

        class1_only=0
        class1_2=0
        class1_2_3=0
        class1_3=0
        for ind,row in class_table.iterrows():
            if row['# Class 1']>0 and row['# Class 2']<=0 and row['# Class 3']<=0:
                class1_only+=1
            if row['# Class 1']>0 and row['# Class 2']>0 and row['# Class 3']<=0:
                class1_2+=1
            if row['# Class 1']>0 and row['# Class 2']>0 and row['# Class 3']>0:
                class1_2_3+=1
            if row['# Class 1']>0 and row['# Class 2']<=0 and row['# Class 3']>0:
                class1_3+=1




        output=pd.DataFrame(columns=['Class 1','Class 2','Class 3','Class 1 only','Class 1&2','Class 1&3','Class 1&2&3','Total'])
        output.loc['# scans']=class_1_num,class_2_num,class_3_num,class1_only,class1_2,class1_3,class1_2_3,sum(class_table['VG_output'])
        output.loc['Mean'] = mean_class1.round(2), mean_class2.round(2), mean_class3.round(2),'','','','',''
        output.loc['STD'] = STD_class1.round(2), STD_class2.round(2), STD_class3.round(2),'','','','',''
        cmap = plt.get_cmap('Spectral')
        colors = [cmap(i) for i in np.linspace(0, 1, 10)]


        to_plot=[class1_only,class1_2,class1_3,class1_2_3]
        labels=['Class 1 only','Class 1&2','Class 1&3','Class 1&2&3']

        def func(pct, to_plot):
            absolute = int(np.round(pct / 100. * np.sum(to_plot)))
            return "{:.1f}%, ({:d})".format(pct, absolute)

        for val,label in zip(to_plot,labels):
            if val==0:
                to_plot.remove(val)
                labels.remove(label)

        if eye=='R':
            ax1.pie(to_plot, labels=labels,colors=colors, autopct=lambda pct: func(pct, to_plot))
            ax1.set_title('Per Scan Class Distribution, Patient {}, {}'.format(patientID, eye))
        if eye=='L':
            ax2.pie(to_plot, labels=labels,colors=colors, autopct=lambda pct: func(pct, to_plot))
            plt.title('Per Scan Class Distribution, Patient {}, {}'.format(patientID, eye))


        output.to_excel(save_excel_path)
    plt.savefig(save_fig_path+'/Per_Scan Class Distribution.png')
    merge_eye_excels(patient, '/{}_{}_ver3_class_analysis.xlsx', '{}_ver3_class_analysis.xlsx'.format(patientID))
    return



def class_distrib2(data_folder,patient):
    patientID = patient.patient_ID
    vg_88_path = patient.analysis_folder
    save_fig_path = (vg_88_path + '/Plots')
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 7))
    for eye in ['R', 'L']:
        class_table = pd.read_excel(os.path.join(data_folder, patientID, 'Analysis',
                                             '{}_ver3_class_data.xlsx'.format(patientID)),
                                sheet_name=eye)  # read excel file
        class_table = class_table[:-2]
        class_table = class_table[class_table['Full Scan(88)'] > 0]
        class1 = class_table['# Class 1'].array
        class1 = [val for val in class1 if val > 0]
        class_1_sum = sum(class1)

        class2 = class_table['# Class 2'].array
        class2 = [val for val in class2 if val > 0]
        class_2_sum = sum(class2)

        class3 = class_table['# Class 3'].array
        class3 = [val for val in class3 if val > 0]
        class_3_sum = sum(class3)




        cmap = plt.get_cmap('Spectral')
        colors = [cmap(i) for i in np.linspace(0, 1, 10)]

        to_plot = [class_1_sum,class_2_sum,class_3_sum]
        labels = ['Class 1', 'Class 2', 'Class 3']

        def func(pct, to_plot):
            absolute = int(pct / 100. * np.sum(to_plot))
            return "{:.1f}%, ({:d})".format(pct, absolute)

        for val, label in zip(to_plot, labels):
            if val == 0:
                to_plot.remove(val)
                labels.remove(label)

        if eye == 'R':
            ax1.pie(to_plot, labels=labels, colors=colors, autopct=lambda pct: func(pct, to_plot))
            ax1.set_title('All Bscans Class Distribution, Patient {}, {}'.format(patientID, eye))
        if eye == 'L':
            ax2.pie(to_plot, labels=labels, colors=colors, autopct=lambda pct: func(pct, to_plot))
            plt.title('All Bscans Class Distribution, Patient {}, {}'.format(patientID, eye))

    plt.savefig(save_fig_path + '/All Bscans Class Distribution.png')
    return
