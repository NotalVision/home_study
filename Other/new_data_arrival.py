import os
import time
import pyodbc
from Utils import send_email_func

def UpdateScanTable(patients_list):
    in_current_table=[]
    conn = pyodbc.connect('Driver={SQL Server};'
                          'Server=172.30.2.246;'
                          'Database=AlgoTeam;'
                          'uid=shiri_almog;pwd=shiri@123')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Scan")
    row = cursor.fetchone()
    while row:
        in_current_table.append(int(row[0]))
        row = cursor.fetchone()

    print (in_current_table)

    conn = pyodbc.connect('Driver={SQL Server};'
                          'Server=172.30.2.246;'
                          'Database=OCTAnalysis;'
                          'uid=shiri_almog;pwd=shiri@123')
    cursor = conn.cursor()
    cursor.execute("""
    SELECT  officialID,scanID,Scan.StartTime,Scan.Eye, sd.SessionID,session.StartTime,ModesDownloadedMask FROM SessionDownload sd 
    JOIN session ON sd.SessionID = Session.SessionID 
    join _patient on session.patientid = _patient.patientid 
    join _user on _patient.userid = _user.userid 
    join scan on Session.SessionID=Scan.SessionID
    join ScanConfigurationType on Scan.ConfigurationTypeID=ScanConfigurationType.ConfigurationTypeID
    WHERE sd.DataReady = 1 AND(IterationCounter IS NULL OR sd.IterationCounter <= 4) 
    AND session.StartTime >= '15-Nov-2020' AND session.StartTime <= '30-Nov-2020'
    and ScanConfigurationType.DevTeamName='TST'
    """)
    row = cursor.fetchone()
    to_add=[]
    while row:
        if row[0] in patients_list:
            if row[1] not in in_current_table:
                to_add.append([row[1],row[0],row[2],row[3],row[4]])
        row = cursor.fetchone()

    print (to_add)
    conn = pyodbc.connect('Driver={SQL Server};'
                          'Server=172.30.2.246;'
                          'Database=AlgoTeam;'
                          'uid=shiri_almog;pwd=shiri@123')
    cursor = conn.cursor()

    for row in to_add:
        cursor.execute("insert into Scan(ScanID, PatientID,Date,Eye,SessionID) VALUES (?,?,?,?,?)", row[0],row[1],row[2],row[3],row[4])
        conn.commit()
    email_text=''
    for row in to_add:
        email_text += 'Patient {}, on date: {}\n'.format(row[1],row[2])
    msg_subject = 'Attention: New Scans'
    if email_text:
        send_email_func(email_text, 'shiria@notalvision.com', msg_subject)

    return to_add

def GetAnalysisUnit(NewScans):
    VG_ID_list=[]
    VG_Output_List=[]
    DN_ID_list = []
    DN_Output_List = []
    connOCT = pyodbc.connect('Driver={SQL Server};'
                          'Server=172.30.2.246;'
                          'Database=OCTAnalysis;'
                          'uid=shiri_almog;pwd=shiri@123')
    cursorOCT = connOCT.cursor()

    connALGO = pyodbc.connect('Driver={SQL Server};'
                             'Server=172.30.2.246;'
                             'Database=AlgoTeam;'
                             'uid=shiri_almog;pwd=shiri@123')
    cursorALGO = connALGO.cursor()

    for i in NewScans:
        #Get VG unit ID, insert into AnalysisUnit
        cursorOCT.execute("SELECT ID,ScanID,AnalysisUnitDetailsID FROM AnalysisUnitProcess WHERE AnalysisUnitDetailsID in (11,13) AND ScanID=? ",i[0])
        row=cursorOCT.fetchone()
        cursorALGO.execute("insert into AnalysisUnit (AnalysisUnitID, ScanID, AnalysisUnitDetailsID) VALUES (?,?,?)", row[0], row[1], row[2])
        connALGO.commit()
        VG_ID_list.append(row)

        #Get DN unit ID, insert into AnalysisUnit
        try:
            cursorOCT.execute("SELECT ID,ScanID,AnalysisUnitDetailsID FROM AnalysisUnitProcess WHERE AnalysisUnitDetailsID in (12,14) AND ScanID=? ", i[0])
            row = cursorOCT.fetchone()
            cursorALGO.execute("insert into AnalysisUnit (AnalysisUnitID, ScanID, AnalysisUnitDetailsID) VALUES (?,?,?)", row[0], row[1],row[2])
            connALGO.commit()
            DN_ID_list.append(row)
        except:
            print (i)

    # Get VG parameters, Update VG table
    for id in VG_ID_list:
        cursorOCT.execute("""
        SELECT ID, AnalysisUnitProcessID, AdjustmentTime, RasterTime, TotalScanTime, MeanBMsiAll,
        MeanBMsiVsr,Vmsi,RegRangeX,RegRangeY,RegStdX,RegStdY, RegCentX,RegCentY,NumValidLines,QaVsrRemoveOutFOV,MaxGap,
        MeanGap, [MeanRetinalThickness3*3],MeanRetinalThicknessCST,MeanRetinalThicknessNIM, MeanRetinalThicknessTIM, 
        MeanRetinalThicknessSIM,MeanRetinalThicknessIIM,MeanXCover,MaxBMsiVsr from VG_ScanOutput vg WHERE AnalysisUnitProcessID=?
        """, id[0])
        VG_Output_List.append(cursorOCT.fetchone())
    for row in VG_Output_List:
        cursorALGO.execute("""
        insert into VG_Output (ID, AnalysisUnitProcessID, AdjustmentTime, RasterTime, TotalScanTime, MeanBMsiAll,
        MeanBMsiVsr,Vmsi,RegRangeX,RegRangeY,RegStdX,RegStdY, RegCentX,RegCentY,NumValidLines,QaVsrRemoveOutFOV,MaxGap,
        MeanGap,[MeanRetinalThickness3*3], MeanRetinalThicknessCST,MeanRetinalThicknessNIM, MeanRetinalThicknessTIM, 
        MeanRetinalThicknessSIM,MeanRetinalThicknessIIM,MeanXCover,MaxBMsiVsr) 
        VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
        """,  tuple(row))
        connALGO.commit()

    # Get DN parameters, Update DN table
    for id in DN_ID_list:
        cursorOCT.execute("""
        SELECT ID,AnalysisUnitProcessID,WithFluid,WithSrf,WithIrf,withERM,ClassScoreFluid,ClassScoreERM,EligibleQuant,
        SrfVolumeNl,IrfVolumeNl,FluidVolumeNl,MaxGapQuant,FluidVolumeNoClassNl from DN_ScanOutput vg WHERE AnalysisUnitProcessID=?
        """, id[0])
        DN_Output_List.append(cursorOCT.fetchone())

    for row in DN_Output_List:
        cursorALGO.execute("""
        insert into DN_Output (ID,AnalysisUnitProcessID, WithFluid,WithSrf,WithIrf,WithERM,ClassScoreFluid,
        ClassScoreERM,EligibleQuant,SrfVolumeNl,IrfVolumeNl,FluidVolumeNl,MaxGapQuant,FluidVolumeNoClassNl) 
        VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)
        """,  tuple(row))
        connALGO.commit()



if __name__ =="__main__":
    patients_list=['Jason1004','Jason1008','Jason1010','444001','444005','444006','444007','444008','444010','444014','444016','444017','8001','8002','8003','NH02001','NH02002','NH02003']
    while True:
        NewScans=UpdateScanTable(patients_list)
        GetAnalysisUnit(NewScans)
        print('mojo')

        time.sleep(600)

