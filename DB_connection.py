import pyodbc

def check_if_downloaded():
# Server details
    conn = pyodbc.connect('Driver={SQL Server};'
                          'Server=172.30.2.246;'
                          'Database=OCTanalysis;' #BackupForTesting
                          'uid=shiri_almog;pwd=shiri@123')
    cursor = conn.cursor()

    cursor.execute("SELECT SessionID FROM SessionDownload WHERE ModesDownloadedMask=10 OR ModesDownloadedMask=11")
    records = cursor.fetchall()
    downloaded_sessions=[]
    for record in records:
        downloaded_sessions.append(record[0])

    return downloaded_sessions
