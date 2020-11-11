# This script generates an analysis of the data of all the patients in the study
import pandas as pd
import os
import matplotlib.pyplot as plt
import numpy as np

def Bscan_Class_Distributio_per_Eye_analysis(data_folder,save_path,patients):
    data=[]
    labels=[]
    total=[]
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
            total.append(sum_class1+sum_class2+sum_class3)
            data.append([sum_class1/total[-1]*100,sum_class2/total[-1]*100,sum_class3/total[-1]*100])
            labels.append('{}_{}'.format(patient, eye))

    mean_class_1=0
    for i in range(len(data)):
        mean_class_1+=data[i][0]
    mean_class_1=mean_class_1/len(data)
    mean_class_2 = 0
    for i in range(len(data)):
        mean_class_2+=data[i][1]
    mean_class_2=mean_class_2/len(data)
    mean_class_3 = 0
    for i in range(len(data)):
        mean_class_3+=data[i][2]
    mean_class_3=mean_class_3/len(data)
    data.append([mean_class_1,mean_class_2,mean_class_3])
    labels.append('Mean (over eyes)')
    total.append(sum(total))
    idx = np.asarray([i for i in range(len(data))])

    fig,ax = plt.subplots(figsize = (20,10))
    for i in range(len(data)):
        ax.bar(i + 0.00, data[i][0], color='cornflowerblue', width=0.25)
        ax.bar(i + 0.25, data[i][1], color='m', width=0.25)
        ax.bar(i + 0.50, data[i][2], color='mediumseagreen', width=0.25)
        ax.annotate('N={}'.format(total[i]),(i,data[i][0]+3))
        for j in range(3):
            if data[i][j]>0.5:
                ax.annotate(F'{data[i][j]/100:.0%}', (i+(0.25*j)-0.1, data[i][j]))
            elif data[i][j]!=0:
                ax.annotate(F'{data[i][j]/100:.1%}', (i+(0.25*j)-0.1, data[i][j]))

    ax.set_xticks(idx)
    ax.set_xticklabels(labels, rotation=65)
    ax.set_xlabel('Patient')
    ax.set_ylabel('% of Total Bscans')
    ax.legend(labels=['Class 1', 'Class 2', 'Class 3'])
    plt.title('Bscan Class Distribution per Eye')
    fig.tight_layout()
    plt.savefig(save_path + '/Bscan Distribution per Eye analysis.png')
    #plt.show()

def Scan_Class_Distribution_per_Eye_analysis(data_folder,save_path,patients):
    data=[]
    labels=[]
    total = []
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
            total.append(class1_only+class1_2+class1_2_3+class1_3)
            data.append([class1_only/ total[-1] * 100,class1_2/ total[-1] * 100,class1_3/ total[-1] * 100,class1_2_3/ total[-1] * 100])
            labels.append('{}_{}'.format(patient, eye))

    mean_class_1 = 0
    for i in range(len(data)):
        mean_class_1 += data[i][0]
    mean_class_1 = mean_class_1 / len(data)
    mean_class_1_2 = 0
    for i in range(len(data)):
        mean_class_1_2 += data[i][1]
    mean_class_1_2 = mean_class_1_2 / len(data)
    mean_class_1_3 = 0
    for i in range(len(data)):
        mean_class_1_3 += data[i][2]
    mean_class_1_3 = mean_class_1_3 / len(data)
    mean_class_1_2_3 = 0
    for i in range(len(data)):
        mean_class_1_2_3 += data[i][3]
    mean_class_1_2_3 = mean_class_1_2_3 / len(data)
    data.append([mean_class_1, mean_class_1_2, mean_class_1_3,mean_class_1_2_3])
    labels.append('Mean (over eyes)')
    total.append(sum(total))

    idx = np.asarray([i for i in range(len(data))])

    fig,ax = plt.subplots(figsize = (20,10))
    for i in range(len(data)):
        ax.bar(i + 0.00, data[i][0], color='cornflowerblue', width=0.2)
        ax.bar(i + 0.2, data[i][1], color='mediumorchid', width=0.2)
        ax.bar(i + 0.4, data[i][2], color='sandybrown', width=0.2)
        ax.bar(i + 0.6, data[i][3], color='mediumaquamarine', width=0.2)
        ax.annotate('N={}'.format(total[i]), (i, max(data[i])+ 3))
        for j in range(4):
            if data[i][j] != 0:
                ax.annotate(F'{data[i][j] / 100:.0%}', (i + (0.2 * j) - 0.1, data[i][j]))
    ax.set_xticks(idx)
    ax.set_xticklabels(labels, rotation=65)
    ax.set_xlabel('Patient')
    ax.set_ylabel('# of Scans')
    ax.legend(labels=['Class 1', 'Class 1&2','Class 1&3','Class 1&2&3'])
    plt.title('Scan Class Distribution per Eye')
    fig.tight_layout()
    plt.savefig(save_path + '/Scan Class Distribution per Eye analysis.png')
    #plt.show()

def compliance_analysis(data_folder,save_path,patients):
    data = []
    data_count=[]
    labels = []
    fig = plt.figure(figsize=(20, 10))
    for patient in patients:
        for e,eye in enumerate(['R', 'L'],0):
            full_table = pd.read_excel(os.path.join(data_folder, patient, 'Analysis',
                                                    '{}_DB.xlsx'.format(patient)))  # read excel file
            full_table=full_table[full_table['Eye']==eye]

            dates=pd.to_datetime(full_table['Date - Time'], format='%Y-%m-%d-%H-%M-%S')
            dates=pd.DatetimeIndex(dates).date
            first_date=dates[0]
            total = pd.date_range(start=first_date, end=dates[-1])
            missing = pd.date_range(start=first_date, end=dates[-1]).difference(dates)
            comp=100-len(missing)/len(total)*100


            less_than_88=full_table[full_table['Full Scan(88)']==0]
            less_than_88_dates = pd.to_datetime(less_than_88['Date - Time'], format='%Y-%m-%d-%H-%M-%S')
            less_than_88_count=len(pd.DatetimeIndex(less_than_88_dates).date)
            less_than_88_dates = set(pd.DatetimeIndex(less_than_88_dates).date)
            less_than_88_dates = len(less_than_88_dates) / len(total) * 100
            more_than_88=full_table[full_table['Full Scan(88)']!=0]
            failure = more_than_88[(more_than_88['VG_output'] ==0) | (more_than_88['TimeOut'] == 1)]
            failure_dates = pd.to_datetime(failure['Date - Time'], format='%Y-%m-%d-%H-%M-%S')
            failure_count=len(pd.DatetimeIndex(failure_dates).date)
            failure_dates = set(pd.DatetimeIndex(failure_dates).date)
            failure_dates = len(failure_dates) / len(total) * 100
            data.append([comp, less_than_88_dates,failure_dates,len(total)])
            data_count.append([len(full_table),less_than_88_count,failure_count])
            labels.append('{}_{}'.format(patient, eye))

    idx = np.asarray([i for i in range(len(data))])
    ax=fig.add_subplot(2,1,1)
    for i in range(len(data)):
        ax.bar(i + 0.00, data[i][0], color='cornflowerblue', width=0.15)
    ax.set_xticks(idx)
    ax.set_xticklabels(labels, rotation=65)
    ax.set_xlabel('Patient')
    ax.set_ylabel('% of All Scans')
    plt.title('Compliance per Eye',fontsize=18)

    ax = fig.add_subplot(2, 1, 2)
    for i in range(len(data_count)):
        total=data_count[i][0]-data_count[i][2]-data_count[i][1]
        ax.bar(i, total, color='cornflowerblue', width=0.15)
        ax.bar(i , data_count[i][1], bottom=total,color='sandybrown', width=0.15)
        ax.bar(i, data_count[i][2], bottom=data_count[i][1]+total,color='mediumorchid', width=0.15)

    ax.set_xticks(idx)
    ax.set_xticklabels(labels, rotation=65)
    ax.set_xlabel('Patient')
    ax.set_ylabel('# of Scans')
    ax.legend(labels=['Success', 'Less than 88 Bscans', 'Failure - No VG/TO'], bbox_to_anchor=(1.05, 1))
    plt.title('Success',fontsize=18)
    plt.tight_layout()
    plt.ylim([0,100])
    plt.savefig(save_path + '/Compliance.png')
    #plt.show()

def time(data_folder,save_path,patients):
    data=[]
    labels=[]
    total=[]
    for patient in patients:
        DB=pd.read_excel(os.path.join(data_folder,'DB',patient+'_DB.xlsx'))
        for eye in ['R','L']:
            eye_DB=DB[DB['Eye']==eye]
            eye_DB=eye_DB[eye_DB['AdjustmentTime']!=-1]
            adjustment_time = (np.mean(eye_DB['AdjustmentTime']),np.std(eye_DB['AdjustmentTime']))
            total_time = (np.mean(eye_DB['TotalScanTime']),np.std(eye_DB['TotalScanTime']))
            raster_time = (np.mean(eye_DB['RasterTime']),np.std(eye_DB['RasterTime']))
            total.append(len(eye_DB))
            data.append([adjustment_time, raster_time,total_time])
            labels.append('{}_{}'.format(patient, eye))

    mean_ad_time=[]
    for i in range(len(data)):
        mean_ad_time.append(data[i][0][0])
    std_ad_time=np.std(mean_ad_time)
    mean_ad_time=np.mean(mean_ad_time)
    mean_rast_time = []
    for i in range(len(data)):
        mean_rast_time.append(data[i][1][0])
    std_rast_time = np.std(mean_rast_time)
    mean_rast_time = np.mean(mean_rast_time)
    mean_tot_time = []
    for i in range(len(data)):
        mean_tot_time.append(data[i][2][0])
    std_tot_time = np.std(mean_tot_time)
    mean_tot_time = np.mean(mean_tot_time)
    data.append([(mean_ad_time,std_ad_time),(mean_rast_time,std_rast_time),(mean_tot_time,std_tot_time)])
    labels.append('Mean (over eyes)')
    total.append(sum(total))
    idx = np.asarray([i for i in range(len(data))])

    fig,ax = plt.subplots(figsize = (20,10))
    for i in range(len(data)):
        ax.bar(i + 0.00, data[i][0][0], color='cornflowerblue', width=0.25)
        ax.bar(i + 0.25, data[i][1][0], color='m', width=0.25)
        ax.bar(i + 0.50, data[i][2][0], color='mediumseagreen', width=0.25)
        ax.annotate('N={}'.format(total[i]),(i,data[i][2][0]+2))
        for j in range(3):
            if i!=len(data)-1:
                ax.annotate(F'{np.round(data[i][j][0],decimals=0):.0f} ', (i+(0.25*j)-0.1, data[i][j][0]))
            else:
                ax.annotate(F'{np.round(data[i][j][0], decimals=0):.0f}\n({np.round(data[i][j][1], decimals=0):.0f}) ',
                            (i + (0.25 * j) - 0.1, data[i][j][0]))



    ax.set_xticks(idx)
    ax.set_xticklabels(labels, rotation=65)
    ax.set_xlabel('Patient')
    ax.set_ylabel('Time [sec]')
    ax.legend(labels=['Adjustment Time','Raster Time','Total Time'])
    plt.title('Mean Adjustment, Raster, Total time')
    plt.ylim([0,60])
    fig.tight_layout()
    plt.savefig(save_path + '/Adjustment and Total time.png')
    #plt.show()

def mean_MSI(data_folder,save_path,patients):
    data=[]
    labels=[]
    total=[]
    for patient in patients:
        DB=pd.read_excel(os.path.join(data_folder,'DB',patient+'_DB.xlsx'))
        for eye in ['R','L']:
            eye_DB=DB[DB['Eye']==eye]
            MSI_DB=eye_DB[eye_DB['MSI']!=-1]
            msi = np.mean(MSI_DB['MSI'])
            total.append(len(MSI_DB))
            data.append(msi)
            labels.append('{}_{}'.format(patient, eye))

    mean_msi=0
    for i in range(len(data)):
        mean_msi+=data[i]
    mean_msi=mean_msi/len(data)
    data.append(mean_msi)
    labels.append('Mean (over eyes)')
    total.append(sum(total))
    idx = np.asarray([i for i in range(len(data))])

    fig,ax = plt.subplots(figsize = (20,10))
    for i in range(len(data)):
        ax.bar(i + 0.00, data[i], color='cornflowerblue', width=0.25)
        ax.annotate('N={}'.format(total[i]),(i-0.1,data[i]+0.5))
        ax.annotate(F'{np.round(data[i],decimals=1):.1f}', (i-0.1, data[i]+0.05))


    ax.set_xticks(idx)
    ax.set_xticklabels(labels, rotation=65)
    ax.set_xlabel('Patient')
    ax.set_ylabel('MSI')
    plt.title('Mean MSI')
    plt.ylim([0,8])
    fig.tight_layout()
    plt.savefig(save_path + '/MSI.png')
    #plt.show()

def clipped(data_folder,save_path,patients):
    data=[]
    labels=[]
    total=[]
    for patient in patients:
        DB=pd.read_excel(os.path.join(data_folder,'DB',patient+'_DB.xlsx'))
        for eye in ['R','L']:
            eye_DB=DB[DB['Eye']==eye]
            eye_DB = eye_DB[eye_DB['# of bscans clipped>0'] !=-1]
            Clipped_0 = np.mean(eye_DB['# of bscans clipped>0'])
            Clipped_5 = np.mean(eye_DB['# of bscans clipped>5'])
            total.append(len(eye_DB))
            data.append([Clipped_0, Clipped_5])
            labels.append('{}_{}'.format(patient, eye))

    mean_clipped_0 = []
    for i in range(len(data)):
        mean_clipped_0.append(data[i][0])
    std_clipped_0 = np.std(mean_clipped_0)
    mean_clipped_0 = np.mean(mean_clipped_0)
    mean_clipped_5 = []
    for i in range(len(data)):
        mean_clipped_5.append(data[i][1])
    std_clipped_5 = np.std(mean_clipped_5)
    mean_clipped_5 = np.mean(mean_clipped_5)
    std=[std_clipped_0,std_clipped_5]
    data.append([mean_clipped_0,mean_clipped_5])
    labels.append('Mean (over eyes)')
    total.append(sum(total))
    idx = np.asarray([i for i in range(len(data))])

    fig,ax = plt.subplots(figsize = (20,10))
    for i in range(len(data)):
        ax.bar(i + 0.00, data[i][0], color='cornflowerblue', width=0.25)
        ax.bar(i + 0.25, data[i][1], color='m', width=0.25)
        ax.annotate('N={}'.format(total[i]),(i,data[i][0]+2))
        for j in range(2):
            if i != len(data) - 1:
                ax.annotate(F'{np.round(data[i][j],decimals=2):.0f} ({np.round(data[i][j]/88*100,decimals=2):.0f}%)', (i+(0.25*j)-0.1, data[i][j]))
            else:
                ax.annotate(F'{np.round(data[i][j], decimals=0):.0f} (STD={np.round(std[j], decimals=0):.0f}) ',
                            (i + (0.25 * j) - 0.1, data[i][j]))


    ax.set_xticks(idx)
    ax.set_xticklabels(labels, rotation=65)
    ax.set_xlabel('Patient')
    ax.set_ylabel('# Clipped Bscans')
    ax.legend(labels=['# Clipped', '# Clipped > 5%'])
    plt.title('Mean # Clipped Bscans After Volume Reconstruction (% out of 88)')
    plt.ylim([0,30])
    fig.tight_layout()
    plt.savefig(save_path + '/Clipped Bscans.png')
    #plt.show()

def reg(data_folder,save_path,patients):
    data=[]
    labels=[]
    total=[]
    for patient in patients:
        DB=pd.read_excel(os.path.join(data_folder,'DB',patient+'_DB.xlsx'))
        for eye in ['R','L']:
            eye_DB=DB[DB['Eye']==eye]
            eye_DB = eye_DB[eye_DB['RegStdX'] != -1]
            RegStdX = np.mean(eye_DB['RegStdX'])
            RegStdY = np.mean(eye_DB['RegStdY'])
            total.append(len(eye_DB))
            data.append([RegStdX,RegStdY])
            labels.append('{}_{}'.format(patient, eye))

    mean_reg_x=0
    for i in range(len(data)):
        mean_reg_x+=data[i][0]
    mean_reg_x=mean_reg_x/len(data)
    mean_reg_y = 0
    for i in range(len(data)):
        mean_reg_y+=data[i][1]
    mean_reg_y=mean_reg_y/len(data)
    data.append([mean_reg_x,mean_reg_y])
    labels.append('Mean (over eyes)')
    total.append(sum(total))
    idx = np.asarray([i for i in range(len(data))])

    fig,ax = plt.subplots(figsize = (20,10))
    for i in range(len(data)):
        ax.bar(i + 0.00, data[i][0], color='cornflowerblue', width=0.25)
        ax.bar(i + 0.25, data[i][1], color='m', width=0.25)
        ax.annotate('N={}'.format(total[i]),(i,max(data[i])+10))
        for j in range(2):
            ax.annotate(F'{np.round(data[i][j],decimals=0):.0f}', (i+(0.25*j)-0.1, data[i][j]))


    ax.set_xticks(idx)
    ax.set_xticklabels(labels, rotation=65)
    ax.set_xlabel('Patient')
    ax.set_ylabel('RegStdX/RegStdY [um]')
    ax.legend(labels=['RegStdX','RegStdY'])
    plt.title('Mean RegStdX & RegStdY')
    fig.tight_layout()
    plt.savefig(save_path + '/Regx_Regy.png')
    #plt.show()

if __name__ =="__main__":
    network = '172.17.102.175'  # 'nv -nas01'
    data_folder = r'\\{}\Home_OCT_Repository\Clinical_studies\Notal-Home_OCT_study-box3.0\Study_at_home\Data'.format(network)
    save_path=os.path.join(data_folder,'Analysis')
    patients = ['NH01001','NH01002', 'NH01005', 'NH01006', 'NH02001', 'NH02002', 'NH02003']
    new_patients=['NH02001', 'NH02002', 'NH02003']
    compliance_analysis(data_folder,save_path,patients)
    Bscan_Class_Distributio_per_Eye_analysis(data_folder,save_path,new_patients)
    Scan_Class_Distribution_per_Eye_analysis(data_folder,save_path,new_patients)
    time(data_folder,save_path,patients)
    mean_MSI(data_folder,save_path,patients)
    clipped(data_folder,save_path,new_patients)
    reg(data_folder,save_path,patients)