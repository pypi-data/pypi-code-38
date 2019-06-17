import ctypes
import re


def get_display_name():
    GetUserNameEx = ctypes.windll.secur32.GetUserNameExW
    NameDisplay = 3

    size = ctypes.pointer(ctypes.c_ulong(0))
    GetUserNameEx(NameDisplay, None, size)

    nameBuffer = ctypes.create_unicode_buffer(size.contents.value)
    GetUserNameEx(NameDisplay, nameBuffer, size)
    return nameBuffer.value


EnumWindows = ctypes.windll.user32.EnumWindows

EnumWindowsProc = ctypes.WINFUNCTYPE(
    ctypes.c_bool, ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int)
)


def HandleError(func):
    def _handler(*args, **kwargs):
        result = func(*args, **kwargs)
        if result == 0:
            raise Exception("Error!")
        return result

    return _handler


GetWindowText = ctypes.windll.user32.GetWindowTextW
GetWindowTextLength = ctypes.windll.user32.GetWindowTextLengthW
IsWindowVisible = ctypes.windll.user32.IsWindowVisible

CloseWindow = ctypes.windll.user32.CloseWindow
ShowWindow = ctypes.windll.user32.ShowWindow
BringWindowToTop = HandleError(ctypes.windll.user32.BringWindowToTop)
SetForegroundWindow = HandleError(ctypes.windll.user32.SetForegroundWindow)
SetWindowPos = HandleError(ctypes.windll.user32.SetWindowPos)

GetWindowPlacement = ctypes.windll.user32.GetWindowPlacement
GetDesktopWindow = ctypes.windll.user32.GetDesktopWindow
GetClipboardData = ctypes.windll.user32.GetClipboardData


class POINT(ctypes.Structure):
    _fields_ = [("x", ctypes.c_long), ("y", ctypes.c_long)]


class RECT(ctypes.Structure):
    _fields_ = [
        ("left", ctypes.c_long),
        ("top", ctypes.c_long),
        ("right", ctypes.c_long),
        ("bottom", ctypes.c_long),
    ]


class WindowPlacement(ctypes.Structure):
    _fields_ = [
        ("length", ctypes.c_uint),
        ("flags", ctypes.c_uint),
        ("showCmd", ctypes.c_uint),
        ("ptMinPosition", POINT),
        ("ptMaxPosition", POINT),
        ("rcNormalPosition", RECT),
        ("rcDevices", RECT),
    ]

    @property
    def top(self):
        return self.rcNormalPosition.top

    @property
    def left(self):
        return self.rcNormalPosition.left

    @property
    def bottom(self):
        return self.rcNormalPosition.bottom

    @property
    def right(self):
        return self.rcNormalPosition.right

    @staticmethod
    def get(handle):
        winpl = WindowPlacement()
        # print(index, title, str(handle))
        # ShowWindow(handle, 9)
        # BringWindowToTop(handle)
        # SetForegroundWindow(handle)
        GetWindowPlacement(handle, ctypes.byref(winpl))
        return winpl


class Window(object):
    """A wrapper around a Window Handle object.

    """

    def __init__(self, handle):
        self.handle = handle

    @property
    def title(self):
        if not hasattr(self, "_text"):
            length = GetWindowTextLength(self.handle)
            buff = ctypes.create_unicode_buffer(length + 1)
            GetWindowText(self.handle, buff, length + 1)
            self._text = buff.value
        return self._text

    @property
    def placement(self):
        if not hasattr(self, "_placement"):
            self._placement = WindowPlacement.get(self.handle)
        return self._placement

    @property
    def desktop(self):
        if not hasattr(self, "_desktop"):
            self._desktop = Desktop()
        return self._desktop

    @property
    def visible(self):
        return IsWindowVisible(self.handle)

    @property
    def top(self):
        return self.placement.top

    @property
    def right(self):
        return self.placement.right

    @property
    def bottom(self):
        return self.placement.bottom

    @property
    def left(self):
        return self.placement.left

    @property
    def width(self):
        return self.right - self.left

    @property
    def height(self):
        return self.bottom - self.top

    def bring_to_front(self):
        ShowWindow(self.handle, 9)
        SetForegroundWindow(self.handle)

    def set_position(self, top, left, width, height):
        SetWindowPos(self.handle, 0, top, left, width, height, 0)

    def anchor_top_left(self):
        width = int(self.desktop.width / 2)
        height = int(self.desktop.height / 2)
        self.set_position(0, 0, width, height)

    def anchor_left(self):
        width = int(self.desktop.width / 2)
        self.set_position(0, 0, width, self.desktop.height)

    def get_window_text(handle):
        length = GetWindowTextLength(handle)
        buff = ctypes.create_unicode_buffer(length + 1)
        GetWindowText(handle, buff, length + 1)
        return buff.value

    @staticmethod
    def iter_windows():
        windows = []

        def enumerate_windows(hwnd, lParam):
            windows.append(Window(hwnd))
            return True

        EnumWindows(EnumWindowsProc(enumerate_windows), 0)

        for entry in windows:
            yield entry

    @staticmethod
    def find(name):
        windows = list(Window.find_all(name))
        if windows:
            return windows[0]
        return []

    @staticmethod
    def find_all(name):
        def _match_in(title):
            return name in title

        matcher = _match_in

        if isinstance(name, re.Pattern):
            regex = re.compile(name)

            def _match_re(title):
                return regex.match(title)

            matcher = _match_re

        for wind in Window.iter_windows():
            if not wind.visible:
                continue
            if matcher(wind.title):
                yield wind


class Desktop(Window):
    def __init__(self):
        dsktp = GetDesktopWindow()
        super(Desktop, self).__init__(dsktp)


if __name__ == "__main__":

    # chrome = None
    #
    # for index, wind in enumerate(Window.iter_windows(), 1):
    #     if not wind.visible:
    #         continue
    #     print((f'{index:0>3} "{wind.title}" ({wind.handle}) '
    #            f'({wind.top}, {wind.right}, '
    #            f'{wind.bottom}, {wind.left})'))
    #     if 'Google Chrome' in wind.title:
    #         chrome = wind
    for win in Window.iter_windows():
        if win.visible:
            print(win.title)

    chrome = Window.find(re.compile("^.* - Google Chrome$"))

    print(f"{chrome.title}")
    print(f"Chrome: {chrome.top} {chrome.left}, {chrome.width} x {chrome.height}")

    chrome.bring_to_front()
    chrome.anchor_left()
