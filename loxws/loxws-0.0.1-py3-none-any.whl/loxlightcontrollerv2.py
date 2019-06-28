import logging

_LOGGER = logging.getLogger(__name__)

class LoxLightControllerV2:
    """Class for LightControllerV2 abstraction."""

    def __init__(self, id, name, device_type):
        self._id = id
        self._name = name
        self._device_type = device_type
        self.async_callbacks = []

    @property
    def id(self):
        return self._id

    @property
    def name(self):
        return self._name

    @property
    def device_type(self):
        return self._device_type

    @property
    def manufacturername(self):
        return 'Loxone'    

    def register_async_callback(self, async_callback):
        #_LOGGER.debug("register_async_callback")
        self.async_callbacks.append(async_callback)

    def unregister_async_callback(self, callback):
        #_LOGGER.debug("unregister_async_callback")
        if callback in self.async_callbacks:
            self.async_callbacks.remove(callback)

    def async_update(self):
        for async_signal_update in self.async_callbacks:
            async_signal_update()


    def set_value(self, stateName, value):
        if self._device_type == "LightControllerV2" and stateName == "moodList":
            _LOGGER.debug("{0} {1} Set {2} - {3}={4}".format(self._id, self._name, self._device_type, stateName, value))
            #device.add_modes(value)

        else:
            _LOGGER.debug("{0} {1} NotSet {2} - {3}={4}".format(self._id, self._name, self._device_type, stateName, value))
