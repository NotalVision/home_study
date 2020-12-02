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
            if eye_DB.empty:
                continue
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
            if eye_DB.empty:
                continue
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
            if full_table.empty:
                continue

            dates=pd.to_datetime(full_table['Date - Time'], format='%Y-%m-%d-%H-%M-%S')
            dates=pd.DatetimeIndex(dates).date
            if len(dates)==0:
                continue
            first_date=dates[0]
            total = pd.date_range(start=first_date, end=dates[-1])
            missing = pd.date_range(start=first_date, end=dates[-1]).difference(dates)
            comp=100-len(missing)/len(total)*100


            incomplete=full_table[(full_table['Full Scan(88)']==0)|(full_table['TimeOut']==1)]
            incomplete=incomplete[incomplete['VG_output']==1]
            incomplete_dates = pd.to_datetime(incomplete['Date - Time'], format='%Y-%m-%d-%H-%M-%S')
            incomplete_count=len(pd.DatetimeIndex(incomplete_dates).date)
            incomplete_dates = pd.DatetimeIndex(incomplete_dates).date
            incomplete_dates = len(incomplete_dates) / len(full_table) * 100

            failure = full_table[(full_table['VG_output']==0) ]
            failure_dates = pd.to_datetime(failure['Date - Time'], format='%Y-%m-%d-%H-%M-%S')
            failure_count=len(pd.DatetimeIndex(failure_dates).date)
            failure_dates = pd.DatetimeIndex(failure_dates).date
            failure_dates = len(failure_dates) / len(full_table) * 100
            data.append([comp, incomplete_dates,failure_dates,len(total)])
            data_count.append([len(full_table),incomplete_count,failure_count])
            labels.append('{}_{}'.format(patient, eye))

    mean_comp = []
    for i in range(len(data)):
        mean_comp.append(data[i][0])
    std_comp = np.std(mean_comp)
    mean_comp = np.mean(mean_comp)
    mean_incomplete = []
    for i in range(len(data)):
        mean_incomplete.append(data[i][1])
    std_incomplete = np.std(mean_incomplete)
    mean_incomplete = np.mean(mean_incomplete)
    mean_failure = []
    for i in range(len(data)):
        mean_failure.append(data[i][2])
    std_failure = np.std(mean_failure)
    mean_failure = np.mean(mean_failure)
    data.append([(mean_comp, std_comp),(mean_incomplete, std_incomplete),(mean_failure, std_failure)])
    labels.append('Mean (over eyes)')

    idx = np.asarray([i for i in range(len(data))])
    ax=fig.add_subplot(2,1,1)
    for i in range(len(data)):
        ax.bar(i, data[i][0], color='cornflowerblue', width=0.15)
        if i != len(data) - 1:
            ax.annotate(F'{np.round(data[i][0],decimals=0):.0f}%', (i-0.1, data[i][0] + 2))
        else:
            ax.annotate(F'{np.round(data[i][0][0], decimals=0):.0f}%\n({np.round(data[i][0][1], decimals=0):.0f}) ',
                        (i - 0.1, data[i][0][0]))

    ax.set_xticks(idx)
    ax.set_xticklabels(labels, rotation=65)
    ax.set_xlabel('Patient')
    ax.set_ylabel('% of All Scans')
    plt.title('Compliance per Eye',fontsize=18)

    ax = fig.add_subplot(2, 1, 2)
    for i in range(len(data)):
        ax.bar(i , data[i][1], color='sandybrown', width=0.15)
        if i != len(data) - 1:
            if data[i][1] != 0:
                ax.annotate(F'{np.round(data[i][1], decimals=0):.0f}%', (i+ 0.1, data[i][1]))
        else:
            ax.annotate(F'{np.round(data[i][1][0], decimals=0):.0f}%\n({np.round(data[i][1][1], decimals=0):.0f})', (i + 0.1, data[i][1][0]))


        if i != len(data) - 1:
            ax.bar(i, data[i][2], bottom=data[i][1], color='mediumorchid', width=0.15)
            if data[i][2] != 0:
                ax.annotate(F'{np.round(data[i][2], decimals=0):.0f}%',
                         (i + 0.1,(data[i][2]+data[i][1] +2)))
        else:
            ax.bar(i+0.15, data[i][2][0], color='mediumorchid', width=0.15)
            ax.annotate(F'{np.round(data[i][2][0], decimals=0):.0f}%\n({np.round(data[i][2][1], decimals=0):.0f})',
                        (i + 0.1, data[i][2][1]))



    ax.set_xticks(idx)
    ax.set_xticklabels(labels, rotation=65)
    ax.set_xlabel('Patient')
    ax.set_ylabel('% of Scans')
    ax.legend(labels=['Incomplete', 'Failure '], bbox_to_anchor=(1.05, 1))
    plt.title('Success',fontsize=18)
    #plt.tight_layout()
    plt.ylim([0,120])
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
            if eye_DB.empty:
                continue
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
    plt.ylim([0,150])
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
            if eye_DB.empty:
                continue
            MSI_DB=eye_DB[eye_DB['MSI']!=-1]
            msi = np.mean(MSI_DB['MSI'])
            total.append(len(MSI_DB))
            data.append(msi)
            labels.append('{}_{}'.format(patient, eye))
    mean_msi = []
    for i in range(len(data)):
        mean_msi.append(data[i])
    std_msi = np.std(mean_msi)
    mean_msi = np.mean(mean_msi)
    data.append(mean_msi)
    labels.append('Mean (over eyes)')
    total.append(sum(total))
    idx = np.asarray([i for i in range(len(data))])

    fig,ax = plt.subplots(figsize = (20,10))
    for i in range(len(data)):
        ax.bar(i + 0.00, data[i], color='cornflowerblue', width=0.25)
        ax.annotate('N={}'.format(total[i]),(i-0.1,data[i]+0.5))
        if i != len(data) - 1:
            ax.annotate(F'{np.round(data[i],decimals=1):.1f}', (i-0.1, data[i]+0.05))
        else:
            ax.annotate(F'{np.round(data[i], decimals=0):.0f} (STD={np.round(std_msi, decimals=0):.0f}) ',
                        (i +  - 0.1, data[i]))



    ax.set_xticks(idx)
    ax.set_xticklabels(labels, rotation=65)
    ax.set_xlabel('Patient')
    ax.set_ylabel('MSI')
    plt.title('Mean MSI')
    plt.ylim([0,8])
    fig.tight_layout()
    plt.savefig(save_path + '/MSI.png')
    #plt.show()

def MSI_lower_than2(data_folder,save_path,patients):
    data=[]
    labels=[]
    total=[]
    for patient in patients:
        DB=pd.read_excel(os.path.join(data_folder,'DB',patient+'_DB.xlsx'))
        for eye in ['R','L']:
            eye_DB=DB[DB['Eye']==eye]
            if eye_DB.empty:
                continue
            MSI_DB=eye_DB[eye_DB['% MSI<2']!=-1]
            msi = np.mean(MSI_DB['% MSI<2'])
            total.append(len(MSI_DB))
            data.append(msi)
            labels.append('{}_{}'.format(patient, eye))

    mean_msi = []
    for i in range(len(data)):
        mean_msi.append(data[i])
    std_msi = np.std(mean_msi)
    mean_msi = np.mean(mean_msi)
    data.append(mean_msi)
    labels.append('Mean (over eyes)')
    total.append(sum(total))
    idx = np.asarray([i for i in range(len(data))])

    fig,ax = plt.subplots(figsize = (20,10))
    for i in range(len(data)):
        ax.bar(i + 0.00, data[i], color='cornflowerblue', width=0.25)
        ax.annotate('N={}'.format(total[i]), (i - 0.1, data[i] + 1))
        if i != len(data) - 1:
            ax.annotate(F'{np.round(data[i], decimals=1):.1f}%', (i - 0.1, data[i] + 0.05))
        else:
            ax.annotate(F'{np.round(data[i], decimals=0):.0f}% (STD={np.round(std_msi, decimals=0):.0f}) ',
                        (i + - 0.1, data[i]))


    ax.set_xticks(idx)
    ax.set_xticklabels(labels, rotation=65)
    ax.set_xlabel('Patient')
    ax.set_ylabel('% of scans')
    plt.title('Mean % of Scans with MSI lower than 2')
    #plt.ylim([0,max(data)])
    fig.tight_layout()
    plt.savefig(save_path + '/MSI_lower_than2.png')
    #plt.show()

def clipped(data_folder,save_path,patients):
    data=[]
    labels=[]
    total=[]
    for patient in patients:
        DB=pd.read_excel(os.path.join(data_folder,'DB',patient+'_DB.xlsx'))
        for eye in ['R','L']:
            eye_DB=DB[DB['Eye']==eye]
            if eye_DB.empty:
                continue
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
            if eye_DB.empty:
                continue
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
        ax.annotate('N={}'.format(total[i]),(i,max(data[i])+5))
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

def eligibilty(data_folder,save_path,patients):
    data=[]
    labels=[]
    total=[]
    for patient in patients:
        DB=pd.read_excel(os.path.join(data_folder,patient,'Analysis',patient+'_DN_DB.xlsx'))
        for eye in ['R','L']:
            eye_DB=DB[DB['Eye']==eye]
            if eye_DB.empty:
                continue
            low_msi= eye_DB[( eye_DB['MSI']<=2) & ( eye_DB['MSI']!=-1) ]
            low_msi_count=len(low_msi)/len(eye_DB)*100
            MaxGapQuant = eye_DB[(eye_DB['MSI'] > 2) & (eye_DB['MaxGapQuant'] >= 300)]
            maxGap_count=len(MaxGapQuant)/len(eye_DB)*100
            total.append(len(eye_DB))
            data.append([low_msi_count,maxGap_count])
            labels.append('{}_{}'.format(patient, eye))

    mean_low_msi=[]
    for i in range(len(data)):
        mean_low_msi.append(data[i][0])
    std_low_msi = np.std(mean_low_msi)
    mean_low_msi = np.mean(mean_low_msi)
    mean_max_gap = []
    for i in range(len(data)):
        mean_max_gap.append(data[i][1])
    std_max_gap = np.std(mean_max_gap)
    mean_max_gap = np.mean(mean_max_gap)
    std = [std_low_msi, std_max_gap]
    data.append([mean_low_msi, mean_max_gap])
    labels.append('Mean (over eyes)')
    total.append(sum(total))
    idx = np.asarray([i for i in range(len(data))])

    fig,ax = plt.subplots(figsize = (20,10))
    for i in range(len(data)):
        ax.bar(i + 0.00, data[i][0], color='cornflowerblue', width=0.25)
        ax.bar(i + 0.25, data[i][1], color='m', width=0.25)
        ax.annotate('N={}'.format(total[i]),(i,max(data[i])+1))
        for j in range(2):
            if i != len(data) - 1:
                if data[i][j] != 0:
                    ax.annotate(
                        F'{np.round(data[i][j], decimals=2):.0f}% ({np.round(data[i][j] * total[i] / 100, decimals=2):.0f})',
                        (i + (0.25 * j) - 0.1, data[i][j]))
            else:
                ax.annotate(F'{np.round(data[i][j], decimals=0):.0f}% (STD={np.round(std[j], decimals=0):.0f}%) ',
                            (i + (0.25 * j) - 0.15, data[i][j]))


    ax.set_xticks(idx)
    ax.set_xticklabels(labels, rotation=65)
    ax.set_xlabel('Patient')
    ax.set_ylabel('% of Scans (# of Ineligible scans)')
    ax.legend(labels=['MSI<=2','MaxGap>300'])
    plt.title('Scan Ineligibility')
    #plt.ylim([0,25])
    fig.tight_layout()
    plt.savefig(save_path + '/Ineligibility.png')
    #plt.show()

def MaxGapQuant(data_folder,save_path,patients):
    data=[]
    labels=[]
    total=[]
    for patient in patients:
        DB=pd.read_excel(os.path.join(data_folder,patient,'Analysis',patient+'_DN_DB.xlsx'))
        for eye in ['R','L']:
            eye_DB=DB[DB['Eye']==eye]
            if eye_DB.empty:
                continue
            eye_DB = eye_DB[eye_DB['MaxGapQuant'] != -1]
            MaxGapQuant = np.mean(eye_DB['MaxGapQuant'])
            total.append(len(eye_DB))
            data.append(MaxGapQuant)
            labels.append('{}_{}'.format(patient, eye))

    mean_MaxGapQuant=[]
    for i in range(len(data)):
        mean_MaxGapQuant.append(data[i])
    std_MaxGapQuant = np.std(mean_MaxGapQuant)
    mean_MaxGapQuant = np.mean(mean_MaxGapQuant)
    data.append(mean_MaxGapQuant)
    labels.append('Mean (over eyes)')
    total.append(sum(total))
    idx = np.asarray([i for i in range(len(data))])

    fig,ax = plt.subplots(figsize = (20,10))
    for i in range(len(data)):
        ax.bar(i + 0.00, data[i], color='cornflowerblue', width=0.25)
        ax.annotate('N={}'.format(total[i]),(i-0.1,data[i]+4))
        ax.annotate(F'{np.round(data[i],decimals=0):.0f}', (i+-0.1, data[i]))
        if i==len(data)-1:
            ax.bar(i + 0.25, std_MaxGapQuant, color='m', width=0.25)
            ax.annotate(F'STD={np.round(std_MaxGapQuant, decimals=0):.0f}', (i + 0.15, std_MaxGapQuant))



    ax.set_xticks(idx)
    ax.set_xticklabels(labels, rotation=65)
    ax.set_xlabel('Patient')
    ax.set_ylabel('Max Gap Quant [um]')
    #ax.legend(labels=['RegStdX','RegStdY'])
    plt.title('Quantification Max Gap')
    fig.tight_layout()
    plt.savefig(save_path + '/Quant Max Gap.png')
    #plt.show()


if __name__ =="__main__":
    network = '172.17.102.175'  # 'nv -nas01'
    #data_folder = r'\\{}\Home_OCT_Repository\Clinical_studies\Notal-Home_OCT_study-box3.0\Study_at_home\Data'.format(network)
    data_folder = r'\\{}\Home_OCT_Repository\Clinical_studies\Notal-Home_OCT_study-box3.0\Study_US\Clinics\Elman\Data'.format(
        network)
    VG_save_path=os.path.join(data_folder,'Analysis/VG')
    DN_save_path = os.path.join(data_folder, 'Analysis/DN')
    # patients = ['NH01001','NH01002', 'NH01005', 'NH01006', 'NH02001', 'NH02002', 'NH02003']
    # new_patients=['NH02001', 'NH02002', 'NH02003']
    all_patients=['8001','8002','8003','8004','8005'] #might not have DC
    patients=[]
    for patient in all_patients:
        if os.path.isfile(os.path.join(data_folder, 'DB', patient + '_DB.xlsx')):
            patients.append(patient)
    new_patients=patients # only patients with existing DB file

    compliance_analysis(data_folder,VG_save_path,patients)
    Bscan_Class_Distributio_per_Eye_analysis(data_folder,VG_save_path,new_patients)
    Scan_Class_Distribution_per_Eye_analysis(data_folder,VG_save_path,new_patients)
    time(data_folder,VG_save_path,patients)
    mean_MSI(data_folder,VG_save_path,patients)
    MSI_lower_than2(data_folder, VG_save_path, patients)
    clipped(data_folder,VG_save_path,new_patients)
    reg(data_folder,VG_save_path,patients)
    try:
        eligibilty(data_folder,DN_save_path,new_patients)
        MaxGapQuant(data_folder,DN_save_path,new_patients)
    except:
        print ('Could not generate eligibility/max gap plots')

    all_patients_db_col = ['Patient','Date - Time','Eye','Device', 'ScanID','Session', 'Scan Ver', 'VG Ver','VG_output','checked_for_alerts',
                   'MSI','Vmsi', 'MaxBMsiVsr','Max_BMSIAllRaw','% MSI<2','AdjustmentTime','RasterTime', 'TotalScanTime', 'NumValidLines','NumValidBatchReg',
                   'VsrRemoveOutFOV', 'MeanGap', 'MaxGap','ClippedPrecent', '# of bscans clipped>0','# of bscans clipped>5',
                    'RegCentX','RegCentY','RegRangeX','RegRangeY',
                   'RegStdX', 'RegStdY','MeanXCover', 'MeanRetinalThickness3*3', 'MeanRetinalThicknessCST',
                   'MeanRetinalThicknessNIM', 'MeanRetinalThicknessTIM', 'MeanRetinalThicknessSIM',
                   'MeanRetinalThicknessIIM','x_long_shift','y_long_shift','Compliance','TimeOut','Alert_for_clipped','88+ Class 1',
               'Full Scan(88)', '# Class 1', '# Class 2', '# Class 3', '% Class 1', '% Class 2',
               '% Class 3','Scan']
    all_patients_db = pd.DataFrame()
    for patientID in patients:
        try:
            patient_db = os.path.join(data_folder, 'DB','{}_DB.xlsx'.format(patientID))
            curr_patient_db = pd.read_excel(patient_db)
        except:
            print('DB for patient {} does not exist'.format(patientID))
            continue
        curr_patient_db = curr_patient_db[all_patients_db_col]
        all_patients_db = pd.concat([all_patients_db, curr_patient_db])
    all_patients_db = all_patients_db.sort_values(by=['Date - Time', 'Patient'])
    save_name = os.path.join(data_folder,'Analysis', 'Combined_DB.xlsx')
    all_patients_db.to_excel(save_name,index=False)