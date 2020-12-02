import pandas as pd
import xlsxwriter
import os
import smtplib
from email.message import EmailMessage
import logging
import sys
import numpy as np

def merge_eye_excels(new_patient,path,new_path):
    '''
    Input: path of 2 excels, one for each eye
    Saves one excel with two tabs, one for each eye
    Deletes Input files
    '''
    path_str=new_patient.analysis_folder+path
    left_ver_db = pd.read_excel(path_str.format(new_patient.patient_ID,'L'))
    right_ver_db = pd.read_excel(path_str.format(new_patient.patient_ID,'R'))
    writer = pd.ExcelWriter(new_patient.analysis_folder +'/'+ new_path, engine='xlsxwriter')
    left_ver_db.to_excel(writer, sheet_name='L')
    right_ver_db.to_excel(writer, sheet_name='R')
    try:
        writer.save()
    except xlsxwriter.exceptions.FileCreateError as e:  ## in case somebody is viewing this file atm
        print(e)
    os.remove(path_str.format(new_patient.patient_ID,'L'))
    os.remove(path_str.format(new_patient.patient_ID,'R'))
    return

def send_email_func(email_text,mailing_list,msg_subject):
    s = smtplib.SMTP(host='smtp.gmail.com', port=587)
    s.starttls()
    s.login("shirialm1994@gmail.com", "Zohar256")
    msg = EmailMessage()
    msg.set_content(email_text)
    msg['Subject'] = msg_subject
    msg['From'] = 'shirialm1994@gmail.com'
    msg['To'] =  'shiria@notalvision.com'#mailing_list  #
    # Send the message via our own SMTP server.
    s.send_message(msg)
    s.quit()

def my_logger(logger_name, level=logging.DEBUG):
    """
    Method to return a custom logger with the given name and level
    """
    logger = logging.getLogger(logger_name)
    logging.basicConfig(
        filename=logger_name,
        filemode='w',
        format='%(asctime)s, %(message)s',
        datefmt='%H:%M:%S',
        level=logging.DEBUG)
    # Creating and adding the console handler
    console_handler = logging.StreamHandler(sys.stdout)
    logger.addHandler(console_handler)
    # Creating and adding the file handler
    file_handler = logging.FileHandler(logger_name, mode='a')
    logger.addHandler(file_handler)
    return logger

def DecreasingMSI(MSI_list,percentage):
    mean_list=[]
    for ind in range(1,len(MSI_list)+1):
        tmp_list=MSI_list[0:ind]
        curr_mean=np.mean(tmp_list)
        mean_list.append(curr_mean)
    try:
        total_max_mean=np.max(mean_list)
        if total_max_mean*(1-percentage)>mean_list[-1]:
            return 'Decrease in MSI'
        else:
            return ''
    except:
        return ''

