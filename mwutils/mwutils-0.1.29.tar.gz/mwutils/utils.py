
from datetime import datetime, timedelta
import time as time_u
import configparser
import socket
import os
import sys

minTime = lambda t1,t2: t1 if t1<t2 else t2
maxTime = lambda t1,t2: t1 if t1>t2 else t2

def getConfig(filename):
    #获取config配置文件
    config = configparser.ConfigParser()
    # 如果是win平台使用程序目录下的配置，因win目录下的配置应该只会用于测试
    sys_name = os.name
    path = ''
    # 允许外面指定config文件，因pycharm2016.3开始argv参数顺序调整，
    # 导致argv[1]不再是传入的config.ini参数，采用遍历取ini文件为配置
    for f in sys.argv:
        if f.endswith('.ini'):
            path = f
            break
    if not path:
        if sys_name == 'nt':
            path = os.path.split(os.path.realpath(filename))[0] + '\\config.ini'
        elif sys_name == 'posix':
            dirName = os.path.split(os.path.realpath(filename))[0].split('/')
            # /etc/maxwin/sync_db2redis/config.ini ,专案名为 sync_db2redis
            prjname = dirName[len(dirName) - 1]
            path = '/etc/maxwin/%s/config.ini' % prjname
        else:
            path = '/etc/maxwin/anlysetrip/config.ini'
    config.read(path)
    return config

def oneDay():
    return timedelta(days=1)

def oneHour():
    return timedelta(hours=1)

def none2default(val,NoneVal):
    return val if val else NoneVal

def getSec(time):
    return time.hour*60*60+time.minute*60+time.second if time else 0

def dateAddTime(adate,atime):
    return datetime.combine(adate,atime)

def datetimeAddSec(adatetime,aseconds):
    return adatetime + timedelta(seconds=aseconds)

def datetimeReduceSec(adatetime,aseconds):
    return adatetime - timedelta(seconds=aseconds)

def toUTCtime(dt):
    if dt:
        return int(dt.timestamp())
    else:
        return time_u.timezone

def bool2redis(val):
    return -1 if val else 0

def hostname():
    return socket.gethostname()

