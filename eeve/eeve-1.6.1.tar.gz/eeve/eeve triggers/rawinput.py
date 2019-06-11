import structs
import ctypes
import time
import win32con
import win32gui
import win32api


def main():
    register_raw = False
    if register_raw:
        WM_INPUT = 0xff
        RIDEV_INPUTSINK = 0x00000100
        RID_INPUT = 0x10000003

        def ErrorIfZero(handle):
            if handle == 0:
                raise Exception("WinError: handle is 0")
            else:
                return handle

        def winproc(hwnd, message, wParam, lParam):
            if message == WM_INPUT:
                GetRawInputData = ctypes.windll.user32.GetRawInputData
                NULL = ctypes.c_int(win32con.NULL)
                dwSize = ctypes.c_uint()
                GetRawInputData(lParam, RID_INPUT, NULL, ctypes.byref(dwSize), ctypes.sizeof(structs.RAWINPUTHEADER))
                if dwSize.value == 40:
                    raw = structs.RAWINPUT()
                    if GetRawInputData(lParam, RID_INPUT, ctypes.byref(raw), ctypes.byref(dwSize),
                                       ctypes.sizeof(structs.RAWINPUTHEADER)) == dwSize.value:
                        RIM_TYPEMOUSE = 0x00000000
                        RIM_TYPEKEYBOARD = 0x00000001

                        if raw.header.dwType == RIM_TYPEMOUSE:
                            print((raw.header.hDevice, raw.mouse.usFlags, raw.mouse.ulButtons, raw.mouse._u1._s2.usButtonFlags,
                                   raw.mouse._u1._s2.usButtonData, raw.mouse.ulRawButtons, raw.mouse.lLastX, raw.mouse.lLastY,
                                   raw.mouse.ulExtraInformation))
                        elif raw.header.dwType == RIM_TYPEKEYBOARD:
                            print()
                            print('type:', raw.header.dwType)
                            print('device:', raw.header.hDevice)
                            print('message:', raw.keyboard.Message)
                            print('vKey:', raw.keyboard.VKey)
                            print('scan code:', raw.keyboard.MakeCode)
                            print('state:', raw.keyboard.Flags)
                        else:
                            print("unknown dwType:", raw.header.dwType)

                else:
                    print('different dwSize:', dwSize.value)
            else:
                print(f"wndproc: {message} w: {hex(wParam)} l: {hex(lParam)}")

            return ctypes.windll.user32.DefWindowProcA(ctypes.c_int(hwnd), ctypes.c_int(message), ctypes.c_int(wParam), ctypes.c_int(lParam))

        # Define Window Class
        wndclass = win32gui.WNDCLASS()
        wndclass.style = win32con.CS_HREDRAW | win32con.CS_VREDRAW
        wndclass.lpfnWndProc = structs.WNDPROC(winproc)
        #wndclass.cbClsExtra = 0
        wndclass.cbWndExtra = 0
        wndclass.hInstance = ctypes.windll.kernel32.GetModuleHandleA(ctypes.c_int(win32con.NULL))
        wndclass.hIcon = ctypes.windll.user32.LoadIconA(ctypes.c_int(win32con.NULL), ctypes.c_int(win32con.IDI_APPLICATION))
        wndclass.hCursor = ctypes.windll.user32.LoadCursorA(ctypes.c_int(win32con.NULL), ctypes.c_int(win32con.IDC_ARROW))
        wndclass.hbrBackground = ctypes.windll.gdi32.GetStockObject(ctypes.c_int(win32con.WHITE_BRUSH))
        #wndclass.lpszMenuName = None
        wndclass.lpszClassName = "MainWin"

        # Register Window Class
        #if not ctypes.windll.user32.RegisterClassA(ctypes.byref(wndclass)):
        if not win32gui.RegisterClass(wndclass):
            import win32api
            raise Exception("WinError:", win32api.GetLastError())

        # Create Window
        HWND_MESSAGE = -3
        hwnd = win32gui.CreateWindowEx(
            0,
            wndclass.lpszClassName,
            "Python Window",
            0,
            0,
            0,
            win32con.CW_USEDEFAULT,
            win32con.CW_USEDEFAULT,

            #HWND_MESSAGE,
            win32con.NULL,
            win32con.NULL,
            wndclass.hInstance,
            None)
        # Show Window
        #windll.user32.ShowWindow(c_int(hwnd), c_int(win32con.SW_SHOWNORMAL))
        #windll.user32.UpdateWindow(c_int(hwnd))

        # Register for raw input
        Rid = (1 * structs.RAWINPUTDEVICE)()
        Rid[0].usUsagePage = 0x01
        Rid[0].usUsage = 0x06
        Rid[0].dwFlags = RIDEV_INPUTSINK  # Get events even when not focused
        Rid[0].hwndTarget = hwnd

        RegisterRawInputDevices = ctypes.windll.user32.RegisterRawInputDevices
        RegisterRawInputDevices(Rid, 1, ctypes.sizeof(structs.RAWINPUTDEVICE))

    # register high-level keyboard hook (as low-level is executed before rawinput)
    hook_id_keyboard = None

    def high_level_keyboard_handler(nCode, wParam, lParam):
        print('YEAHHRR! BRUUUHH')
        return ctypes.windll.user32.CallNextHookEx(hook_id_keyboard, nCode, wParam, lParam)

        def init_get_bits(value: int):
            def get_bits(begin: int, end: int = None) -> int:
                if end is None:
                    end = begin
                return (value >> begin) & (2**(end - begin + 1) - 1)

            return get_bits

        allow_passing = True
        print('action:', wParam)
        get_bits = init_get_bits(lParam)
        key_info = {
            'repeat_count': get_bits(0, 15),
            'scan_code': get_bits(16, 23),
            'is_extended_key': get_bits(24),
            'reserved_bits': get_bits(25, 28),
            'is_alt_pressed': get_bits(29),
            'was_down_before': get_bits(30),
            'being_released': get_bits(31),
        }
        print('\n'.join([f'{k}: {v}' for k, v in key_info.items()]))
        if allow_passing:
            return ctypes.windll.user32.CallNextHookEx(hook_id_keyboard, nCode, wParam, lParam)
        else:
            print("#")
            return 1

    CMPFUNC = ctypes.CFUNCTYPE(ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.POINTER(ctypes.c_void_p))
    p_keyboard = CMPFUNC(high_level_keyboard_handler)
    module_handle = win32api.GetModuleHandle(None)
    print(hex(module_handle))
    module_handle = ctypes.wintypes.HMODULE(module_handle)
    print(module_handle)
    hook_id_keyboard = ctypes.windll.user32.SetWindowsHookExA(win32con.WH_KEYBOARD, p_keyboard, module_handle, 0)
    if not hook_id_keyboard:
        err = win32api.GetLastError()
        if err == 126:
            print('module not found')
        elif err == 1428:
            print('Cannot set nonlocal hook without a module handle.')
        else:
            print('Last Error:', err)

    while True:
        #peek_result, msg = win32gui.PeekMessage(None, 0, 0, 1)
        result, msg = win32gui.GetMessage(None, 0, 0)
        print('got msg:', msg, result)
        win32gui.TranslateMessage(msg)
        #print('translated')
        win32gui.DispatchMessage(msg)
        #print('sent')
        #sleep(0.5)
        pass

    while True:
        win32gui.PumpWaitingMessages()
        time.sleep(0.2)


if __name__ == '__main__':
    main()