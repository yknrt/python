import subprocess
import datetime
import os
import time

if os.path.exists('../stdout.log'):
    os.remove('../stdout.log')
if os.path.exists('../stderr.log'):
    os.remove('../stderr.log')


while True:
    curr_time = datetime.datetime.now()
    with open('../stdout.log', 'a') as fout, open('../stderr.log', 'a') as ferr:
        subprocess.run('python fetch.py', shell=True, stdout=fout, stderr=ferr)
    time.sleep(300)
            
        
