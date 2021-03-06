import pandas as pd
import numpy as np
import os
from Alerts import Alert
import pickle
pd.options.mode.chained_assignment = None
from DB_connection import check_if_downloaded
from Patient_Utils import check_vg_status,check_DN_status, check_if_timeout,analysis_88
import logging
import glob
from stat import S_ISREG, ST_CTIME, ST_MODE


class Patient:
    def __init__(self,data_folder, patientID,eye,logger):
        self.data_path=data_folder+'/'+patientID
        self.patient_ID=patientID
        self.eye=eye
        self.email_text=''
        self.analysis_folder=(data_folder +'/'+ patientID + '/Analysis')
        if not os.path.isdir(self.analysis_folder):
            os.mkdir(self.analysis_folder)
        self.DB_folder_path=os.path.join(data_folder,'DB','{}_DB.xlsx'.format(self.patient_ID))
        self.DB_path=os.path.join(self.analysis_folder,'{}_DB.xlsx'.format(self.patient_ID))
        self.DN_path=os.path.join(self.analysis_folder,'{}_DN_DB.xlsx'.format(self.patient_ID))
        self.ver3_DB_path=(self.analysis_folder+ '/'+ patientID + '_{}_ver3_class_data.xlsx'.format(eye))
        self.analysis_summary_path= (self.analysis_folder+ '/' + patientID+'_{}_scan_quality_&_fixation.xlsx'.format(eye))
        self.alert_template = Alert(self)
        if os.path.isfile(self.DB_folder_path):  #create new DB only if doesn't exist yet
            self.DB=pd.read_excel(self.DB_folder_path)
            self.DB=self.DB[self.DB['Eye']==eye]
            self.alerts=self.alert_template.load_existing()
            self.new=0
        else:
            self.new=1
            self.alerts=self.alert_template.create_new()
        if os.path.isfile(self.DN_path):
            self.DN_DB = pd.read_excel(self.DN_path)
            if not self.DN_DB.empty:
                self.DN_DB = self.DN_DB[self.DN_DB['Eye'] == eye]
        else:
            self.DN_DB = pd.DataFrame()

    def full_analysis(self,host,logger):
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

        isDownloaded = check_if_downloaded(host) # returns sessionID of downloaded sessions
        new_data = False
        for scan in scans_list:
            if 'TST' in scan:
                scan_path = self.data_path + '/' + self.eye + '/Hoct/' + scan
                data_sum = scan_path + '/DataSummary.txt'  ##get session_id and scan_id
                try:
                    with open(data_sum,'r') as f:
                        session_ID=f.readline()
                        scan_ID = f.readline()
                except:
                    ## if there is no Data summary file, download is not cmoplete, skip to next scan
                    continue

                if int(session_ID[12:-1]) in isDownloaded: # is scan is marked as downloaded in DB
                    new_row = pd.DataFrame(columns=columns_new_row) #create a new empty row that will be added to DB at the end
                    new_row.loc[0, 'Scan'] = scan_path
                    new_row.loc[0, 'TimeOut'] = check_if_timeout(scan_path)
                    new_row.loc[0, 'Compliance'] = 1
                    new_row.loc[0, 'checked_for_alerts']=0
                    new_row.loc[0, 'Patient'] = self.patient_ID
                    new_row.loc[0, 'Eye'] = self.eye
                    date_time = scan[-33:-14]
                    try:
                        #check if scan already in DB
                        if date_time in self.DB['Date - Time'].array:
                            try: #check if scan wad added to DN_DB (might be added to DB before DN was running)
                                vg_4_folder = os.path.join(scan_path, 'VolumeGenerator_4')
                                new_row.loc[0, 'Date - Time'] = date_time
                                if self.DN_DB.empty or (os.path.isdir(vg_4_folder) and date_time not in self.DN_DB['Date - Time'].array) :
                                    DN_new_row = self.extract_DeepNoa_data(scan,vg_4_folder, new_row)
                                    self.DN_DB = pd.concat([self.DN_DB, DN_new_row])
                                elif date_time in self.DN_DB['Date - Time'].array and self.DN_DB[self.DN_DB['Date - Time']==date_time]['DN_output'].values==0:
                                    DN_new_row = self.extract_DeepNoa_data(scan,vg_4_folder, new_row)
                                    self.DN_DB = pd.concat([self.DN_DB, DN_new_row])

                            except:
                                pass
                            # a scan may be added to DB if VG did not complete run
                            # In this case we want to run over it again, so need to check VG status
                            cur_row=self.DB[self.DB['Date - Time']==date_time] # cur_row will be the row in the current DB with the same date
                            cur_vg_output=cur_row['VG_output'].values[0]
                            if cur_vg_output==1 or cur_vg_output==0: #vg_output ==1: Success #vg_output ==0: Fail
                                continue
                            if cur_vg_output == 2: #vg_output ==2: not complete, need to run analysis again
                                #get vg_data for this row
                                vg_output, new_row = self.extract_VG_data(scan, scan_path, new_row)
                                continue
                    except:
                        pass

                    new_data=True
                    new_row.loc[0,'Date - Time']=date_time
                    device = scan[0:-34]
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
                    if vg_output == False: #send alert for no VG output
                        email_text, new_row = self.alerts.check_for_alerts(self, new_row, scan_path)
                        self.email_text += email_text
                        self.DB = pd.concat([self.DB, new_row])
                        continue


                    vg_4_folder = os.path.join(scan_path, 'VolumeGenerator_4')
                    if os.path.isdir(vg_4_folder):
                        DN_new_row = self.extract_DeepNoa_data(scan,vg_4_folder, new_row)
                        self.DN_DB = pd.concat([self.DN_DB, DN_new_row])

                    new_row.rename(columns={'MeanBMsiVsr': 'MSI'}, inplace=True)

                    ##~~~~~~~~~~Alerts~~~~ #####
                    # check_for_alerts() receives a new row and checks if need to send an alert about it
                    email_text,new_row=self.alerts.check_for_alerts(self,new_row,scan_path)
                    self.email_text+=email_text
                    self.DB=pd.concat([self.DB,new_row])


        ##visulaization and saving
        ## order by date, by columns, find mean & STD, change names of columns, save to excel files
        columns = ['Patient','Date - Time','Eye','Device', 'ScanID','Session', 'Scan Ver', 'VG Ver','VG_output','checked_for_alerts',
                   'MSI','Vmsi', 'MaxBMsiVsr','Max_BMSIAllRaw','% MSI<2','AdjustmentTime','RasterTime', 'TotalScanTime', 'NumValidLines','NumValidBatchReg',
                   'VsrRemoveOutFOV', 'MeanGap', 'MaxGap','ClippedPrecent', '# of bscans clipped>0','# of bscans clipped>5',
                    'RegCentX','RegCentY','RegRangeX','RegRangeY',
                   'RegStdX', 'RegStdY','MeanXCover', 'MeanRetinalThickness3*3', 'MeanRetinalThicknessCST',
                   'MeanRetinalThicknessNIM', 'MeanRetinalThicknessTIM', 'MeanRetinalThicknessSIM',
                   'MeanRetinalThicknessIIM','x_long_shift','y_long_shift','Compliance','TimeOut','Alert_for_clipped','88+ Class 1',
               'Full Scan(88)', '# Class 1', '# Class 2', '# Class 3', '% Class 1', '% Class 2',
               '% Class 3','Scan']
        DN_columns=['Patient','Date - Time','Eye','DN_output','DN_Success','DN_ver','SrfVolume Class','IrfVolume Class','FluidVolume Class','ClassScoreFluid','Classifier Fluid Decision',
                    'Fluid Volume No Class','Fluid Decision No Class','EligibleQuant','MSI','MaxGap VG','MaxGapQuant',
                    '# Bscans in VS','# Bscans Valid for Quant','x_long_shift','y_long_shift','Scan']

        try:
            self.DN_DB = self.DN_DB[DN_columns]
        except:
            pass

        try:
            self.DB=self.DB[columns] #organizes DB by columns order above
            #this will give an error if one of the rows does not exist, or if there is no new data
        except:
            return self,new_data

        self.save_one_eye_excels()


        return self,new_data

    def save_one_eye_excels(self):
        '''
        This functions receives the total DB of a single eye and saves 2 excel sheets:
        1. ver3_DB - containing the data for the class distribution
        2. Total DB with mean and STD calculations
        '''
        self.DB = self.DB.sort_values(by='Date - Time')
        self.final_DB = self.DB
        self.final_DB = self.final_DB.round(2)

        col = ['Patient', 'Date - Time', 'Eye', 'Scan Ver', 'VG Ver', 'VG_output', 'TimeOut', '88+ Class 1',
               'Full Scan(88)', '# Class 1', '# Class 2', '# Class 3', '% Class 1', '% Class 2',
               '% Class 3','# of bscans clipped>0','# of bscans clipped>5']
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
        #self.DN_DB.to_excel(self.DN_path)

    def extract_VG_data(self,scan,scan_path, new_row):
        vg_output=False

        #want to get VG folder that was created first
        earliest_date=100000000000
        vg_folder='Not Found'
        for name in glob.glob(scan_path + r'/VolumeGenerator*'): # find all folder names with 'VolumeGenerator'
            stat=os.stat(name) #get the time folder was created
            date=stat[ST_CTIME]
            if date<earliest_date:
                earliest_date=date
                vg_folder=name

        #vg_folder = scan_path + r'/VolumeGenerator_4'
        if vg_folder=='Not Found':
            new_row.loc[0, 'VG_output'] = 0
            return vg_output,new_row
        else:
            vg_path = vg_folder
            vg_ver_loc = str.find(vg_folder,'VolumeGenerator')
            vg_ver=vg_folder[vg_ver_loc+15:]
            new_row.loc[0, 'VG Ver'] = vg_ver
            file_path = vg_folder+r'/DB_Data/VG_scan.csv'
            if not os.path.isfile(file_path):
                file_path = vg_folder + r'/DB_Data/scan.csv' # in some older versions
            vg_bscan_path=vg_folder+r'/DB_Data/VG_Bscan.csv'



        try:
            #get data from VG_scan file, save it in 'data' - a pd object. Note - it is different than 'new_row'. they will be concatenated later
            curr_csv = pd.read_csv(file_path)
            data = curr_csv[['MeanBMsiVsr', 'Vmsi', 'MaxBMsiVsr', 'AdjustmentTime', 'RasterTime', 'TotalScanTime',
                             'NumValidLines', 'NumValidReg',
                             'QaVsrRemoveOutFOV', 'MeanGap', 'MaxGap', 'ClippedPrecent',
                             'RegCentX', 'RegCentY', 'RegRangeX', 'RegRangeY',
                             'RegStdX', 'RegStdY', 'MeanXCover', 'MeanRetinalThickness3*3', 'MeanRetinalThicknessCST',
                             'MeanRetinalThicknessNIM', 'MeanRetinalThicknessTIM', 'MeanRetinalThicknessSIM',
                             'MeanRetinalThicknessIIM']]
            data.rename(columns={'NumValidReg': 'NumValidBatchReg', 'QaVsrRemoveOutFOV': 'VsrRemoveOutFOV', 'MeanBMsiVsr':'MSI'},
                           inplace=True)
            data.loc[0,'Patient'] = self.patient_ID
            vg_bscan = pd.read_csv(vg_bscan_path)
            data.loc[0, 'Max_BMSIAllRaw'] = max(vg_bscan['BMSIAllRaw'].values)
            msi_list=vg_bscan['BMSIAllRaw'].values
            len_msi_list=len(msi_list)
            msi_list_lower_than2=msi_list[msi_list<2]
            msi_lower_than2=len(msi_list_lower_than2)/len_msi_list*100
            data.loc[0, '% MSI<2']=msi_lower_than2

            new_row.loc[0, 'VG_output'] = 1
            vg_output=True

        except:
            #if the file does not contain all the rows above - may be a VG error, check which one
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
                return vg_output,new_row


        alert_for_clipped,num_clipped_above_0,num_clipped_above_5=self.check_clipped_param(scan,scan_path,vg_path)
        new_row.loc[0, 'Alert_for_clipped'] = alert_for_clipped
        new_row.loc[0, '# of bscans clipped>0'] = num_clipped_above_0
        new_row.loc[0, '# of bscans clipped>5'] = num_clipped_above_5

        ## concat current row and data
        new_row = new_row.merge(data, left_on='Patient', right_on='Patient', copy=False)

        try:
            VG_Bscan_VSR = vg_path+'/DB_Data/VG_Bscan_VSR.csv'
            curr_csv = pd.read_csv(VG_Bscan_VSR)
            data = curr_csv['ClassType']
            new_row = analysis_88(new_row, data)

        except:
            try:
                VG_Bscan_VSR = scan_path + r'/VolumeGenerator_3/DB_Data/VG_Bscan_VSR.csv'
                curr_csv = pd.read_csv(VG_Bscan_VSR)
                data = curr_csv['ClassType']
                new_row = analysis_88(new_row, data)
            except:
                print('No VG_Bscan_VSR.csv file for ' + file_path)

        #self.DB = pd.concat([self.DB, new_row])
        return vg_output,new_row

    def check_clipped_param(self,scan, scan_path,vg_path):
        '''
        This function reads the VG Bscan file, check is alert needs to be sent
        criterion for alert: more than 10 bscans (in more than one batch) that have 5+ % bscans clipped
        :return:
        0/1 - need to send an alert (0 - No, 1 - Yes)
        num_clipped_above_0: # of clipped bscans that are clipped
        num_clipped_above_5 # of clipped bscans that are more than 5% clipped
        This is added to DB and used for plot
        '''
        clipped_path = vg_path + r'/DB_Data/VG_Bscan.csv'
        try:
            VG_Bscan = pd.read_csv(clipped_path)
        except:
            print('No VG_Bscan file for scan ' + scan)
            return -1,-1,-1
        try:
            clipped_data = VG_Bscan[['RastIndex', 'BatchIndex', 'ClippedPercent', 'IsClipped','InVs']]
            clipped_data=clipped_data[clipped_data['InVs']==1] # Only take bscans that were chosen to be in final 88

        except:
            #handle older versions
            try:
                clipped_path = scan_path + r'/VolumeGenerator_3/DB_Data/VG_Bscan.csv'
                VG_Bscan = pd.read_csv(clipped_path)
                clipped_data = VG_Bscan[['RastIndex', 'BatchIndex', 'ClippedPercent', 'IsClipped','InVs']]
                clipped_data = clipped_data[clipped_data['InVs'] == 1]
            except:
                print('error in reading VG_Bscan ' + scan)
                logging.info('error in reading VG_Bscan ' + scan)
                return -1, -1, -1

        num_clipped_above_0=len(clipped_data[clipped_data['ClippedPercent']>0])
        num_clipped_above_5 = len(clipped_data[clipped_data['ClippedPercent'] > 5])

        # check for alert

        high_clipped_per=clipped_data[clipped_data['ClippedPercent']>5]
        batch_list=high_clipped_per['BatchIndex'].values
        # we want to check for 10 cases in differnt batches. csv file shows sub batch so need to convert
        # i.e. 1+2 become 1. 3+4 become 2 etc
        for ind,val in enumerate(batch_list,0):
            if val%2==1:
                batch_list[ind]+=1
            batch_list[ind]=batch_list[ind]/2
        batch_set=set(batch_list) ##get unique
        if len(batch_set)>=2 and len(batch_list)>=10: #need to send alert
            return 1,num_clipped_above_0,num_clipped_above_5
        else:
            return 0,num_clipped_above_0,num_clipped_above_5

    def extract_DeepNoa_data(self,scan,vg_folder, new_row):
        VG_Scan_path = os.path.join(vg_folder,'DB_Data','VG_Scan.csv')
        if not os.path.isfile(VG_Scan_path):
            print ('No VG_scan file for scan {}'.format(vg_folder))
            new_row.loc[0, 'DN_output'] = 0
            new_row.loc[0, 'DN_Success'] = 0

            return new_row
        try:
            VG_Scan = pd.read_csv(VG_Scan_path)
            new_row.loc[0, 'x_long_shift'] = VG_Scan['LongiRegShiftX'].values[0]
            new_row.loc[0, 'y_long_shift'] = VG_Scan['LongiRegShiftY'].values[0]
            new_row.loc[0, 'MSI'] = VG_Scan['MeanBMsiAll'].values[0]
            new_row.loc[0, 'MaxGap VG'] = VG_Scan['MaxGap'].values[0]

        except:
            print('Cant get long shift data')
            new_row.loc[0, 'DN_output'] = 0
            new_row.loc[0, 'DN_Success'] = 0
            return new_row

        # Find DN folder
        try:
            DN_folders=glob.glob(vg_folder + r'/DeepNoa*')
            DN_folder=DN_folders[0]
            new_row.loc[0, 'DN_ver']=1.2
            if not os.path.isdir(DN_folder):
                new_row.loc[0, 'DN_output'] =0
                return new_row
        except:
            new_row.loc[0, 'DN_output'] = 0
            new_row.loc[0, 'DN_Success'] = 0
            return new_row
        DN_scan_path = DN_folder+r'/DB_Data/DN_scan.csv'
        DN_Bscan_VSR_path = DN_folder + r'/DB_Data/DN_Bscan_VSR.csv'
        DN_Bscan_Quant_path = DN_folder + r'/DB_Data/DN_Bscan_Quant.csv'

        try:
            curr_csv = pd.read_csv(DN_scan_path)
            data = curr_csv[['WithFluid','SrfVolumeNl','IrfVolumeNl','FluidVolumeNl','ClassScoreFluid','EligibleQuant','MaxGapQuant']]
            data.rename(columns={'SrfVolumeNl': 'SrfVolume Class', 'IrfVolumeNl': 'IrfVolume Class',
                                 'FluidVolumeNl': 'FluidVolume Class'},
                        inplace=True)
            seg_fluid_volume=curr_csv['FluidVolumeNoClassNl'].values
            data.loc[0, 'Fluid Volume No Class'] = seg_fluid_volume
            if seg_fluid_volume>0:
                data.loc[0, 'Fluid Decision No Class'] =1
            else:
                data.loc[0, 'Fluid Decision No Class'] = 0
            data.rename(columns={'WithFluid': 'Classifier Fluid Decision'}, inplace=True)
            data.loc[0,'Patient'] = self.patient_ID
            new_row.loc[0, 'DN_output'] = 1
            new_row = new_row.merge(data, left_on='Patient', right_on='Patient', copy=False)

            curr_csv = pd.read_csv(DN_Bscan_VSR_path)
            new_row.loc[0, '# Bscans in VS'] = len(curr_csv)

            curr_csv = pd.read_csv(DN_Bscan_Quant_path)
            new_row.loc[0, '# Bscans Valid for Quant'] = len(curr_csv)
        except:
            new_row.loc[0, 'DN_output'] = 0
            new_row.loc[0, 'DN_Success'] = 0

        try:
            status = check_DN_status(DN_folder)
            if status == 'running':
                new_row.loc[0, 'DN_output'] = 2  # still running
                new_row.loc[0, 'DN_Success'] = 0
            elif status == '1':
                print(scan + ': DN success, check for other error')
                new_row.loc[0, 'DN_Success'] = 1
            elif status == '0':
                print(scan + ': VG early stop because of VG error')
                new_row.loc[0, 'DN_Success'] = 0
            elif status == '2':
                print(scan + ': VG early stop because of input error or registration reference problem')
                new_row.loc[0, 'DN_Success'] = 0
            elif status == '3':
                print(scan + ': Exit current VG process and later rerun VG by analyzer - ILM RPE memory error')
                new_row.loc[0, 'DN_Success'] = 0
            elif status == '4':
                print(scan + ': Full process completed with problem notification')
                new_row.loc[0, 'DN_Success'] = 0

        except:
            print('Unexpected error with VG for scan' + scan)
            new_row.loc[0, 'DN_Success'] = 0


        return new_row







