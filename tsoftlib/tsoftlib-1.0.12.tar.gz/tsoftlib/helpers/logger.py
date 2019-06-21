from .fileMaker import makeFolderIfNotExists
from datetime import datetime

DEFAULTFOLDERNAME='./log'

def logIt(name, msg):
    makeFolderIfNotExists(DEFAULTFOLDERNAME)
    with open(DEFAULTFOLDERNAME+'/'+name+'.log', 'a+', encoding='UTF-8') as logFile:
        now = datetime.now()
        time = now.strftime("%d-%m-%y|%H:%M:%S")
        s = f'{time} - {msg}\n'
        logFile.write(s)
        logFile.close()