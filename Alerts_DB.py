import pyodbc
import os
import pandas as pd
import pickle
import copy
import math
import datetime
from datetime import date



conn = pyodbc.connect('Driver={SQL Server};'
                      'Server=172.30.2.177;'
                      'Database=OCTanalysisBackupForTesting;'
                      'uid=shiri_almog;pwd=shiri@123')
cursor = conn.cursor()

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

    def check_for_alerts(self, patient, new_row, scan_path):
        email_text = ''
        alerts_object = patient.alerts
        # alerts_object=alerts_object.check_if_outdated()
        alerts = alerts_object.alert_dic

        e = patient.eye
        date = new_row['Date - Time'].values[0]
        date=pd.to_datetime(date, format='%Y-%m-%d-%H-%M-%S')
        if new_row['VG_output'].values[0] == 0 or new_row['VG_output'].values[0] == 2:
            email_text += ('No VG output in the last scan: \nScan Date: ' + str(new_row['Date - Time'].values[0])
                           + ', Scan ID: ' + str(new_row['ScanID'].values[0][:-1]) + '\n' + scan_path + '\n' + '\n')
            cursor.execute(
                "INSERT INTO ALERTS(PatientID,Eye, Date, ScanID, AlertParam,ParamValue,AlertSent,Outdated) VALUES (?,?,?,?,?,?,?,?)",patient.patient_ID,e,date,4953, 'VG_output', 0, 0,0)
            conn.commit()
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
                    try:
                        cursor.execute(
                            "INSERT INTO ALERTS(PatientID,Eye, Date, ScanID, AlertParam,ParamValue,AlertSent,Outdated) VALUES (?,?,?,?,?,?,?,?)",
                            patient.patient_ID, e, date, 4953, param, new_row[param].values[0]==np.nan, 0, 0)
                        conn.commit()
                    except:
                        print ('Could not add alert {},{} to DB'.format(param, new_row[param].values[0]==np.nan))


                    continue

        if new_row['Alert_for_clipped'].values[0] == 1:
            email_text += ('High percentage of clipped Bscans in the last scan: \nScan Date: ' + str(
                new_row['Date - Time'].values[0])
                           + ', Scan ID: ' + str(new_row['ScanID'].values[0][:-1]) + '\n' + scan_path + '\n' + '\n')

        if new_row['TimeOut'].values[0] == 1:
            email_text += ('Timeout reported in the last scan: \nScan Date: ' + str(new_row['Date - Time'].values[0])
                           + ', Scan ID: ' + str(new_row['ScanID'].values[0][:-1]) + '\n' + scan_path + '\n' + '\n')
        cursor.execute(
            "INSERT INTO ALERTS(PatientID,Eye, Date, ScanID, AlertParam,ParamValue,AlertSent,Outdated) VALUES (?,?,?,?,?,?,?,?)",
            patient.patient_ID, e, date, 4953, 'Timeout', 1, 0, 0)
        conn.commit()


        if email_text != '':
            with open(self.text_file, 'a') as f:
                f.writelines('\n({})'.format(e) + email_text)
        return email_text, new_row