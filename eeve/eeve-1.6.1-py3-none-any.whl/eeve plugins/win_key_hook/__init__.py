import ctypes
import collections
import threading
import travel_backpack
import win32con
import win32api
import win32gui
from typing import Callable
import atexit
from win_key_hook.input_parser import InputParser
from uuid import uuid4


class WinLowLevelHook(metaclass=travel_backpack.Singleton):
    hook_thread:threading.Thread
    def __init__(self, keyboard_callback, mouse_callback):
        self.keyboard_callback = keyboard_callback
        self.mouse_callback = mouse_callback
        self.KeyboardEvent = collections.namedtuple('KeyboardEvent', ['event_type', 'key_code', 'scan_code', 'alt_pressed', 'time', 'extra_info'])
        self.MouseEvent = collections.namedtuple('MouseEvent', ['event_type', 'point', 'wheel_direction', 'injection', 'time'])

        self.hook_id_keyboard = None
        self.hook_id_mouse = None
        self.running = False

    def stop(self):
        self.running =False

    def start(self, asynchronous=True):
        if asynchronous:
            print('async hook')
            t = threading.Thread(target=self.start, kwargs={'asynchronous': False})
            self.running = True
            t.start()
            return t

        print('starting hook')
        keyboard_event_types = {
            win32con.WM_KEYDOWN: 'key down',
            win32con.WM_KEYUP: 'key up',
            0x104: 'key down',  # WM_SYSKEYDOWN, used for Alt key.
            0x105: 'key up',  # WM_SYSKEYUP, used for Alt key.
        }

        # WM_LBUTTONDOWN, WM_LBUTTONUP, WM_MOUSEMOVE, WM_MOUSEWHEEL, WM_MOUSEHWHEEL, WM_RBUTTONDOWN, or WM_RBUTTONUP.
        mouse_event_types = {
            win32con.WM_RBUTTONDOWN: 'RMB down',
            win32con.WM_RBUTTONUP: 'RMB up',
            win32con.WM_LBUTTONDOWN: 'LMB down',
            win32con.WM_LBUTTONUP: 'LMB up',
            0x0207: 'MMB down',
            0x0208: 'MMB up',
            win32con.WM_MOUSEWHEEL: 'Wheel',
            0x020E: 'Horizontal Wheel',  # win32con.WM_MOUSEHWHEEL
            win32con.WM_MOUSEMOVE: 'mouse move'
        }

        def low_level_keyboard_handler(nCode, wParam, lParam):
            event = (nCode,
                     self.KeyboardEvent(
                         event_type=keyboard_event_types[wParam],
                         key_code=lParam[0] & 0xFFFFFFFF,
                         scan_code=lParam[1] & 0xFFFFFFFF,
                         alt_pressed=lParam[2] == 32,
                         time=lParam[3] & 0xFFFFFFFF if lParam[3] is not None else 0,
                         extra_info=lParam[4]))  # unsigned int 64 for 32bit
            # Be a good neighbor and call the next hook.
            if self.keyboard_callback(event):
                return ctypes.windll.user32.CallNextHookEx(self.hook_id_keyboard, nCode, wParam, lParam)
            else:
                print("#")
                return 1

        def low_level_mouse_handler(nCode, wParam, lParam):
            event = (nCode,
                     self.MouseEvent(
                         event_type=mouse_event_types.get(wParam, f'unknown ({hex(wParam)})'),
                         point=lParam[0],
                         wheel_direction=lParam[1],
                         injection=lParam[2],
                         time=lParam[3]))

            if self.mouse_callback(event):
                # Be a good neighbor and call the next hook.
                return ctypes.windll.user32.CallNextHookEx(self.hook_id_mouse, nCode, wParam, lParam)
            else:
                return 1

        CMPFUNC = ctypes.CFUNCTYPE(ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.POINTER(ctypes.c_void_p))
        # Convert the Python handler into C pointer.
        pointer_keyboard = CMPFUNC(low_level_keyboard_handler)
        pointer_mouse = CMPFUNC(low_level_mouse_handler)

        # Hook both key up and key down events for common keys (non-system).
        try:
            wh_keyboard_lo_level = win32con.WH_KEYBOARD_LL
            wh_mouse_low_level = win32con.WH_MOUSE_LL
            p_keyoard = pointer_keyboard
            p_mouse = pointer_mouse
            module_handle = win32api.GetModuleHandle(None)
            module_handle = 0
            self.hook_id_keyboard = ctypes.windll.user32.SetWindowsHookExA(wh_keyboard_lo_level, p_keyoard, module_handle, 0)
            self.hook_id_mouse = ctypes.windll.user32.SetWindowsHookExA(wh_mouse_low_level, p_mouse, module_handle, 0)

        except Exception as ex:
            print(ex)

        # Register to remove the hook when the interpreter exits.
        # Unfortunately a
        # try/finally block doesn't seem to work here.
        atexit.register(ctypes.windll.user32.UnhookWindowsHookEx, self.hook_id_keyboard)
        atexit.register(ctypes.windll.user32.UnhookWindowsHookEx, self.hook_id_mouse)

        while self.running:
            #peek_result, msg = win32gui.PeekMessage(None, 0, 0, 1)
            result, msg = win32gui.GetMessage(None, 0, 0)
            print('got msg:', msg, result)
            win32gui.TranslateMessage(msg)
            #print('translated')
            win32gui.DispatchMessage(msg)
            #print('sent')
            #sleep(0.5)
            pass


class BaseKeyInfo:
    def __init__(self, chain: str, func: Callable, allowed_tag: str):
        print(f'[{chain}]')
        chain += 'Z'
        self.chain = []
        temp_w = None
        for c in chain:
            if not c.isupper():
                temp_w += c
            else:
                if temp_w:
                    self.chain.append(temp_w)
                temp_w = c

        self.func = func
        self.currentIndex = 0
        self.allowed_tag = allowed_tag.lower() if allowed_tag is not None else None
        for c in self.chain:
            print('key in chain:', c)

    def can_run(self) -> bool:
        if self.allowed_tag is None:
            return True
        else:
            if not KeyHookWrapper().allowed_tags:
                return False
            else:
                if self.allowed_tag in KeyHookWrapper().allowed_tags or self.allowed_tag == 'any' or 'any' in KeyHookWrapper().allowed_tags:
                    return True
                else:
                    return False

    def next(self, char: str) -> bool:
        if self.can_run():
            char = char.capitalize()
            return self._next(char)
        else:
            return False

    def _next(self, char: str) -> bool:
        raise NotImplementedError('This method must be implemented by child classes')


class KeychainInfo(BaseKeyInfo):
    def _next(self, char: str) -> bool:
        if char == self.chain[self.currentIndex]:
            self.currentIndex += 1
        elif char == self.chain[0]:
            self.currentIndex = 1
        else:
            self.currentIndex = 0
        # print('index', self.currentIndex)
        # print(char, self.currentIndex)

        if self.currentIndex == len(self.chain):
            self.currentIndex = 0
            self.func()
            return True
        else:
            return False


class KeyCombinationInfo(BaseKeyInfo):
    def _next(self, char):
        res = True
        kd = [k.lower() for k in KeyHookWrapper().keys_down]
        for c in self.chain:
            res = res and (c.lower() in kd)
            #print(res, c)

        if res:
            self.func()
        return res


class KeyHookWrapper(metaclass=travel_backpack.Singleton):
    def __init__(self):
        print('initializing Key Hook Wrapper')
        self.keyboard_callbacks = dict()
        self.mouse_down_callbacks = dict()
        self.mouse_move_callbacks = dict()
        self.keychains = dict()
        self.allowed_tags = set()
        self.keys_down = set()

        def keyboard_callback(key_name):
            ret = True
            for cb in self.keyboard_callbacks.values():
                cb(key_name=key_name)

            for kc, swallow_key in self.keychains.values():
                if kc.next(char=key_name):
                    if kc.allowed_tag is not None:
                        self.allowed_tags = set()
                    if swallow_key:
                        ret = False

            return ret and not self.allowed_tags

        def mouse_hook_callback(info):
            nCode, event = info
            nCode  # just to stop error on line above and keep the name

            if event.event_type == 'LMB down':
                for cb in self.mouse_down_callbacks.values():
                    cb(key_name=event.event_type,
                       point=event.point,
                       wheel_direction=event.wheel_direction,
                       injection=event.injection,
                       time=event.time)
            elif event.event_type == 'mouse move':
                for cb in self.mouse_move_callbacks.values():
                    cb(key_name=event.event_type, point=event.point, injection=event.injection, time=event.time)

            return True

        parser = InputParser(key_down_callback=keyboard_callback, key_up_callback=None, keys_down=self.keys_down)
        self.hook = WinLowLevelHook(parser.process_keyboard_event, mouse_hook_callback)

        print('Starting input hook')
        self.hook.start()

    def check_callbacks(self):
        if len(self.keyboard_callbacks) + \
            len(self.mouse_down_callbacks) +\
            len(self.mouse_move_callbacks) + \
            len(self.keychains) == 0:
            #self.hook.stop()
            ...

    def add_keyboard_callback(self, callback):
        uuid = uuid4()
        self.keyboard_callbacks[uuid] = callback
        return uuid

    def remove_keyboard_callback(self, uuid):
        del self.keyboard_callbacks[uuid]

    def add_mouse_down_callback(self, callback):
        uuid = uuid4()
        self.mouse_down_callbacks[uuid] = callback
        return uuid

    def remove_mouse_down_callback(self, uuid):
        del self.mouse_down_callbacks[uuid]

    def add_mouse_move_callback(self, callback):
        uuid = uuid4()
        self.mouse_move_callbacks[uuid] = callback
        return uuid

    def remove_mouse_move_callback(self, uuid):
        del self.mouse_move_callbacks[uuid]

    def add_keychain_callback(self, callback, keychain: str, swallow_key: bool, only_on_blocking_mode: bool):
        uuid = uuid4()
        self.keychains[uuid] = KeychainInfo(chain=keychain, func=callback, allowed_tag=only_on_blocking_mode), swallow_key
        return uuid

    def remove_keychain_callback(self, uuid):
        del self.keychains[uuid]

    def add_keycombination_callback(self, callback, keys: str, swallow_key: bool, only_on_blocking_mode: bool):
        uuid = uuid4()
        self.keychains[uuid] = KeyCombinationInfo(chain=keys, func=callback, allowed_tag=only_on_blocking_mode), swallow_key
        return uuid

    def remove_keycombination_callback(self, uuid):
        del self.keychains[uuid]


class RegisterKeyDown:
    def __init__(self, action):
        self.uuid = KeyHookWrapper().add_keyboard_callback(action)

    def unregister(self):
        KeyHookWrapper().remove_keyboard_callback(self.uuid)


class RegisterMouseDown:
    def __init__(self, action):
        self.uuid = KeyHookWrapper().add_mouse_down_callback(action)

    def unregister(self):
        KeyHookWrapper().remove_mouse_down_callback(self.uuid)


class RegisterMouseMove:
    def __init__(self, action):
        self.uuid = KeyHookWrapper().add_mouse_move_callback(action)

    def unregister(self):
        KeyHookWrapper().remove_mouse_move_callback(self.uuid)


class RegisterKeychain:
    def __init__(self, action, keychain: str, swallow_key=False, only_on_blocking_mode=None):
        self.uuid = KeyHookWrapper().add_keychain_callback(action, keychain, swallow_key, only_on_blocking_mode)

    def unregister(self):
        KeyHookWrapper().remove_keychain_callback(self.uuid)


class RegisterKeyCombination:
    def __init__(self, action, keys: str, swallow_last_key=False, only_on_blocking_mode=None):
        self.uuid = KeyHookWrapper().add_keycombination_callback(action, keys, swallow_last_key, only_on_blocking_mode)

    def unregister(self):
        KeyHookWrapper().remove_keychain_callback(self.uuid)


class SetKeyBlockingMode:
    def run(self, value='any'):
        value = value.lower()
        kw = KeyHookWrapper()
        if value in kw.allowed_tags:
            print('Removing', value, 'from allowed tags')
            kw.allowed_tags.remove(value)
        else:
            print('Adding', value, 'to allowed tags')
            kw.allowed_tags.add(value)

        print('key blocking mode is', kw.allowed_tags)


triggers = {
    'key down': RegisterKeyDown,
    'mouse down': RegisterMouseDown,
    'mouse move': RegisterMouseMove,
    'keychain': RegisterKeychain,
    'keys down': RegisterKeyCombination
}
actions = {'toggle keychain mode': SetKeyBlockingMode}


def main():
    print('initializing Key Hook')

    def keyboard_callback(key_name):
        print(key_name)
        return True

    def mouse_hook_callback(info):
        nCode, event = info
        nCode  # just to stop error on line above and keep the name
        event
        return True

    parser = InputParser(key_down_callback=keyboard_callback, key_up_callback=None)
    hook = WinLowLevelHook(parser.process_keyboard_event, mouse_hook_callback)

    print('Starting input hook')
    hook.start()


if __name__ == '__main__':
    main()
