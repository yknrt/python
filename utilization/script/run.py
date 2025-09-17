import subprocess
import os
import const

info = const.CONST

if os.path.exists('../stdout.log'):
    os.remove('../stdout.log')
if os.path.exists('../stderr.log'):
    os.remove('../stderr.log')

with open('../stdout.log', 'a') as fout, open('../stderr.log', 'a') as ferr:
    print('STEP1:マトリックス表算出 start')
    if info['OrcaFlex']['analyze']:
        result = subprocess.run('python matrix.py', shell=True, stdout=fout, stderr=ferr)
    print('STEP1:マトリックス表算出 end')
    print('STEP2:動揺量変換 start')
    result1 = subprocess.run('python conversion.py', shell=True, stdout=fout, stderr=ferr)
    print('STEP2:動揺量変換 end')
    print('STEP3:稼働率計算 start')
    result2 = subprocess.run('python kadou.py', shell=True, stdout=fout, stderr=ferr)
    print('STEP3:稼働率計算 end')