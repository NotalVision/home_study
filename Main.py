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
from Utils import merge_eye_excels,send_email_func,my_logger
import sys
import pytz
#from long_shift import long_shift_DB


if __name__ =="__main__":
    while True:
        start_time = time.time()
        env=os.environ._data['COMPUTERNAME'] #to run both locally and on the cloud
        if 'V-S-G' in env:
            network='V-S-G-RNDSTORE'
            host='Cloud'
        else:
            network='nv-nas01'
            host = 'Local Host'
        data_folder = r'\\{}\Home_OCT_Repository\Clinical_studies\Notal-Home_OCT_study-box3.0\Study_at_home\Data'.format(network)
        logger=my_logger(os.path.join(data_folder,'logger'))
        config_path = os.path.join(data_folder, 'mailing_list.txt')
        with open(config_path) as f:
            mailing_list = [i.strip() for i in f.readlines()]
        #patients = ['NH02001','NH02002','NH02003','Jason1004']
        patients = ['Jason1004']
        send_email=True
        mailing_list_path = os.path.join(data_folder, 'mailing_list.txt')
        with open(mailing_list_path) as f:
            mailing_list = [i.strip() for i in f.readlines()] # separate text into list items
        #patients = ['NH02001','NH02002','NH02003']
        patients = ['Jason1004']
        send_email=True # can change to false if only want to generate plots

        # this variable is used to determine if any new data arrived today. The last day of data arrival is saved in a text file in data folder
        # when new data arrives from any of the patients, this will be updated to true and the the text file will be updated with
        # the date of data arrival.
        all_patients_new_data=False
        for patientID in patients:
            total_DB=[]
            patient_new_data=False  # will be used to update 'all_patients_new_data'
            # get timezone
            patient_config_path = os.path.join(data_folder, patientID,'config.txt')
            with open(patient_config_path) as f:
                set_tz = f.readlines()
                set_tz=set_tz[0][10:]
            for eye in ['R','L']:
                new_patient = Patient(data_folder, patientID,eye,logger) #create new patient object - if DB/alerts exist for this patient - load them.
                new_patient,new_data=new_patient.full_analysis(host,logger)  # check for new scans
                if new_data==True:
                    patient_new_data=True

                try:
                    total_DB.append(new_patient.final_DB)  ## want to create one DB for both eyes
                except:
                    continue


                if send_email and new_patient.email_text!='': #email text will be empty if there are not alerts
                    email_text=new_patient.email_text
                    msg_subject= 'Attention: Patient {}, {} ({})'.format(patientID,eye,host) #title
                    send_email_func(email_text,mailing_list,msg_subject)


            if len(total_DB)==0: # no new scans in both eyes --> no need to update DB/plots
                continue
            elif len(total_DB)==1: # new scans only in left eye or right eye --> change from [DB] to DB
                total_DB = total_DB[0]
            elif len(total_DB)==2: # new scans in both eyes --> concat left and right, change from [right_DB, left_DB] to DB
                total_DB = pd.concat([total_DB[0], total_DB[1]])

            total_DB = total_DB.sort_values(by='Date - Time')

            try:
                total_DB.to_excel(os.path.join(data_folder, 'DB', '{}_DB.xlsx'.format(new_patient.patient_ID)))
                total_DB.to_excel(new_patient.DB_path)
            except: ## in case this is open by another user
                print ('Could not save display DB- open by another user ')

            ## merge left and right DB
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
            if patient_new_data==True:
                all_patients_new_data=True

        # if no data received from any of the patients, check when was the last date data was received
        if all_patients_new_data==False:
            with open(os.path.join(data_folder, 'last_Scan_date.txt'), 'r') as f:
                last_scan_date = f.readlines()
                last_scan_date = datetime.strptime(last_scan_date[0], '%Y-%m-%d')
                last_scan_date = last_scan_date.date()
                today = datetime.now(pytz.timezone("{}".format(set_tz)))
                if eye == 'L' and (today.date() - last_scan_date).days >= 2:
                    yesterday = (today - timedelta(1)).date()
                    email_text = 'No scans were received from any of the patients on {}'.format(yesterday)
                    msg_subject = 'Attention: No incoming scans on {}'.format(yesterday)
                    send_email_func(email_text, mailing_list, msg_subject)


        # update date of last scan in both cases - if new data arrived or  if email was sent
        with open(os.path.join(data_folder, 'last_Scan_date.txt'), 'w') as f:
            today = datetime.now(pytz.timezone("{}".format(set_tz)))
            f.write(str(today.date()))

        print (time.asctime(time.localtime(time.time())))
        print ('elapsed_time=',time.time() - start_time)
        print ('mojo')
        time.sleep(300)