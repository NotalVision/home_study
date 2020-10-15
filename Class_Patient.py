import pandas as pd
import numpy as np
import os
from os import path
from datetime import date
import scipy.io as sio
from email.message import EmailMessage
import smtplib
import csv
from Alerts import Alert
import pickle
pd.options.mode.chained_assignment = None
from DB_connection import check_if_downloaded
from Patient_Utils import check_vg_status,check_if_timeout






class Patient:
    def __init__(self,data_folder, patientID,eye):
        self.data_path=data_folder+'/'+patientID
        self.patient_ID=patientID
        self.eye=eye
        self.email_text=''

        self.analysis_folder=(data_folder +'/'+ patientID + '/Analysis')
        if not os.path.isdir(self.analysis_folder):
            os.mkdir(self.analysis_folder)
        self.DB_path=(self.analysis_folder+'/'+ patientID + '_DB.xlsx')
        self.ver3_DB_path=(self.analysis_folder+ '/'+ patientID + '_{}_ver3_class_data.xlsx'.format(eye))
        self.analysis_summary_path= (self.analysis_folder+ '/' + patientID+'_{}_scan_quality_&_fixation.xlsx'.format(eye))
        self.alerts = Alert(self)
        if os.path.isfile(self.DB_path):  #create new DB only if doesn't exist yet
            self.DB=pd.read_excel(self.DB_path)
            self.DB=self.DB[self.DB['Eye']==eye]
            self.alert=self.alerts.load_existing()
            self.new=0
        else:
            self.new=1
            self.alert=self.alerts.create_new()



    def full_analysis(self,host):
        if self.new==1:
            self.DB=pd.DataFrame()
            self.ver3_DB=pd.DataFrame()

        columns_new_row = [ 'Patient', 'Date - Time', 'Eye','Device', 'ScanID', 'Session', 'Scan Ver', 'VG Ver',
                           'VG_output', 'checked_for_alerts','x_long_shift', 'y_long_shift','Compliance','TimeOut','88+ Class 1', 'Full Scan(88)',
                            '# Class 1','# Class 2','# Class 3','% Class 1','% Class 2','% Class 3']
        try:
            scans_list = os.listdir(self.data_path + '/' + self.eye + '/Hoct') #check for scans
        except:
            scans_list=[]

        isDownloaded = check_if_downloaded(host)
        new_data=False
        for scan in scans_list:
            if 'TST' in scan:
                scan_path = self.data_path + '/' + self.eye + '/Hoct/' + scan
                data_sum = scan_path + '/DataSummary.txt'  ##get session_id and scan_id
                try:
                    with open(data_sum,'r') as f:
                        session_ID=f.readline()
                        scan_ID = f.readline()
                except:
                    continue
                #isDownloaded=check_if_downloaded(session_ID)
                if int(session_ID[12:-1]) in isDownloaded:
                    new_row = pd.DataFrame(columns=columns_new_row)
                    new_row.loc[0, 'Scan'] = scan_path
                    new_row.loc[0, 'TimeOut'] = check_if_timeout(scan_path)
                    new_row.loc[0, 'Compliance'] = 1
                    new_row.loc[0, 'checked_for_alerts']=0
                    new_row.loc[0, 'Patient'] = self.patient_ID
                    new_row.loc[0, 'Eye'] = self.eye
                    date_time = scan[10:29]
                    try:
                        if date_time in self.DB['Date - Time'].array:
                            cur_row=self.DB[self.DB['Date - Time']==date_time]
                            cur_vg_output=cur_row['VG_output'].values[0]
                            if cur_vg_output==1 or cur_vg_output==0:
                                continue
                            if cur_vg_output == 2:
                                vg_output, new_row = self.extract_VG_data(scan, scan_path, new_row)
                                continue
                    except:
                        pass

                    new_row.loc[0,'Date - Time']=date_time
                    device = scan[0:9]
                    new_row.loc[0, 'Device']=device

                    if 'TST_V1' in scan:
                        scan_ver='V1'
                    if 'TST_V2' in scan:
                        scan_ver='V2'
                    if 'TST_V3' in scan:
                        scan_ver='V3'

                    new_row.loc[0, 'ScanID']=scan_ID[9:15]
                    new_row.loc[0, 'Session'] = session_ID[12:]
                    new_row.loc[0, 'Scan Ver'] = scan_ver

                    vg_output, new_row = self.extract_VG_data(scan, scan_path, new_row)
                    if vg_output == False:
                        self.DB = pd.concat([self.DB, new_row])
                        continue

                    long_path = scan_path + r'\Longitudinal\VG\Data\OrigShiftCalcLongi.mat'
                    if not os.path.isfile(long_path):
                        long_path = scan_path + r'\Longitudinal_2\VG\Data\OrigShiftCalcLongi.mat'
                    if not os.path.isfile(long_path):
                        long_path = scan_path + r'\Longitudinal_ver3\VG\Data\OrigShiftCalcLongi.mat'

                    try:
                        shift = sio.loadmat(long_path)
                        shift_x = shift['shift'][0][0]
                        shift_y = shift['shift'][0][1]

                    except:
                        shift_x = np.nan
                        shift_y = np.nan
                        print('no OrigShiftCalcLongi for ' + scan)

                    new_row.loc[0, 'x_long_shift'] = shift_x
                    new_row.loc[0, 'y_long_shift'] = shift_y
                    ##~~~~~~~~~~Alerts~~~~ #####

                    email_text,new_row=self.alert.check_for_alerts(self,new_row,scan_path)
                    self.email_text+=email_text
                    self.DB=pd.concat([self.DB,new_row])
                    new_data=True

        if new_data==False:
            return "no new data"
        ##visulaization and saving
        ## order by date, by columns, find mean & STD, change names of columns, save to excel files
        columns = ['Patient','Date - Time','Eye','Device', 'ScanID','Session', 'Scan Ver', 'VG Ver','VG_output','checked_for_alerts',
                   'MeanBMsiVsr','Vmsi', 'MaxBMsiVsr','AdjustmentTime','RasterTime', 'TotalScanTime', 'NumValidLines','NumValidBatchReg',
                   'VsrRemoveOutFOV', 'MeanGap', 'MaxGap','ClippedPrecent', 'RegCentX','RegCentY','RegRangeX','RegRangeY',
                   'RegStdX', 'RegStdY','MeanXCover', 'MeanRetinalThickness3*3', 'MeanRetinalThicknessCST',
                   'MeanRetinalThicknessNIM', 'MeanRetinalThicknessTIM', 'MeanRetinalThicknessSIM',
                   'MeanRetinalThicknessIIM','x_long_shift','y_long_shift','Compliance','TimeOut','Alert_for_clipped','88+ Class 1',
               'Full Scan(88)', '# Class 1', '# Class 2', '# Class 3', '% Class 1', '% Class 2',
               '% Class 3','Scan']
        try:
            self.DB=self.DB[columns]
        except:
            return 'no new data'

        self.DB=self.DB.sort_values(by='Date - Time')
        self.final_DB = self.DB
        self.final_DB = self.final_DB.round(2)

        col = ['Patient', 'Date - Time', 'Eye', 'Scan Ver', 'VG Ver', 'VG_output', 'TimeOut', '88+ Class 1',
               'Full Scan(88)', '# Class 1', '# Class 2', '# Class 3', '% Class 1', '% Class 2',
               '% Class 3']
        self.ver3_DB = self.final_DB[col]
        self.ver3_DB.loc['Overall Mean'] = self.ver3_DB.mean()
        self.ver3_DB.loc['STD'] = self.ver3_DB.std()


        self.ver3_DB.fillna(-1, inplace=True)
        self.ver3_DB = self.ver3_DB.round(2)
        self.ver3_DB.to_excel(self.ver3_DB_path)

        self.final_DB.fillna(-1, inplace=True)
        self.DB.loc['Overall Mean'] = self.DB.mean()
        self.DB.loc['STD'] = self.DB.std()
        self.DB.fillna(-1, inplace=True)
        self.DB = self.DB.round(2)
        self.DB.to_excel(self.analysis_summary_path)


        return self

    def extract_VG_data(self,scan,scan_path, new_row):
        vg_output=False
        vg_path = scan_path + r'/VolumeGenerator-V.3-CfgID-26'
        vg_new_path=scan_path + r'/VolumeGenerator19_3'
        if os.path.isdir(vg_path):
            vg_ver = 'Ver3'
            new_row.loc[0, 'VG Ver'] = vg_ver
            file_path = vg_path + r'/DB_Data/VG_scan.csv'
        elif os.path.isdir(vg_new_path):
            vg_ver = 'Ver3'
            new_row.loc[0, 'VG Ver'] = vg_ver
            file_path = vg_new_path + r'/DB_Data/VG_scan.csv'
            vg_path=vg_new_path
        else:
            vg_ver = 'Ver2.31'
            new_row.loc[0, 'VG Ver'] = vg_ver
            vg_path = scan_path + r'/VolumeGenerator19_2.3'
            file_path = vg_path + r'/DB_Data/VG_scan.csv'
            if not os.path.isfile(file_path):
                file_path = vg_path + r'/DB_Data/scan.csv'
        try:
            curr_csv = pd.read_csv(file_path)
            data = curr_csv[['MeanBMsiVsr', 'Vmsi', 'MaxBMsiVsr', 'AdjustmentTime', 'RasterTime', 'TotalScanTime',
                             'NumValidLines', 'NumValidReg',
                             'QaVsrRemoveOutFOV', 'MeanGap', 'MaxGap', 'ClippedPrecent','RegCentX', 'RegCentY', 'RegRangeX', 'RegRangeY',
                             'RegStdX', 'RegStdY', 'MeanXCover', 'MeanRetinalThickness3*3', 'MeanRetinalThicknessCST',
                             'MeanRetinalThicknessNIM', 'MeanRetinalThicknessTIM', 'MeanRetinalThicknessSIM',
                             'MeanRetinalThicknessIIM']]
            data.rename(columns={'NumValidReg': 'NumValidBatchReg', 'QaVsrRemoveOutFOV': 'VsrRemoveOutFOV', },
                           inplace=True)
            data.loc[0,'Patient'] = self.patient_ID
            new_row.loc[0, 'VG_output'] = 1
            vg_output=True


        except:
            try:
                status=check_vg_status(vg_path)
                if status=='running':
                    new_row.loc[0, 'VG_output'] = 2 #still running
                elif status=='1':
                    print (scan+': VG success, check for other error')
                    new_row.loc[0, 'VG_output'] = 1
                    vg_output = True
                elif status=='0':
                    print (scan+': VG early stop because of VG error')
                    new_row.loc[0, 'VG_output'] = 0
                elif status=='2':
                    print (scan+': VG early stop because of input error or registration reference problem')
                    new_row.loc[0, 'VG_output'] = 0
                elif status=='3':
                    print (scan+': Exit current VG process and later rerun VG by analyzer - ILM RPE memory error')
                    new_row.loc[0, 'VG_output'] = 0
                elif status=='4':
                    print (scan+': Full process completed with problem notification')
                    new_row.loc[0, 'VG_output'] = 0
                return vg_output,new_row
            except:
                print ('Unexpected error with VG for scan'+ scan)
                new_row.loc[0, 'VG_output'] = 0
                self.DB = pd.concat([self.DB, new_row])
                return vg_output,new_row

        new_row.loc[0, 'Alert_for_clipped'] = self.check_clipped_param(scan,vg_path)
        ## if no VG output, concat current row and move to next scan
        new_row = new_row.merge(data, left_on='Patient', right_on='Patient', copy=False)

        try:
            VG_Bscan_VSR = vg_path+'/DB_Data/VG_Bscan_VSR.csv'
            curr_csv = pd.read_csv(VG_Bscan_VSR)
            data = curr_csv['ClassType']
            new_row = analysis_88(new_row, data)

        except:
            print('No VG_Bscan_VSR.csv file for ' + file_path)

        #self.DB = pd.concat([self.DB, new_row])
        return vg_output,new_row

    def check_clipped_param(self,scan, vg_path):
        clipped_path = vg_path + r'/DB_Data/VG_Bscan.csv'
        try:
            VG_Bscan = pd.read_csv(clipped_path)
        except:
            print('No VG_Bscan file for scan ' + scan)
            return -1
        try:
            clipped_data = VG_Bscan[['RastIndex', 'BatchIndex', 'ClippedPrecent', 'IsClipped']]
            high_clipped_per=clipped_data[clipped_data['ClippedPercent']>5]
            batch_list=high_clipped_per['BatchIndex'].values
            for ind,val in enumerate(batch_list,0): ##from sub batch to batch
                if val%2==1:
                    batch_list[ind]+=1
                batch_list[ind]=batch_list[ind]/2
            batch_set=set(batch_list) ##get unique
            if len(batch_set)>=2 and len(batch_list)>=10:
                return 1
            else:
                return 0
        except:
            print ('error in reading VG_Bscan '+ scan)
            return -1


def analysis_88(new_row_ver3,data):
    length=len(data)
    class1=sum(data==1)
    new_row_ver3.loc[0, '# Class 1']=class1
    new_row_ver3.loc[0, '# Class 2'] = sum(data == 2)
    new_row_ver3.loc[0, '# Class 3'] = sum(data == 3)
    new_row_ver3.loc[0, '% Class 1'] = sum(data == 1)/length*100
    new_row_ver3.loc[0, '% Class 2'] = sum(data == 2) / length * 100
    new_row_ver3.loc[0, '% Class 3'] = sum(data == 3) / length * 100
    new_row_ver3.loc[0, 'Full Scan(88)'] = int((length>=88))
    over88=0
    if class1>=88:
        over88=1
    new_row_ver3.loc[0, '88+ Class 1']=over88
    return new_row_ver3



