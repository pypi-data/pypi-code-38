from travel_backpack import log_info as li
import win32con
import win32api
import win32gui
import time
from ctypes import POINTER, windll, Structure, cast, CFUNCTYPE, c_int, c_uint, c_void_p, c_bool, sizeof, Union, c_ushort, c_ulong, c_long, c_char
from comtypes import GUID
from ctypes.wintypes import HANDLE, DWORD, USHORT, HWND, WPARAM, ULONG, LONG, UINT, BYTE
from datetime import datetime as dt
now = dt.now

log_info = lambda info: li(info, file='System.log', print_time=False)

PBT_POWERSETTINGCHANGE = 0x8013
WM_INPUT = 0x00FF

display_on_callbacks = dict()
display_off_callbacks = dict()
display_dim_callbacks = dict()
session_end_callbacks = dict()
sys_suspend_callbacks = dict()


def display_change(data):
    mapping = {0: 'off', 1: 'on', 2: 'dimmed'}
    status = mapping[data]
    if status == 'on':
        for c in display_on_callbacks.values():
            #print('fon')
            c()
    elif status == 'off':
        for c in display_off_callbacks.values():
            #print('foff')
            c()
    elif status == 'dimmed':
        for c in display_dim_callbacks.values():
            #print('fdim')
            c()

    return "Display " + status


power_settings = {
    'SYSTEM_AWAYMODE': {
        'GUID': '{98A7F580-01F7-48AA-9C0F-44352C29E5C0}',
        'Data': {
            0: 'Exiting away mode',
            1: 'Entering away mode'
        }
    },
    'CONSOLE_DISPLAY_STATE': {
        'GUID': '{6FE69556-704A-47A0-8F24-C28D936FDA47}',
        'Data': display_change
    },
    'ACDC_POWER_SOURCE': {
        'GUID': '{5D3E9A59-E9D5-4B00-A6BD-FF34FF516548}',
        'Data': {
            0: 'AC power',
            1: 'DC power (batteries)',
            2: 'Short term power source (UPS)'
        }
    },
    'BATTERY_PERCENTAGE_REMAINING': {
        'GUID': '{A7AD8041-B45A-4CAE-87A3-EECBB468A9E1}',
        'Data': lambda batt: f'Battery remaining: {batt}'
    }
}

GUID_to_name = {v['GUID']: k for k, v in power_settings.items()}


def process_power_broadcast(lparam):
    settings = cast(lparam, POINTER(POWERBROADCAST_SETTING)).contents

    power_setting_GUID = str(settings.PowerSetting)
    data_length = settings.DataLength
    data = settings.Data

    data_info = power_settings.get(GUID_to_name.get(power_setting_GUID)).get('Data')
    if data_info is None:
        log_info(f'Power setting changed but GUID is unknown: {power_setting_GUID}')

    elif callable(data_info):
        log_info(data_info(data))
    else:
        log_info(data_info.get(data, f'Unknown Data: {hex(data)}({data})'))


def system_suspend(x):
    for c in sys_suspend_callbacks.values():
        log_info('f sys suspend')
        c()
    log_info('System suspend')


power_broadcast_wParams = {
    win32con.PBT_APMPOWERSTATUSCHANGE: lambda x: log_info('Power status has changed'),
    win32con.PBT_APMRESUMEAUTOMATIC: lambda x: log_info('System resume'),
    win32con.PBT_APMRESUMESUSPEND: lambda x: log_info('System resume by user input'),
    win32con.PBT_APMSUSPEND: system_suspend,
    PBT_POWERSETTINGCHANGE: process_power_broadcast
}

end_session_lParams = {
    0x00000000: 'Shutdown or Restart',
    0x00000001: 'Using file that must be replaced, system being serviced or resourses exausted',
    0x40000000: 'Force shutdown',
    0x80000000: 'User logging off'
}


class POWERBROADCAST_SETTING(Structure):
    _fields_ = [("PowerSetting", GUID), ("DataLength", DWORD), ("Data", DWORD)]


class RECT(Structure):
    _fields_ = [('left', c_long), ('top', c_long), ('right', c_long), ('bottom', c_long)]


class PAINTSTRUCT(Structure):
    _fields_ = [('hdc', c_int), ('fErase', c_int), ('rcPaint', RECT), ('fRestore', c_int), ('fIncUpdate', c_int), ('rgbReserved', c_char * 32)]


class POINT(Structure):
    _fields_ = [('x', c_long), ('y', c_long)]


class MSG(Structure):
    _fields_ = [('hwnd', c_int), ('message', c_uint), ('wParam', c_int), ('lParam', c_int), ('time', c_int), ('pt', POINT)]


class RAWINPUTDEVICE(Structure):
    _fields_ = [
        ("usUsagePage", c_ushort),
        ("usUsage", c_ushort),
        ("dwFlags", DWORD),
        ("hwndTarget", HWND),
    ]


class RAWINPUTHEADER(Structure):
    _fields_ = [
        ("dwType", DWORD),
        ("dwSize", DWORD),
        ("hDevice", HANDLE),
        ("wParam", WPARAM),
    ]


class RAWMOUSE(Structure):
    class _U1(Union):
        class _S2(Structure):
            _fields_ = [
                ("usButtonFlags", c_ushort),
                ("usButtonData", c_ushort),
            ]

        _fields_ = [
            ("ulButtons", ULONG),
            ("_s2", _S2),
        ]

    _fields_ = [
        ("usFlags", c_ushort),
        ("_u1", _U1),
        ("ulRawButtons", ULONG),
        ("lLastX", LONG),
        ("lLastY", LONG),
        ("ulExtraInformation", ULONG),
    ]
    _anonymous_ = ("_u1", )


class RAWKEYBOARD(Structure):
    _fields_ = [
        ("MakeCode", c_ushort),
        ("Flags", c_ushort),
        ("Reserved", c_ushort),
        ("VKey", c_ushort),
        ("Message", UINT),
        ("ExtraInformation", ULONG),
    ]


class RAWHID(Structure):
    _fields_ = [
        ("dwSizeHid", DWORD),
        ("dwCount", DWORD),
        ("bRawData", BYTE),
    ]


class RAWINPUT(Structure):
    class _U1(Union):
        _fields_ = [
            ("mouse", RAWMOUSE),
            ("keyboard", RAWKEYBOARD),
            ("hid", RAWHID),
        ]

    _fields_ = [
        ("header", RAWINPUTHEADER),
        ("_u1", _U1),
        ("hDevice", HANDLE),
        ("wParam", WPARAM),
    ]
    _anonymous_ = ("_u1", )


def wndproc(hwnd, msg, wparam, lparam):
    print(f"wndproc: {msg} w: {hex(wparam)} l: {hex(lparam)}")
    if msg == win32con.WM_POWERBROADCAST:
        power_broadcast_wParams.get(wparam, lambda x: log_info(f'Unknown wParam for WM_POWERBROADCAST ({wparam})'))(lparam)
        return True

    elif msg == win32con.WM_QUERYENDSESSION:
        log_info("Query End Session")
        for k, v in end_session_lParams.items():
            if lparam & k:
                log_info(v)
        for c in session_end_callbacks.values():
            #print('fsend')
            log_info('Executing eeve')
            c()
            log_info('Executed eeve')
        #return False  # to cancel shutdown
        return True

    elif msg == win32con.WM_ENDSESSION:
        log_info("End Session")
        for k, v in end_session_lParams.items():
            if lparam & k:
                log_info(v)
        return 0

    elif msg == WM_INPUT:
        process_input(wparam, lparam)

    else:
        log_info(f"wndproc: {msg}\nw: {hex(wparam)}\nl: {hex(lparam)}")


running = False

GetRawInputData = windll.user32.GetRawInputData


def process_input(wParam, hRawInput):
    print('input from background?:', wParam)
    RID_INPUT = 0x10000003
    POINTER(c_int)
    ri = RAWINPUT()
    GetRawInputData(hRawInput, RID_INPUT, POINTER(ri), POINTER(c_int), sizeof(RAWINPUTHEADER))
    print('type:', ri.header.dwType)
    print('device:', ri.header.hDevice)
    print('message:', ri.data.keyboard.Message)
    print('vKey:', ri.data.keyboard.VKey)
    print('scan code:', ri.data.keyboard.MakeCode)
    print('state:', ri.data.keyboard.Flags)
    pass


def run():
    global running
    if running:
        return
    running = True
    log_info("*** STARTING ***")
    running = True
    hinst = win32api.GetModuleHandle(None)
    wndclass = win32gui.WNDCLASS()
    wndclass.hInstance = hinst
    wndclass.lpszClassName = "PyWindow"
    CMPFUNC = CFUNCTYPE(c_bool, c_int, c_uint, c_uint, c_void_p)
    wndproc_pointer = CMPFUNC(wndproc)
    messageMap = {
        win32con.WM_POWERBROADCAST: wndproc_pointer,
        win32con.WM_QUERYENDSESSION: wndproc,
        win32con.WM_ENDSESSION: wndproc,
        win32con.WM_SYSCOMMAND: wndproc,
        win32con.WM_DESTROY: wndproc,
        win32con.WM_CLOSE: wndproc,
        win32con.WM_QUIT: wndproc,
        WM_INPUT: wndproc
    }

    try:
        myWindowClass = win32gui.RegisterClass(wndclass)
        #hwnd = win32gui.CreateWindowEx(win32con.WS_EX_LEFT, myWindowClass, "PyWindow", 0, 0, 0, win32con.CW_USEDEFAULT, win32con.CW_USEDEFAULT, 0, 0,
        #                               hinst, None)
        hwnd = win32gui.CreateWindowEx(win32con.WS_EX_LEFT, wndclass.lpszClassName, "PyWindow", 0, 0, 0, win32con.CW_USEDEFAULT,
                                       win32con.CW_USEDEFAULT, win32con.NULL, win32con.NULL, hinst, None)
    except Exception as e:
        log_info("Exception: %s" % str(e))

    if hwnd is None:
        log_info("hwnd is none!")
    else:
        log_info("hwnd: %s" % hwnd)
    '''
    rid = RAWINPUTDEVICE()
    rid.usUsagePage = 1
    rid.usUsage = 6
    rid.dwFlags = 0x00000100  # RIDEV_INPUTSINK
    rid.hwndTarget = HWND(hwnd)

    ridptr = POINTER(RAWINPUTDEVICE)(rid)
    ridsz = sizeof(rid)

    RegisterRawInputDevices = windll.user32.RegisterRawInputDevices
    print('register return:', RegisterRawInputDevices(ridptr, 1, ridsz))

    GetRegisteredRawInputDevices = windll.user32.GetRegisteredRawInputDevices
    num_ptr = POINTER(UINT)(c_uint(5))
    devs_ptr = POINTER(RAWINPUTDEVICE)(rid)
    print('registered devices:', GetRegisteredRawInputDevices(devs_ptr, num_ptr, ridsz))
    print(num_ptr.contents)
    '''
    # Register for raw input
    Rid = (1 * RAWINPUTDEVICE)()
    Rid[0].usUsagePage = 0x01
    #Rid[0].usUsage = 0x02
    Rid[0].usUsage = 6
    RIDEV_INPUTSINK = 0x00000100  # Get events even when not focused
    Rid[0].dwFlags = RIDEV_INPUTSINK
    Rid[0].hwndTarget = hwnd

    RegisterRawInputDevices = windll.user32.RegisterRawInputDevices
    RegisterRawInputDevices(Rid, 1, sizeof(RAWINPUTDEVICE))

    wndclass.lpfnWndProc = messageMap

    register_function = windll.user32.RegisterPowerSettingNotification
    hwnd_pointer = HANDLE(hwnd)
    for name, power_setting_info in power_settings.items():
        result = register_function(hwnd_pointer, GUID(power_setting_info['GUID']), DWORD(0))
        print('registering', name)
        #print('result:', hex(result))
        #print('lastError:', win32api.GetLastError())
        #print()

    #print('\nEntering loop')
    while True:
        win32gui.PumpWaitingMessages()
        time.sleep(1)
        #print('.', end='', flush=True)


if __name__ == "__main__":
    run()


def thread_run():

    import travel_backpack
    travel_backpack.threadpool(run)()

    return
    global running
    if not running:
        running = True
        import travel_backpack
        travel_backpack.threadpool(run)()


class Display:
    def __init__(self, action, status):
        from uuid import uuid4
        self.uuid = uuid4()
        self.mappings = {'on': display_on_callbacks, 'off': display_off_callbacks, 'dimmed': display_dim_callbacks}
        self.status = status
        #print(action)
        self.mappings[self.status][self.uuid] = action
        thread_run()

    def unregister(self):
        del self.mappings[self.status][self.uuid]


class SessionEnd:
    def __init__(self, action):
        from uuid import uuid4
        self.uuid = uuid4()
        session_end_callbacks[self.uuid] = action

        thread_run()

    def unregister(self):
        del session_end_callbacks[self.uuid]


class SystemSuspend:
    def __init__(self, action):
        from uuid import uuid4
        self.uuid = uuid4()
        sys_suspend_callbacks[self.uuid] = action

        thread_run()

    def unregister(self):
        del sys_suspend_callbacks[self.uuid]


triggers = {'display': Display, 'session end': SessionEnd, 'system suspend': SystemSuspend}
