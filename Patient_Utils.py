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


'''
This script contains accessory functions for the Patient object
'''

def check_if_timeout(scan_path):
    '''
    Check if timeout was recorded in rawdata. RETURNS 1/0

    '''
    with open(scan_path+'/RawData/output_plan.csv') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        timeout=0
        for line in csv_reader:
            if line[0]=='status':
                timeout=line[1]
                break
        if timeout=='net_timeout':
            return 1
        else:
            return 0


def check_vg_status(vg_path):
    '''
    Opens VG log to check status of VG
    '''
    vglog_path=vg_path+r'/DB_data/VGLogDetails.csv'
    with open(vglog_path) as csv_file:
        rows = reversed(list(csv.reader(csv_file, delimiter=',')))
        last_line=rows.__next__()
        if last_line[0]=='11':
            status_type=last_line[3]
        else:
            status_type='running'
    return status_type

def analysis_88(new_row_ver3,data):
    '''
    Get data from VG_Bscan_VSR file, and add relevant data to the current 'new_row'
    :param new_row_ver3: current new row, contains all data extracted from VG etc
    :param data: VG_Bscan_VSR file data
    :return:
    new row
    '''
    length=len(data)
    class1=sum(data==1)
    new_row_ver3.loc[0, '# Class 1']=class1
    new_row_ver3.loc[0, '# Class 2'] = sum(data == 2)
    new_row_ver3.loc[0, '# Class 3'] = sum(data == 3)
    new_row_ver3.loc[0, '% Class 1'] = sum(data == 1)/length*100
    new_row_ver3.loc[0, '% Class 2'] = sum(data == 2) / length * 100
    new_row_ver3.loc[0, '% Class 3'] = sum(data == 3) / length * 100
    new_row_ver3.loc[0, 'Full Scan(88)'] = int((length>=88))
    #check if the scan had 88+ bscans in class 1
    over88=0
    if class1>=88:
        over88=1
    new_row_ver3.loc[0, '88+ Class 1']=over88
    return new_row_ver3


