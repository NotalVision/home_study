import pyodbc



conn = pyodbc.connect('Driver={SQL Server};'
                      'Server=172.30.2.177;'
                      'Database=OCTanalysisBackupForTesting;'
                      'uid=shiri_almog;pwd=shiri@123')
cursor = conn.cursor()
cursor.execute("INSERT INTO ALERTS(PatientID,Eye, Date, ScanID, AlertParam,ParamValue,AlertSent,Outdated) VALUES ('NH02001','L','2020-10-30 14:43:12',4953, 'Vmsi', 1.2, 0,0)")
conn.commit()


def check_for_alerts(self, patient, new_row, scan_path):
    email_text = ''
    alerts_object = patient.alerts
    # alerts_object=alerts_object.check_if_outdated()
    alerts = alerts_object.alert_dic

    e = patient.eye
    date = new_row['Date - Time'].values[0]
    if new_row['VG_output'].values[0] == 0 or new_row['VG_output'].values[0] == 2:
        email_text += ('No VG output in the last scan: \nScan Date: ' + str(new_row['Date - Time'].values[0])
                       + ', Scan ID: ' + str(new_row['ScanID'].values[0][:-1]) + '\n' + scan_path + '\n' + '\n')
        cursor.execute(
            "INSERT INTO ALERTS(PatientID,Eye, Date, ScanID, AlertParam,ParamValue,AlertSent,Outdated) VALUES (?,?,?,?,?,?)",patient.patient_ID,e,date,4953, 'VG_output', 0, 0,0)
        conn.commit()
        return email_text, new_row

    for param in list(alerts[e].keys()):
        if math.isnan(self.params_dic[param][0]):
            high_or_low = 'high'
        else:
            high_or_low = 'low'
        if (abs(new_row[param].values[0]) < self.params_dic[param][0]) or (
                abs(new_row[param].values[0]) > self.params_dic[param][1]):
            alerts[e][param][date] = ('Scan Date: ' + str(new_row['Date - Time'].values[0]) + ', Scan ID: ' + str(
                new_row['ScanID'].values[0][:-1]) + '\n' + param + ': ' + str(
                new_row[param].values[0]) + '\n' + scan_path + '\n')
            if len(alerts[e][param]) >= self.params_dic[param][2]:
                if self.params_dic[param][2] == 1:
                    email_text += '{} was {} in the last scan:'.format(param, high_or_low) + '\n'
                else:
                    email_text += '{} was {} in the last {} scans:'.format(param, high_or_low,
                                                                           self.params_dic[param][2]) + '\n'
                for i in alerts[e][param]:
                    email_text += str(alerts[e][param][i])
                email_text += '\n'
                alerts[e][param] = {}

    if new_row['Alert_for_clipped'].values[0] == 1:
        email_text += ('High percentage of clipped Bscans in the last scan: \nScan Date: ' + str(
            new_row['Date - Time'].values[0])
                       + ', Scan ID: ' + str(new_row['ScanID'].values[0][:-1]) + '\n' + scan_path + '\n' + '\n')

    if new_row['TimeOut'].values[0] == 1:
        email_text += ('Timeout reported in the last scan: \nScan Date: ' + str(new_row['Date - Time'].values[0])
                       + ', Scan ID: ' + str(new_row['ScanID'].values[0][:-1]) + '\n' + scan_path + '\n' + '\n')

    with open(patient.alerts.path + '/alerts.pkl', 'wb') as f:
        pickle.dump(alerts, f, pickle.HIGHEST_PROTOCOL)
    new_row.loc[0, 'checked_for_alerts'] = 1
    if email_text != '':
        with open(self.text_file, 'a') as f:
            f.writelines('\n({})'.format(e) + email_text)
    return email_text, new_row