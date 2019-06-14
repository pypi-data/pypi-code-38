# -*- coding:UTF-8 -*-

'''
Created on 2013-9-7

@author: cfh
'''
import win32api
import win32file
import win32pipe
import winerror
import pywintypes
import time
import creditutils.base_util as base

import inspect

def func_flag():
    pass

global __modpath__
__modpath__ = base.module_path(func_flag)


def get_file_line():
    return (__modpath__, inspect.currentframe().f_back.f_lineno)

# 命名管道读取实现    
class ReadClient(object):
    MS_TO_SEC = 0.001
    WAIT_TIMEOUT = 2000
    BUFFER_SIZE = 16384
    PIPE_PATH_FORMAT = '\\\\{0}\\pipe\\{1}'
    PIPE_NAME = 'USB_DEVICE_MONITOR_WRITE_SERVER_201309122124'
    PIPE_PATH = PIPE_PATH_FORMAT.format('.', PIPE_NAME)
    MSG_HEAD_FLAG = '!PIPE_MSG_HEAD!'
    
    def __init__(self, pipePath=PIPE_PATH):
        self.pipePath = pipePath
        self.hPipe = None
        self.receiver = None
        
    def Connect(self):
        isFirstConnect = True
        while True:
            try:
                self.hPipe = win32file.CreateFile(self.pipePath, 
                                             win32file.GENERIC_READ, 
                                             0, 
                                             None, 
                                             win32file.OPEN_EXISTING,
                                             0,
                                             None)
                
                infoFormat = 'The named pipe {0} is connected.'
                info = infoFormat.format(self.pipePath)
                win32api.OutputDebugString(info)
                
                return self.hPipe
            
            except pywintypes.error as e:
                infoFormat = 'Unable to open named pipe {0}, w/err: {1}'
                info = infoFormat.format(self.pipePath, e.args[2]);
                win32api.OutputDebugString(info)
                
                if isFirstConnect:
                    isFirstConnect = False
                
                    # 如果提示没有找到文件，则等待一定时间之后再尝试打开
                    if e.args[0] == winerror.ERROR_FILE_NOT_FOUND:
                        time.sleep(ReadClient.WAIT_TIMEOUT*ReadClient.MS_TO_SEC)
                        continue
    
                    elif e.args[0] == winerror.ERROR_PIPE_BUSY:
                        # All pipes instances are busy, so wait for some seconds
                        try:
                            win32pipe.WaitNamedPipe(self.pipePath, ReadClient.WAIT_TIMEOUT)
                            continue
                        except pywintypes.error as waitError:
#                             if waitError.args[0] == winerror.ERROR_SEM_TIMEOUT:
                            infoFormat = '{0} {1} failed, w/err: {2}'
                            info = infoFormat.format(waitError.args[1], self.pipePath, waitError.args[2])
                            win32api.OutputDebugString(info)
                            
                            return None
                                
                    else:   # Exit if an error other than ERROR_FILE_NOT_FOUND or ERROR_PIPE_BUSY occurs
                        return None
                else:
                    return None
                
    def Receive(self):
        # Receive data from server
        
        bufObject = win32file.AllocateReadBuffer(ReadClient.BUFFER_SIZE)
        
        while True:
            try:
                (readRtn, data) = win32file.ReadFile(self.hPipe, bufObject)
                if readRtn != 0 and readRtn != winerror.ERROR_MORE_DATA:
                    showFormat = 'ReadFile failed, w/err: {0} {1}: {2}'
                    showInfo = showFormat.format(win32api.FormatMessage(win32api.GetLastError()), *get_file_line())
                    win32api.OutputDebugString(showInfo)
                    break
                
                data_list = data.split(ReadClient.MSG_HEAD_FLAG)
                if self.receiver:
                    for item in data_list:
                        if len(item) > 0:
                            self.receiver(item)
                
            except pywintypes.error as e:
                showFormat = '{0} failed, w/err: {1} {2}: {3}'
                showInfo = showFormat.format(e.args[1], e.args[2], *get_file_line())
                win32api.OutputDebugString(showInfo)
                break
            
    def SetReceiver(self, receiver):
        self.receiver = receiver
    
    def Close(self):
        if self.hPipe:
            self.hPipe.Close()
            self.hPipe = None

class Consumer:
    TYPE_FLAG = 'CHANGE_TYPE'       # 设备状态变化标识
    TYPE_ARRIVAL_FLAG = 'ARRIVAL'       # 设备插入
    TYPE_REMOVE_FLAG = 'REMOVE'     # 设备拔出
    TYPE_HEARTBEAT_FLAG = 'HEARTBEAT'       # 心跳
    PIPE_MSG_COLON_ALIAS = '&!colon!&'      # ":"替换符
    PIPE_MSG_COMMA_ALIAS = '&!comma!&'      # ","替换符
    
    VID_FLAG = 'VID'
    PID_FLAG = 'PID'
    SN_FLAG = 'SN'
    NAME_FLAG = 'FRIENDLYNAME'
    MFG_FLAG = 'MFG'        # 厂商信息
    DESC_FLAG = 'DEVICEDESC'
    
    
    TYPE_ARRIVAL = 1
    TYPE_REMOVE = 2
    TYPE_HEARTBEAT = 3
    
    TYPE_MAP = {
        TYPE_ARRIVAL_FLAG: TYPE_ARRIVAL,
        TYPE_REMOVE_FLAG: TYPE_REMOVE,
        TYPE_HEARTBEAT_FLAG: TYPE_HEARTBEAT
    }
    
    HEARTBEAT_SHOW_INTERVAL = 60
    
    def __init__(self):
        self.heartbeatCnt = 0
        self.receiver = None
    
    def _replace_seperator_alias_in_data(self, data):
        return data.replace(Consumer.PIPE_MSG_COLON_ALIAS, ':').replace(Consumer.PIPE_MSG_COMMA_ALIAS, ',')
    
    def Process(self, item):
        infoDict = {}
        
        infos = item.split(',')
        for subItem in infos:
            if len(subItem) > 0:
                infoItems = subItem.split(':')
                key = self._replace_seperator_alias_in_data(infoItems[0].strip())
                val = self._replace_seperator_alias_in_data(infoItems[1].strip())
                infoDict[key] = val
        
        self._ShowDebugInfo(infoDict)
        
        try:
            msgType = Consumer.TYPE_MAP[infoDict[Consumer.TYPE_FLAG]]
            if msgType != Consumer.TYPE_HEARTBEAT:
                if self.receiver:
                    self.receiver(infoDict)
                    
        except KeyError as e:
            win32api.OutputDebugString(str(e))
            return
        
    def _ShowDebugInfo(self, item):
        try:
            msgType = Consumer.TYPE_MAP[item[Consumer.TYPE_FLAG]]
        except KeyError as e:
            win32api.OutputDebugString(str(e))
            return
        
        showFormat = 'Receives Message: "{0}"'
        if msgType == Consumer.TYPE_HEARTBEAT:
            self.heartbeatCnt += 1
            if self.heartbeatCnt % Consumer.HEARTBEAT_SHOW_INTERVAL == 0:
                showInfo = showFormat.format(item)
            else:
                showInfo = None
        else:
            showInfo = showFormat.format(item)

        if showInfo:            
            win32api.OutputDebugString(showInfo)
    
    def SetReceiver(self, receiver):
        self.receiver = receiver

BUFFER_SIZE = 65536
def CreateServer():
    p = win32pipe.CreateNamedPipe('\\\\.\\pipe\\test_pipe',
        win32pipe.PIPE_ACCESS_DUPLEX,
        win32pipe.PIPE_TYPE_MESSAGE | win32pipe.PIPE_WAIT,
        1, 65536, 65536,300, None)
    
    bufObject = win32file.AllocateReadBuffer(BUFFER_SIZE)
    data = 'Hello Pipe' 
    for i in range(len(data)):
        bufObject[i] = ord(data[i])
        
    win32pipe.ConnectNamedPipe(p, None)
    
    
    win32file.WriteFile(p, bufObject[0:len(data)])
    
def CreateClient():
    fileHandle = win32file.CreateFile('\\\\.\\pipe\\test_pipe',
                              win32file.GENERIC_READ | win32file.GENERIC_WRITE,
                              0, None,
                              win32file.OPEN_EXISTING,
                              0, None)
    data = win32file.ReadFile(fileHandle, 4096)
    win32file.CloseHandle(fileHandle)
    print(data)