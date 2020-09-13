import requests
import os
from time import sleep
from datetime import datetime

tdi_url="https://tdiwebapp2.azurewebsites.net"
FILE_NAME="data.txt"
DATA_FOLDER="data"
TMP_FOLDER="tmp"

#-----------------------------------------------------------
# write data to file
#-----------------------------------------------------------
def saveError(e):
    f = open("log/errors.txt", "a")
    s = '{} - {}\n'.format(datetime.now(),e)
    f.write(s)
    f.close()
#-----------------------------------------------------------
# Send data
#-----------------------------------------------------------
def send_data(txt):
    r=requests.post(tdi_url+'/home/setdata', data={'row':txt})
    print(r.text)
    return r.status_code
 
def read_file(file_name):
    if not os.path.isfile(file_name):
        return False
    
    print('send file: '+file_name)
    with open(file_name) as f:
        for line in f:
            send_data(line)
    
    os.remove(file_name)
            
    
def is_ready_to_send():
    try:
        r=requests.get(tdi_url)
        print('ready to send')
        return r.status_code == 200
    except:
        return False
#-----------------------------------------------------------
# main
#-----------------------------------------------------------
while 1:
    try:
        if is_ready_to_send():
            try:
                read_file(TMP_FOLDER+"/"+FILE_NAME)
            except Exception as e:
                saveError(e)
            #move
            os.replace(DATA_FOLDER+"/"+FILE_NAME, TMP_FOLDER+"/"+FILE_NAME)
            read_file(TMP_FOLDER+"/"+FILE_NAME)
            
        sleep(10) #delay in sec
    except Exception as e:
        saveError(e)
        sleep(10) #delay in sec
        


