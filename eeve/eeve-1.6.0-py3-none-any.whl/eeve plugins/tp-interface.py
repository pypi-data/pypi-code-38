from pyHS100 import Discover
import travel_backpack
import time


class SmartDeviceContainer:
    def __init__(self, dev):
        self.device = dev
        self.hw_id = self.device.hw_info['hwId']
        self.alias = self.device.alias
        self.disconnect_count = 0

    def __hash__(self):
        h = hash(self.hw_id)
        #print('hash:', h)
        return h

    def __eq__(self, other):
        return self.hw_id == other.hw_id

    def __repr__(self):
        alias = self.alias + ' (offline)'
        try:
            alias = self.device.alias
        except:
            pass
        return alias


class Discoverer(metaclass=travel_backpack.Singleton):
    def __init__(self):
        print('inited')
        self.timeout = 1
        self.time_between_pings = 0
        self.threshold = 10

        self.single_connect_event = dict()
        self.single_disconnect_event = dict()

        self.multi_connect_event = dict()
        self.multi_disconnect_event = dict()

        self.discoverer_thread = self.discoverer()
        print('end init')

    def set_params(self, timeout, time_between_pings, threshold):
        self.timeout = timeout
        self.time_between_pings = time_between_pings
        self.threshold = threshold

    @travel_backpack.threadpool
    def discoverer(self):
        self.current_device_set = set()
        while True:
            #print('\nloop start')
            new_device_set = set()
            for ip, dev in Discover.discover(timeout=self.timeout).items():
                try:
                    dev = SmartDeviceContainer(dev)
                    new_device_set.add(dev)
                except:
                    pass

            offline_devices = self.current_device_set - new_device_set
            #print('offline devices:'.ljust(18), (offline_devices) or '-')
            for dev in offline_devices:
                if dev.disconnect_count > self.threshold:
                    print(dev, 'disconnected')
                    for e in self.single_disconnect_event.values():
                        e(device=dev.device)
                else:
                    dev.disconnect_count += 1
                    print(dev.alias, 'hwid:', dev.hw_id, 'id:', id(dev), 'dcnts:', dev.disconnect_count)
                    new_device_set.add(dev)

            offline_devices = self.current_device_set - new_device_set
            for e in self.multi_disconnect_event.values():
                e(device_list=[d.device for d in offline_devices])

            new_devices = new_device_set - self.current_device_set
            #print('new_devices:'.ljust(18), (new_devices) or '-')
            for e in self.multi_connect_event.values():
                e(device_list=[d.device for d in new_devices])
            for dev in new_devices:
                print(dev, 'connected')
                for e in self.single_connect_event.values():
                    e(device=dev.device, is_on=dev.device.is_on)

            #print('noch:'.ljust(18), (new_device_set & self.current_device_set) or '-')
            self.current_device_set = new_device_set

            time.sleep(self.time_between_pings)


class RegisterTrigger:
    def __init__(self, action, trigger_status, mult='single', timeout=1, time_between_pings=2, threshold=10):
        from uuid import uuid4
        self.uuid = uuid4()
        self.mult = mult
        self.trigger_status = trigger_status
        d = Discoverer()
        if trigger_status == 'connect':
            if mult == 'single':
                d.single_connect_event[self.uuid] = action
            elif mult == 'multi':
                d.multi_connect_event[self.uuid] = action
        elif trigger_status == 'disconnect':
            if mult == 'single':
                d.single_disconnect_event[self.uuid] = action
            elif mult == 'multi':
                d.multi_disconnect_event[self.uuid] = action

        d.set_params(timeout=timeout, time_between_pings=time_between_pings, threshold=threshold)
        print('trigger registered')

    def unregister(self):
        d = Discoverer()
        if self.trigger_status == 'connect':
            if self.mult == 'single':
                del d.single_connect_event[self.uuid]
            elif self.mult == 'multi':
                del d.multi_connect_event[self.uuid]
        elif self.trigger_status == 'disconnect':
            if self.mult == 'single':
                del d.single_disconnect_event[self.uuid]
            elif self.mult == 'multi':
                del d.multi_disconnect_event[self.uuid]


def set_device_property(device, brightness=None, temperature=None, is_on=None):
    if type(device) is str:
        print('Getting discoverer')
        d = Discoverer()
        for dev_wrapper, dev in [(dv, dv.device) for dv in d.current_device_set if dv.alias == device]:
            print('setting property from', dev_wrapper.alias)
            set_device_property(dev, brightness, temperature, is_on)

    else:
        if is_on is not None:
            if is_on:
                device.turn_on()
            else:
                device.turn_off()
        if brightness is not None:
            device.brightness = brightness
        if temperature is not None:
            device.color_temp = temperature


actions = {'set TP-Link device property': {'run': set_device_property, 'init': Discover}}
triggers = {'TP-Link device': RegisterTrigger}

if __name__ == "__main__":

    def a(*args, **kwargs):
        print('==>', *args, **kwargs)

    def b(*args, **kwargs):
        print('<==', *args, **kwargs)

    RegisterTrigger(a, 'connect')

    RegisterTrigger(b, 'disconnect')
    while True:
        time.sleep(10 * 60)
