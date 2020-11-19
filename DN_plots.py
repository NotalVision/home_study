import pandas as pd
import numpy as np
import os
from os import path
from datetime import date
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from DB_connection import check_if_downloaded
import scipy.io as sio

def DN_plots(data_folder, patient,save_path):
    dn_db_path=os.path.join(data_folder,patient,'analysis','{}_DN_DB.xlsx'.format(patient))
    dn_db=pd.read_excel(dn_db_path)

    # plot long shift
    fig = plt.figure(figsize=(20, 10))
    for i, eye in enumerate(['R', 'L'], 0):
        time_table = dn_db[dn_db['Eye'] == eye]
        x_long_shift = time_table['x_long_shift']
        y_long_shift = time_table['y_long_shift']
        time_axis = pd.to_datetime(time_table['Date - Time'], format='%Y-%m-%d-%H-%M-%S')
        time_axis = pd.DatetimeIndex(time_axis).date
        ax = fig.add_subplot(2, 1, i + 1)
        plt.subplots_adjust(hspace=0.3)
        formatter = mdates.DateFormatter('%m-%d')
        ax.plot(time_axis, x_long_shift, marker='o')
        ax.plot(time_axis, y_long_shift, marker='o')
        if eye == 'L':
            plt.title('LEFT EYE - Longitudinal Shift', fontsize=16)
        if eye == 'R':
            plt.title('RIGHT EYE - Longitudinal Shift', fontsize=16)
        ax.set_xlabel('Date')

        ax.xaxis.set_major_formatter(formatter)
        ax.set_ylabel('Shift [um]')
        #plt.ylim((0, 100))
        ax.xaxis.set_ticks(time_axis)
        plt.xticks(fontsize=8)
        plt.xticks(rotation=45)
        plt.legend(['x_long_shift', 'y_long_shift'])
        # Get events

        plt.grid()

    plt.savefig(save_path.replace('DN','VG') + '/long_shift.png')

    # plot max gap
    fig = plt.figure(figsize=(20, 10))
    for i, eye in enumerate(['R', 'L'], 0):
        time_table = dn_db[dn_db['Eye'] == eye]
        MaxGapQuant = time_table['MaxGapQuant']
        meanMaxGap=np.round(np.nanmean(MaxGapQuant),decimals=2)
        medianMaxGap = np.round(np.nanmedian(MaxGapQuant),decimals=2)
        time_axis = pd.to_datetime(time_table['Date - Time'], format='%Y-%m-%d-%H-%M-%S')
        time_axis = pd.DatetimeIndex(time_axis).date
        ax = fig.add_subplot(2, 1, i + 1)
        plt.subplots_adjust(hspace=0.3)
        formatter = mdates.DateFormatter('%m-%d')
        ax.plot(time_axis, MaxGapQuant, marker='o')
        if eye == 'L':
            plt.title('LEFT EYE - Quantification Max Gap, Mean: {}  Median: {}'.format(str(meanMaxGap),str(medianMaxGap)) , fontsize=16)
        if eye == 'R':
            plt.title('RIGHT EYE - Quantification Max Gap, Mean: {}  Median: {}'.format(str(meanMaxGap),str(medianMaxGap)), fontsize=16)
        ax.set_xlabel('Date')

        ax.xaxis.set_major_formatter(formatter)
        ax.set_ylabel('Max Gap [um]')
        plt.ylim((0, max(10,max(MaxGapQuant))))
        plt.hlines(y=300,xmin=time_axis[0],xmax=time_axis[-1],linestyles='--', color='r',label='Threshold')
        ax.xaxis.set_ticks(time_axis)
        plt.xticks(fontsize=8)
        plt.xticks(rotation=45)
        #plt.text(time_axis[-1],max(MaxGapQuant),('Mean: {}\n STD: {}'.format(str(meanMaxGap),str(stdMaxGap))),fontsize=10,
                 #bbox={'facecolor': 'white', 'alpha': 0.5, 'pad': 10})
        plt.legend()
        plt.grid()

    plt.savefig(save_path + '/Quantification max gap.png')

    # plot eligibilty
    fig = plt.figure(figsize=(20, 10))
    for i, eye in enumerate(['R', 'L'], 0):
        time_table = dn_db[dn_db['Eye'] == eye]
        EligibleQuant = time_table['EligibleQuant']
        MSI = time_table[(time_table['MSI']<=2) & (time_table['MSI']!=-1) ]
        MSI=pd.to_datetime(MSI['Date - Time'], format='%Y-%m-%d-%H-%M-%S')
        MSI_dates = pd.DatetimeIndex(MSI).date
        MaxGapQuant = time_table[(time_table['MSI']>2) & (time_table['MaxGapQuant']>=300)]
        MaxGapQuant = pd.to_datetime(MaxGapQuant['Date - Time'], format='%Y-%m-%d-%H-%M-%S')
        MaxGapQuant_dates = pd.DatetimeIndex(MaxGapQuant).date
        time_axis = pd.to_datetime(time_table['Date - Time'], format='%Y-%m-%d-%H-%M-%S')
        time_axis = pd.DatetimeIndex(time_axis).date
        ax = fig.add_subplot(2, 1, i + 1)
        plt.subplots_adjust(hspace=0.3)
        formatter = mdates.DateFormatter('%m-%d')
        ax.plot(time_axis, EligibleQuant, marker='o',zorder=2)
        ax.scatter(MSI_dates, [0 for i in range(len(MSI_dates))], s=35, c='red', zorder=4, label='MSI<=2')
        ax.scatter(MaxGapQuant_dates, [0 for i in range(len(MaxGapQuant_dates))], s=35, c='black', zorder=3, label='MaxGap>300')
        if eye == 'L':
            plt.title('LEFT EYE - EligibleQuant', fontsize=16)
        if eye == 'R':
            plt.title('RIGHT EYE - EligibleQuant', fontsize=16)
        ax.set_xlabel('Date')

        ax.xaxis.set_major_formatter(formatter)
        ax.set_ylabel('Eligible (0/1)')
        plt.ylim((-0.1, 1.1))
        ax.xaxis.set_ticks(time_axis)
        plt.xticks(fontsize=8)
        plt.xticks(rotation=45)
        leg=ax.legend()
        # Get events

        plt.grid()

    plt.savefig(save_path + '/Scan Eligibilty.png')


    # plot FLUID VOLUME
    fig = plt.figure(figsize=(20, 10))
    for i, eye in enumerate(['R', 'L'], 0):
        time_table = dn_db[dn_db['Eye'] == eye]
        SrfVolume = time_table['SrfVolume Class']
        IrfVolume = time_table['IrfVolume Class']
        MSI = time_table['MSI']
        Ineligible = time_table[time_table['EligibleQuant'] ==0]
        IneligibleDates = pd.to_datetime(Ineligible['Date - Time'], format='%Y-%m-%d-%H-%M-%S')
        IneligibleDates = pd.DatetimeIndex(IneligibleDates).date
        IneligibleMSI = Ineligible['MSI']
        Ineligiblesrf = Ineligible['SrfVolume Class']
        Ineligibleirf = Ineligible['IrfVolume Class']
        time_axis = pd.to_datetime(time_table['Date - Time'], format='%Y-%m-%d-%H-%M-%S')
        time_axis = pd.DatetimeIndex(time_axis).date
        ax1 = fig.add_subplot(2, 1, i + 1)
        plt.subplots_adjust(hspace=0.3)
        formatter = mdates.DateFormatter('%m-%d')
        ax1.plot(time_axis, SrfVolume, marker='o',zorder=4,label='SRF',color='gold')
        ax1.plot(time_axis, IrfVolume, marker='o', zorder=4,label='IRF',color='red')
        ax2 = ax1.twinx()
        ax2.plot(time_axis, MSI, marker='s', alpha=0.5,linestyle='--',zorder=2,label='MSI',color='blue',linewidth=1)
        ax1.scatter(IneligibleDates, Ineligiblesrf, s=30, c='white', zorder=3)
        ax1.scatter(IneligibleDates, Ineligibleirf, s=30, c='white', zorder=3)
        ax2.scatter(IneligibleDates, IneligibleMSI, s=30, c='white', zorder=3)
        # ax.scatter(MaxGapQuant_dates, [0 for i in range(len(MaxGapQuant_dates))], s=35, c='black', zorder=3, label='MaxGap>300')
        if eye == 'L':
            plt.title('LEFT EYE - Fluid Volume vs. MSI', fontsize=16)
        if eye == 'R':
            plt.title('RIGHT EYE - Fluid Volume vs. MSI', fontsize=16)
        ax1.set_xlabel('Date')


        ax1.set_ylabel('Fluid Volume [nl]')
        ax2.set_ylabel('MSI')
        ax1.set_ylim((-0.3, max(max(SrfVolume),max(IrfVolume),10)*1.1))
        ax2.set_ylim((0,8))
        ax1.set_xticks(time_axis)
        ax1.set_xticklabels(time_axis,rotation=45)
        ax1.xaxis.set_major_formatter(formatter)
        plt.xticks(fontsize=8)
        plt.xticks(rotation=45)
        leg = ax1.legend(loc='upper left')
        leg = ax2.legend(loc='upper right')
        # Get events

        plt.grid()

    plt.savefig(save_path + '/Fluid Volume vs. MSI.png')


    # plot class vs seg
    fig = plt.figure(figsize=(20, 10))
    for i, eye in enumerate(['R', 'L'], 0):
        time_table = dn_db[dn_db['Eye'] == eye]
        noClassFluid = time_table['Fluid Volume No Class']
        ClassWithFluid = time_table[time_table['Classifier Fluid Decision'] == 1]
        ClassWithFluidDates = pd.to_datetime(ClassWithFluid['Date - Time'], format='%Y-%m-%d-%H-%M-%S')
        ClassWithFluidDates = pd.DatetimeIndex(ClassWithFluidDates).date
        ClassWithFluidVal=ClassWithFluid['Fluid Volume No Class']
        ClassWithoutFluid = time_table[time_table['Classifier Fluid Decision'] == 0]
        ClassWithoutFluidDates = pd.to_datetime(ClassWithoutFluid['Date - Time'], format='%Y-%m-%d-%H-%M-%S')
        ClassWithoutFluidDates = pd.DatetimeIndex(ClassWithoutFluidDates).date
        ClassWithoutFluidVal = ClassWithoutFluid['Fluid Volume No Class']
        time_axis = pd.to_datetime(time_table['Date - Time'], format='%Y-%m-%d-%H-%M-%S')
        time_axis = pd.DatetimeIndex(time_axis).date
        ax = fig.add_subplot(2, 1, i + 1)
        plt.subplots_adjust(hspace=0.3)
        formatter = mdates.DateFormatter('%m-%d')
        #ax.plot(time_axis, classFluid, marker='o',zorder=2,label='Classification',color='royalblue')
        ax.plot(time_axis, noClassFluid, marker='o', zorder=2,label='Volume',color='dimgray',linestyle='--')
        ax.scatter(ClassWithFluidDates, ClassWithFluidVal, s=30, c='mediumseagreen', zorder=4,label='Classification = 1')
        ax.scatter(ClassWithoutFluidDates, ClassWithoutFluidVal, s=30, c='r', zorder=4, label='Classification = 0')

        if eye == 'L':
            plt.title('LEFT EYE - Fluid Volume - Classification vs. Segmentation', fontsize=16)
        if eye == 'R':
            plt.title('RIGHT EYE - Fluid Volume -  Classification vs. Segmentation', fontsize=16)
        ax.set_xlabel('Date')


        ax.set_ylabel('Fluid Volume [nl]')
        ax.set_ylim((-0.3, max(max(noClassFluid),10)*1.1))
        #ax2.set_ylim((0,8))
        ax.xaxis.set_major_formatter(formatter)
        ax.xaxis.set_ticks(time_axis)
        plt.xticks(fontsize=8)
        plt.xticks(rotation=45)
        leg = ax.legend()
        # Get events

        plt.grid()

    plt.savefig(save_path + '/Classification vs. Segmentation.png')