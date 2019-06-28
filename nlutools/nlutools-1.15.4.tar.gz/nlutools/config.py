import os
from os import path

#baseDir = os.path.dirname(path.dirname(__file__))
baseDir = os.path.dirname(__file__)

def readModuleMapping(mapFile):
    with open(mapFile,'r') as f:
        return {item[0]:item[1] for item in \
                        (line.strip().split('=') for line in f.readlines() \
                        if line.strip() and not line.strip().startswith('#'))}

#mapConf = readModuleMapping('../config/module_mapping.txt')
mapConf = readModuleMapping(baseDir+'/config/module_map_url.txt')
supportConf = readModuleMapping(baseDir+'/config/support_conf.txt')

def getLocalIp():
    import socket,fcntl,struct
    s=socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(('8.8.8.8',80))
    ip = s.getsockname()[0]
    return ip

localIp = getLocalIp()

def getEnvLabel():
    if '192.168.7' in localIp or '192.168.8' in localIp or '192.168.9' in localIp:
        return 'online'
    if '10.9' in localIp:
        return 'test'
    if '192.168.1' in localIp:
        return 'dev'
env=getEnvLabel()
