# Copyright 2018 Intel Corporation.

import pkg_resources
try:
    __version__ = pkg_resources.get_distribution("onnx_plaidml").version
except pkg_resources.DistributionNotFound:
    __version__ = 'local'

class Error(Exception):
    pass


class DeviceNotFoundError(Error):

    def __init__(self, device_name, devices_available):
        self.device_name = device_name
        self.devices_available = devices_available
        if devices_available == []:
            devmsg = 'perhaps you need to run \'plaidml-setup\' to configure devices on this machine'
        elif len(devices_available) == 1:
            devmsg = 'the only available device is \'{}\''.format(devices_available[0])
        elif len(devices_available) == 2:
            devmsg = 'the available devices are \'{}\' and \'{}\''.format(
                devices_available[0], devices_available[1])
        else:
            devmsg = 'the available devices are {}, and \'{}\''.format(
                ', '.join(['\'{}\''.format(d)
                           for d in devices_available[:-1]]), devices_available[-1])
        if device_name:
            msg = 'Unable to find device \'{}\'; {}'.format(device_name, devmsg)
        else:
            msg = 'No default device configured; {}'.format(devmsg)
        super(DeviceNotFoundError, self).__init__(msg)


class TooManyDefaultDevicesError(Error):

    def __init__(self, device_ids):
        self.device_ids = device_ids
        super(TooManyDefaultDevicesError, self).__init__(
            'Too many default devices specified (found: \'{}\'); run \'plaidml-setup\' to configure devices on this machine'.
            format('\', \''.join(device_ids)))
