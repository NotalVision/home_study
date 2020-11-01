import pyodbc

def check_if_downloaded(host):
# Server details
    if host=='Local Host':
        conn = pyodbc.connect('Driver={SQL Server};'
                              'Server=172.30.2.246;'
                              'Database=OCTanalysis;'
                              'uid=shiri_almog;pwd=shiri@123')
        cursor = conn.cursor()
        cursor.execute("SELECT SessionID FROM SessionDownload WHERE ModesDownloadedMask=10 OR ModesDownloadedMask=11")

    else:
        conn = pyodbc.connect('Driver={SQL Server};'
                              'Server=172.30.2.177;'
                              'Database=OCTanalysis;'
                              'uid=shiri_almog;pwd=shiri@123')
        #BackupForTesting
        cursor = conn.cursor()
        cursor.execute("SELECT SessionID FROM SessionDownload WHERE ModesDownloadedMask=01 OR ModesDownloadedMask=11")

    records = cursor.fetchall()
    downloaded_sessions=[]
    for record in records:
        downloaded_sessions.append(record[0])

    return downloaded_sessions
