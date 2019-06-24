from enum import Enum, auto
from pyudev import Context, Monitor, Device
from contextlib import suppress
from typing import Tuple, Set
from .touchpad import TouchPad


class DeviceType(Enum):
    TouchPad = auto()
    USB = auto()
    Other = auto()


def identify(device: Device) -> DeviceType:
    """
    Attempt to identify what kind of input device it is.
    This can be tricky, because sometimes the drivers
    are not immediately obvious, and controllers like to impersonate
    an external mouse.

    Instead of trying to find a static property that only TouchPads have,
    we use the process of elimination to filter out common usb properties.

    Args:
        device : Device
            The device in question, traverses its parents as well.

    Returns:
        DeviceType
            The device indentity.

    .. note::
        If a device is improperly identified, it means it didn't get caught
        by any of the attribute filters.
    """
    def look(*items: Tuple[str, str]) -> Set['str']:
        found = set()
        for dev in [device, *device.ancestors]:
            for name, val in items:
                prop = dev.attributes.get(name)
                if prop and val in prop.decode().casefold():
                    found.add(val)
        return found

    props = look(
        ('removable', 'removable'),
        ('phys', 'usb'),
        ('name', 'mouse'),
    )

    is_pci = device.find_parent('pci')
    if {'removable', 'mouse'} & props or not is_pci:
        return DeviceType.USB

    # USB but not removable probably means it's a controller
    if 'usb' in props:
        return DeviceType.Other

    return DeviceType.TouchPad


class WatchDog:
    """
    The sentry for input device based events.
    """
    context = Context()

    _devices = set()
    _touchpad: TouchPad = None

    def __init__(self):
        self.monitor = Monitor.from_netlink(self.context)
        self.monitor.filter_by('input')

    def __refresh(self):
        for dev in self.context.list_devices(subsystem='input', sys_name='mouse*'):
            cls = identify(dev)

            if cls is DeviceType.TouchPad:
                if self._touchpad is None:
                    self._touchpad = TouchPad(dev)
                else:
                    raise ValueError('Found multiple TouchPads.')

            elif cls is DeviceType.USB:
                self._devices.add(dev)

        self.__update()

    def __on_device(self, device):
        action = getattr(self._devices, device.action)  # self._devices.add or self._devices.remove
        with suppress(KeyError):  # redundant
            action(device)
        self.__update()

    def __update(self):
        if self._devices and not self._touchpad.toggled:
            self._touchpad.disable()
        else:
            self._touchpad.enable()

    def start(self):
        self.__refresh()
        for device in iter(self.monitor.poll, None):
            valid: bool = all((
                'mouse' in device.sys_name,
                device.action in ('add', 'remove'),
                identify(device) is DeviceType.USB
            ))
            if valid:
                self.__on_device(device)

    def on_toggle(self, *args):
        self._touchpad.toggle()
        self.__update()
