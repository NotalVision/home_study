import pandas as pd
import numpy as np
import os
from os import path
from datetime import date
import scipy.io as sio
from email.message import EmailMessage
import smtplib
import csv
import pickle
import datetime
from datetime import date
import time
import copy
import math


class Alert:
    def __init__(self,patient):
        self.patient=patient.patient_ID
        self.path=patient.analysis_folder+'/Alerts'
        if not os.path.isdir(self.path):
            os.mkdir(self.path)
        self.eye=patient.eye
        self.text_file=patient.analysis_folder+'/Alerts/{}_Alert_History'.format(patient.patient_ID)
        if not os.path.isfile(self.text_file):
            with open(self.text_file,'w') as f:
                f.writelines('Alert History for patient '+patient.patient_ID)
        self.params_path = os.path.join(self.path, 'Alerts_params.xlsx')
        self.params_dic={}
        if os.path.isfile(self.params_path):
            a=pd.read_excel(self.params_path)
            for ind,param in a.iterrows():
                row=param.T
                if row.T[0] in self.params_dic.keys():
                    count=len(self.params_dic[row.T[0]])
                    self.params_dic[row.T[0]].update({count: [row.T[2], row.T[3], row.T[4]]})
                else:
                    self.params_dic[row.T[0]]= {0:[row.T[2],row.T[3],row.T[4]]}


    def load_existing(self):
        try:
            with open(self.path + '/alerts.pkl', 'rb') as f:
                self.alert_dic=pickle.load(f)
                return self
        except:
            return self.create_new()

    def create_new(self):
        #alert_types=['long_x_shift', 'long_y_shift', 'class_1','RegStdX','RegStdY','MaxGap']
        alert_types=list(self.params_dic.keys())


        eye = ['L', 'R']

        partition_by_alert = dict(zip(alert_types, [dict() for i in alert_types]))
        for alert in alert_types:
            for i in range(len(self.params_dic[alert])):
                partition_by_alert[alert][i]=dict()

        self.alert_dic = dict(zip(eye, [copy.deepcopy(partition_by_alert) for i in eye]))
        with open(self.path + '/alerts.pkl', 'wb') as f:
            pickle.dump(self.alert_dic, f, pickle.HIGHEST_PROTOCOL)

        return self

    def check_for_alerts(self,patient, new_row,scan_path):
        email_text = ''
        alerts_object=patient.alerts
        #alerts_object=alerts_object.check_if_outdated()
        alerts = alerts_object.alert_dic

        e = patient.eye
        date = new_row['Date - Time'].values[0]
        if new_row['VG_output'].values[0] ==0 or new_row['VG_output'].values[0] ==2:
            email_text += ('No VG output in the last scan: \nScan Date: '+ str(new_row['Date - Time'].values[0])
                           +', Scan ID: '+ str(new_row['ScanID'].values[0][:-1]) +'\n'+ scan_path+'\n'+'\n')
            return email_text, new_row


        for param in list(alerts[e].keys()):
            for param_sec in list(alerts[e][param].keys()):
                if math.isnan(self.params_dic[param][param_sec][0]):
                    high_or_low='high'
                else:
                    high_or_low='low'
                if (abs(new_row[param].values[0]) < self.params_dic[param][param_sec][0]) or (abs(new_row[param].values[0]) > self.params_dic[param][param_sec][1]):
                    alerts[e][param][param_sec][date] = ('Scan Date: ' + str(new_row['Date - Time'].values[0]) + ', Scan ID: ' + str(new_row['ScanID'].values[0][:-1]) + '\n'+ param +': '+ str(
                                new_row[param].values[0]) + '\n' + scan_path + '\n')
                    if len(alerts[e][param][param_sec]) >= self.params_dic[param][param_sec][2]:
                        if self.params_dic[param][param_sec][2]==1:
                            email_text += '{} was {} in the last scan:'.format(param,high_or_low) + '\n'
                        else:
                            email_text += '{} was {} in the last {} scans:'.format(param,high_or_low,self.params_dic[param][param_sec][2]) + '\n'
                        for i in alerts[e][param][param_sec]:
                            email_text += str(alerts[e][param][param_sec][i])
                        email_text += '\n'
                        alerts[e][param][param_sec] = {}

        # if abs(new_row['# Class 1'].values[0]) <=70:
        #     alerts[e]['class_1'][date]=('Scan Date: '+ str(new_row['Date - Time'].values[0]) +
        #                                      ', Scan ID: '+ str(new_row['ScanID'].values[0][:-1]) + '\n# Class 1 bscans: ' + str(new_row['# Class 1'].values[0]) + '\n'+scan_path+'\n')
        #     if len(alerts[e]['class_1']) >= 2:
        #         email_text += '# Class 1 Bscans was low in the last 2 scans:' + '\n'
        #         for i in alerts[e]['class_1']:
        #             email_text += str(alerts[e]['class_1'][i])
        #         email_text+='\n'
        #         alerts[e]['class_1'] = {}
        # if abs(new_row['RegStdX'].values[0]) >300:
        #     alerts[e]['RegStdX'][date]=('Scan Date: '+ str(new_row['Date - Time'].values[0]) +
        #                                      ', Scan ID: '+ str(new_row['ScanID'].values[0][:-1]) + '\nRegSTD_X: ' + str(new_row['RegStdX'].values[0]) + 'um \n'+scan_path+'\n')
        #     if len(alerts[e]['RegStdX']) >= 2:
        #         email_text += 'RegSTD in the X axis was high in 2 of the last scans:' + '\n'
        #         for i in alerts[e]['RegStdX']:
        #             email_text += str(alerts[e]['RegStdX'][i])
        #         email_text+='\n'
        #         alerts[e]['RegStdX'] = {}
        # if abs(new_row['RegStdY'].values[0]) >300:
        #     alerts[e]['RegStdY'][date]=('Scan Date: '+ str(new_row['Date - Time'].values[0]) +
        #                                      ', Scan ID: '+ str(new_row['ScanID'].values[0][:-1]) + '\nRegSTD_Y: ' + str(new_row['RegStdY'].values[0]) + 'um \n'+scan_path+'\n')
        #     if len(alerts[e]['RegStdY']) >= 2:
        #         email_text += 'RegSTD in the Y axis was high in 2 of the last scans:' + '\n'
        #         for i in alerts[e]['RegStdY']:
        #             email_text += str(alerts[e]['RegStdY'][i])
        #         email_text+='\n'
        #         alerts[e]['RegStdY'] = {}
        # if abs(new_row['MaxGap'].values[0]) >250:
        #     alerts[e]['MaxGap'][date]=('Scan Date: '+ str(new_row['Date - Time'].values[0]) +
        #                                      ', Scan ID: '+ str(new_row['ScanID'].values[0][:-1]) + '\nMaxGap: ' + str(new_row['MaxGap'].values[0]) + '\n'+scan_path+'\n')
        #     if len(alerts[e]['MaxGap']) >= 2:
        #         email_text += 'Max gap was high in 2 of the last scans:' + '\n'
        #         for i in alerts[e]['MaxGap']:
        #             email_text += str(alerts[e]['MaxGap'][i])
        #         email_text+='\n'
        #         alerts[e]['MaxGap'] = {}
        #
        # if new_row['MeanBMsiVsr'].values[0] < 2:
        #     email_text += ('Low MSI detected in the last scan: \nScan Date: '+ str(new_row['Date - Time'].values[0])
        #                    +', Scan ID: '+ str(new_row['ScanID'].values[0][:-1]) + '\nMSI: ' + str(new_row['MeanBMsiVsr'].values[0]) +'\n'+ scan_path+'\n'+'\n')
        # if new_row['Vmsi'].values < 2:
        #     email_text += ('Low Vmsi detected in the last scan: \nScan Date: '+ str(new_row['Date - Time'].values[0])
        #                    +', Scan ID: '+ str(new_row['ScanID'].values[0][:-1]) + '\nVmsi: ' + str(new_row['Vmsi'].values[0])  +'\n'+ scan_path+'\n'+'\n')
        # if new_row['NumValidLines'].values[0] <88:
        #     email_text += ('Low # Bscans detected in the last scan: \nScan Date: '+ str(new_row['Date - Time'].values[0])
        #                    +', Scan ID: '+ str(new_row['ScanID'].values[0][:-1]) + '\n# Bscans: ' + str(new_row['NumValidLines'].values[0])  +'\n'+ scan_path+'\n'+'\n')
        # if new_row['# Class 1'].values[0] <50:
        #     email_text += ('# Class 1 Bscans was low in the last scan: \nScan Date: '+ str(new_row['Date - Time'].values[0])
        #                    +', Scan ID: '+ str(new_row['ScanID'].values[0][:-1]) + '\n# Class 1 Bscans: ' + str(new_row['# Class 1'].values[0])  +'\n'+ scan_path+'\n'+'\n')
        if new_row['Alert_for_clipped'].values[0] ==1:
            email_text += ('High percentage of clipped Bscans in the last scan: \nScan Date: '+ str(new_row['Date - Time'].values[0])
                           +', Scan ID: '+ str(new_row['ScanID'].values[0][:-1]) +'\n'+ scan_path+'\n'+'\n')

        if new_row['TimeOut'].values[0] ==1:
            email_text += ('Timeout reported in the last scan: \nScan Date: '+ str(new_row['Date - Time'].values[0])
                           +', Scan ID: '+ str(new_row['ScanID'].values[0][:-1]) +'\n'+ scan_path+'\n'+'\n')



        with open(patient.alerts.path + '/alerts.pkl', 'wb') as f:
            pickle.dump(alerts, f, pickle.HIGHEST_PROTOCOL)
        new_row.loc[0, 'checked_for_alerts'] = 1
        if email_text!='':
            with open(self.text_file, 'a') as f:
                f.writelines('\n({})'.format(e)+email_text )
        return email_text, new_row


    def check_if_outdated(self):
        today=date.today()
        days = datetime.timedelta(6)
        old_date = today - days
        alert_types=['long_x_shift', 'long_y_shift', 'class_1','RegStdX','RegStdY','MaxGap']
        eyes = ['L', 'R']
        to_remove=[]
        for eye in eyes:
            for param in list(self.alerts[e].keys()):
                for item in self.alert_dic[eye][type]:
                    tmp_item=datetime.datetime.strptime(item,'%Y-%m-%d-%H-%M-%S')
                    tmp_item=tmp_item.date()
                    if tmp_item<old_date:
                        to_remove.append([eye,type,item])

        for i in to_remove:
            self.alert_dic[i[0]][i[1]].pop(i[2])

        return self

