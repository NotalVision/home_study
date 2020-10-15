import os
from email.message import EmailMessage
import smtplib
import json
import time
from datetime import datetime,timedelta
from Class_Patient import Patient
from Analysis_Graphs import load_events,analysis_graphs
from ver3_graphs import ver3_create_graphs
from compliance_graph import compliance
import pandas as pd
from VG_88_bscans_analysis import class_ditrib1,class_distrib2
from datetime import date
import xlsxwriter
from Utils import merge_eye_excels,send_email_func
import sys
import pytz
#from long_shift import long_shift_DB





if __name__ =="__main__":
    while True:
        start_time = time.time()
        set_tz='utc'
        env=os.environ._data['COMPUTERNAME']
        if 'V-S-G' in env:
            network='V-S-G-RNDSTORE'
            host='Cloud'
        else:
            network='nv-nas01'
            host = 'Local Host'
        data_folder = r'\\{}\Home_OCT_Repository\Clinical_studies\Notal-Home_OCT_study-box3.0\Study_at_home\Data_testing'.format(network)
        config_path = os.path.join(data_folder, 'mailing_list.txt')
        with open(config_path) as f:
            mailing_list = [i.strip() for i in f.readlines()]
        patients = ['NH02001']#,'NH02002']
        send_email=True
        for patientID in patients:
            total_DB=[]
            for eye in ['R','L']:
                new_patient = Patient(data_folder, patientID,eye)
                new_patient=new_patient.full_analysis()
                if new_patient=='no new data':
                    with open(os.path.join(data_folder, 'last_Scan_date.txt'), 'r') as f:
                        last_scan_date = f.readlines()
                        last_scan_date=datetime.strptime(last_scan_date[0], '%Y-%m-%d')
                        last_scan_date=last_scan_date.date()
                        today = datetime.now(pytz.timezone("{}".format(set_tz)))
                        if eye=='L' and (today.date()-last_scan_date).days  >= 0:
                            yesterday = (today - timedelta(1)).date()
                            email_text = 'No scans were received from any of the patients on {}'.format(yesterday)
                            msg_subject = 'Attention: No incoming scans on {}'.format(yesterday)
                            send_email_func(email_text, mailing_list, msg_subject)
                            with open(os.path.join(data_folder, 'last_Scan_date.txt'), 'w') as f:
                                f.write(str(today.date()))
                    continue
                else: ##update date of last scan, to send alert if 36h passed without incoming scan
                    with open(os.path.join(data_folder, 'last_Scan_date.txt'), 'w') as f:
                        today=datetime.now(pytz.timezone("{}".format(set_tz)))
                        f.write(str(today.date()))
                total_DB.append(new_patient.final_DB) ## want to create one DB for both eyes

                ##check if 36h passed withoud incoming scan


                if send_email and new_patient.email_text!='':
                    email_text=new_patient.email_text
                    msg_subject= 'Attention: Patient {}, {} ({})'.format(patientID,eye,host)
                    send_email_func(email_text,mailing_list,msg_subject)

            if len(total_DB)==0: ## no scans in both eyes
                continue
            elif len(total_DB)==2:
                total_DB = pd.concat([total_DB[0], total_DB[1]]) ##left and right

            total_DB = total_DB.sort_values(by='Date - Time')
            try:
                total_DB.to_excel(new_patient.DB_path) ## in case this is open by another user
            except:
                total_DB.to_excel(new_patient.analysis_folder+'/DB/'+ patientID + '_DB_tmp.xlsx')

            ## merge
            merge_eye_excels(new_patient, '/{}_{}_ver3_class_data.xlsx', '{}_ver3_class_data.xlsx'.format(patientID))
            merge_eye_excels(new_patient, '/{}_{}_scan_quality_&_fixation.xlsx',
                             '{}_scan_quality_&_fixation.xlsx'.format(patientID))

            ## Create Graphs
            save_fig_path = os.path.join(data_folder, patientID, 'Analysis/Plots')
            if not os.path.isdir(save_fig_path):
                os.mkdir(save_fig_path)
            events_path = os.path.join(data_folder, patientID, 'CRF/Injections.xlsx')
            events, with_events = load_events(events_path)
            analysis_graphs(data_folder, patientID, save_fig_path, events, False)
            ver3_create_graphs(data_folder, patientID, save_fig_path, events, False)
            compliance(data_folder,patientID,save_fig_path,events)
            class_ditrib1(data_folder,new_patient)
            class_distrib2(data_folder,new_patient)
            #long_shift_DB(patientID,data_folder)


        print (time.asctime(time.localtime(time.time())))
        print ('elapsed_time=',time.time() - start_time)
        print ('mojo')
        time.sleep(300)