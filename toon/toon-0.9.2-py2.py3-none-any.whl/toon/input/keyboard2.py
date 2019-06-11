import os
import evdev
from evdev import ecodes, categorize
from glob import glob
from select import select
from toon.input import BaseDevice, make_obs
import ctypes
# find all keyboards


def make_unique(lst):
    out = []
    for dev in lst:
        if dev not in out:
            out.append(dev)
    return out


def find_devices(device_type):
    # device_type == mouse, kbd, joystick
    base_str = '/dev/input/by-%s/*-event-*'
    id_path = glob(base_str % 'id')
    path_path = glob(base_str % 'path')
    device_paths = id_path + path_path

    dev_paths = []
    for dev in device_paths:
        dev_type = dev.rsplit('-', 1)[1]
        actual_path = os.path.realpath(dev)
        if dev_type == device_type:  # mouse, joystick
            dev_paths.append(actual_path)
    dev_paths = make_unique(dev_paths)
    return [evdev.InputDevice(path) for path in dev_paths]


class KeyEvent(ctypes.Structure):
    # only press (true) and release (false), no repeating
    _fields_ = [('key', ctypes.c_char),
                ('value', ctypes.c_bool)]


class Keyboard(BaseDevice):
    Key = make_obs('Key', (1,), KeyEvent)

    def __init__(self, keys=None, **kwargs):
        self.keys = [k.upper() for k in keys]  # optional, only look at subset of keys
        self.devs = find_devices('kbd')
        super(Keyboard, self).__init__(**kwargs)

    def enter(self):
        self.read()

    def read(self):
        r, w, x = select(self.devs, [], [])
        time = self.clock()
        events = []
        for dev in r:
            for event in dev.read():
                if event.type == ecodes.EV_KEY and event.value != 2:
                    key_str = ecodes.keys[event.code][4:]
                    if self.keys:  # if we have keys, filter
                        if key_str in self.keys:
                            events.append(self.Key(time, KeyEvent(key_str.encode(), event.value)))
                    else:
                        events.append(self.Key(time, KeyEvent(key_str.encode(), event.value)))
        return events


if __name__ == '__main__':
    import time
    from toon.input.mpdevice import MpDevice
    dev = MpDevice(Keyboard(keys=['a', 's', 'd', 'f']))
    with dev:
        start = time.time()
        while time.time() - start < 10:
            dat = dev.read()
            if dat is not None:
                print(dat)
            time.sleep(0.016)
