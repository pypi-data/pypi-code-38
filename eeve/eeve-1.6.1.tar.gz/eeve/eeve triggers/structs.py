from ctypes import POINTER, windll, Structure, cast, CFUNCTYPE, c_int, c_uint, c_void_p, c_bool, sizeof, Union, c_ushort, c_ulong, c_long, c_char, c_char_p, WINFUNCTYPE
from comtypes import GUID
from ctypes.wintypes import HANDLE, DWORD, USHORT, HWND, WPARAM, ULONG, LONG, UINT, BYTE
WNDPROC = WINFUNCTYPE(c_long, c_int, c_uint, c_int, c_int)

argtypeList = [c_int, c_char_p, c_char_p, c_int, c_int, c_int, c_int, c_int, c_int, c_int, c_int, c_int]


class WNDCLASS(Structure):
    _fields_ = [('style', c_uint), ('lpfnWndProc', WNDPROC), ('cbClsExtra', c_int), ('cbWndExtra', c_int), ('hInstance', c_int), ('hIcon', c_int),
                ('hCursor', c_int), ('hbrBackground', c_int), ('lpszMenuName', c_char_p), ('lpszClassName', c_char_p)]


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
