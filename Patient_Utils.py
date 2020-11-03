import pandas as pd
import numpy as np
import os
from os import path
from datetime import date
import scipy.io as sio
from email.message import EmailMessage
import smtplib
import csv
from Alerts_DB import Alert
import pickle

def check_if_timeout(scan_path):
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
    vglog_path=vg_path+r'/DB_data/VGLogDetails.csv'
    with open(vglog_path) as csv_file:
        rows = reversed(list(csv.reader(csv_file, delimiter=',')))
        last_line=rows.__next__()
        if last_line[0]=='11':
            status_type=last_line[3]
        else:
            status_type='running'
    return status_type


