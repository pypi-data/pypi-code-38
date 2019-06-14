# -*- coding:UTF-8 -*-


'''
Created on 2013-8-2

@author: caifenghua
'''

import os
import platform
import ctypes
import sys
import locale
import codecs

WINXP = 5
WINVISTA = 6
WIN7 = 7
WIN8 = 8


def GetSystemMainVer():
    verStr = platform.version()
    verStrList = verStr.split('.')
    verInfo = []
    for i in verStrList:
        verInfo.append(int(i))

    mainVer = verInfo[0]
    subVer = verInfo[1]

    if mainVer == 5:
        return WINXP
    elif mainVer == 6:
        if subVer == 0:
            return WINVISTA
        elif subVer == 1:
            return WIN7
        elif subVer >= 2:
            return WIN8
    else:
        return None


# 一种实现方式
def check_process_existence(process_name):
    import win32com.client
    WMI = win32com.client.GetObject('winmgmts:')
    processCodeCov = WMI.ExecQuery('select * from Win32_Process where Name="%s"' % process_name)
    if len(processCodeCov) > 0:
        print(processCodeCov)
        print('%s is exists' % process_name)
    else:
        print('%s is not exists' % process_name)


def query_process_ori():
    import wmi
    c = wmi.WMI(find_classes=False)
    #     for i in c.Win32_Process(["Caption", "ProcessID"]):
    for i in c.Win32_Process():
        print(i)


def get_brief_process_info(caption):
    import wmi
    c = wmi.WMI()
    return c.Win32_Process(fields=["Caption", "ProcessID", "ExecutablePath"], Caption=caption)


def query_process(caption):
    import wmi
    c = wmi.WMI()
    #     for i in c.Win32_Process(["Caption", "ProcessID"]):
    for i in c.Win32_Process(fields=["Caption", "ProcessID", "ExecutablePath"], Caption=caption):
        print(i)


TH32CS_SNAPPROCESS = 0x00000002


class PROCESSENTRY32(ctypes.Structure):
    _fields_ = [("dwSize", ctypes.c_ulong),
                ("cntUsage", ctypes.c_ulong),
                ("th32ProcessID", ctypes.c_ulong),
                ("th32DefaultHeapID", ctypes.c_ulong),
                ("th32ModuleID", ctypes.c_ulong),
                ("cntThreads", ctypes.c_ulong),
                ("th32ParentProcessID", ctypes.c_ulong),
                ("pcPriClassBase", ctypes.c_ulong),
                ("dwFlags", ctypes.c_ulong),
                ("szExeFile", ctypes.c_char * 260)]


def getProcList():
    CreateToolhelp32Snapshot = ctypes.windll.kernel32.CreateToolhelp32Snapshot
    Process32First = ctypes.windll.kernel32.Process32First
    Process32Next = ctypes.windll.kernel32.Process32Next
    CloseHandle = ctypes.windll.kernel32.CloseHandle
    hProcessSnap = CreateToolhelp32Snapshot(TH32CS_SNAPPROCESS, 0)
    pe32 = PROCESSENTRY32()
    pe32.dwSize = ctypes.sizeof(PROCESSENTRY32)
    if not Process32First(hProcessSnap, ctypes.byref(pe32)):
        print("Failed getting first process.", file=sys.stderr)
        return

    while True:
        yield pe32
        if not Process32Next(hProcessSnap, ctypes.byref(pe32)):
            break

    CloseHandle(hProcessSnap)


def killProcessByPid(pid):
    handle = ctypes.windll.kernel32.OpenProcess(1, False, pid)
    ctypes.windll.kernel32.TerminateProcess(handle, 0)


def getChildPid(pid):
    procList = getProcList()
    for proc in procList:
        if proc.th32ParentProcessID == pid:
            yield proc.th32ProcessID


def killTaskByPid(pid):
    childList = getChildPid(pid)
    for childPid in childList:
        killTaskByPid(childPid)

    killProcessByPid(pid)


def get_system_encoding():
    return codecs.lookup(locale.getpreferredencoding()).name


def is_64_windows():
    return 'PROGRAMFILES(X86)' in os.environ


def getProgramFiles32():
    if is_64_windows():
        return os.environ['PROGRAMFILES(X86)']
    else:
        return os.environ['PROGRAMFILES']


def getProgramFiles64():
    if is_64_windows():
        return os.environ['PROGRAMW6432']
    else:
        return None


def getAppDataPath():
    return os.environ['APPDATA']


if __name__ == '__main__':
    #     caption = 'adb.exe'
    #     check_process_existence(caption)

    #     query_process_ori()

    #     query_process(caption)

    #     print('before kill')
    #     info_list = get_brief_process_info(caption)
    #     for i in info_list:
    #         print(i)
    #         kill_process_by_pid(i.ProcessID)
    #
    #     print('after kill')
    #     info_list = get_brief_process_info(caption)
    #     for i in info_list:
    #         print(i)

    print(GetSystemMainVer())

    print('to the end')
