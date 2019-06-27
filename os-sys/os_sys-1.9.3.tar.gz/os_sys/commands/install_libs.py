print('typ the lib that you want to update or install:\
type the lib that you want:')
import os

import os
import inspect
file = str(inspect.getfile(os))
file = file.replace('\os.py', '')
ja = input()

update = input('do you want to install a lib or upgrade one?(type install or upgrade):
')
if update == 'install':
    
    import subprocess as sub
    sub.getstatusoutput('pip install ' + ja.lower())
     
else:
    import subprocess as s
    s.getstatusoutput('pip install --upgrade ' + file)

