import pandas as pd
import xlsxwriter
import os

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