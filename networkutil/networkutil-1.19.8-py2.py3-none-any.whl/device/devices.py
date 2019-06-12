# encoding: utf-8

import logging_helper
from configurationutil import (CfgItems,
                               CfgItem)
from classutils.decorators import deprecated
from ..endpoint_config import Endpoints
from .config import register_device_config
from ._constants import (DEVICE_CONFIG,
                         DeviceConstant)

logging = logging_helper.setup_logging()


class Device(CfgItem):

    @deprecated
    def get_endpoint(self,
                     api,
                     environment):
        # TODO: Remove this as its not used, leaving in place for the time being but not migrating to new ep config.
        return Endpoints().get_endpoint(api=api,
                                        environment=self.__dict__[environment])


class Devices(CfgItems):

    def __init__(self):
        super(Devices, self).__init__(cfg_fn=register_device_config,
                                      cfg_root=DEVICE_CONFIG,
                                      key_name=DeviceConstant.name,
                                      has_active=DeviceConstant.active,
                                      item_class=Device)

    @property
    def default_device(self):

        default_devices = [self[device] for device in self if self[device].default]

        if len(default_devices) == 1:
            return default_devices[0]

        elif len(default_devices) == 0:
            # If we get to here no default device is configured
            self._set_first_configured_device_as_default()
            return self.default_device

        else:
            default_device = [device for device in default_devices if device.name != u'Example Device'][0]
            logging.warning(u'More than one default Device is configured. Using {name}'
                            .format(name=default_device.name))
            return default_device

    def get_device_by_id(self,
                         device_id):
        return self.get_item_by_key(key=DeviceConstant.id,
                                    value=device_id)

    def get_default_device_or_first_configured(self):

        """
        Attempts to retrieve the default device.
        If no default device configured then it will return the first active device.
        If no active devices then it will return the first device it can get!
        """

        try:
            return self.default_device

        except LookupError:

            try:
                return self.get_active_items()[0]

            except IndexError:
                return [self[item] for item in self._items()][0]

    def _set_first_configured_device_as_default(self):

        devices = [self[item] for item in self._items()]

        device = devices[0]
        device.default = True
        device.save_changes()

        for device in devices[1:]:
            device.default = False
            device.save_changes()
