import logging

_LOGGER = logging.getLogger(__name__)

class LoxDimmer:
    """Class for node abstraction."""

    def __init__(self, id, name, device_type):
        self._id = id
        self._name = name
        self._device_type = device_type
        self._state = False
        self._brightness = 0
        self._color_temp = None
        self._hs_color = [0,0]
        self.count = 0
        self.async_callbacks = []

    #def register_device_updated_cb(self, device_updated_cb):
    #    """Register device updated callback."""
    #    self.device_updated_cbs.append(device_updated_cb)

    #def unregister_device_updated_cb(self, device_updated_cb):
    #    """Unregister device updated callback."""
    #    self.device_updated_cbs.remove(device_updated_cb)

    #async def after_update(self):
    #    """Execute callbacks after internal state has been changed."""
    #    for device_updated_cb in self.device_updated_cbs:
    #        # pylint: disable=not-callable
    #        await device_updated_cb(self)
    
            
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

    @property
    def state(self):
        return self._state

    @property
    def brightness(self):
        return self._brightness

    @property
    def color_temp(self):
        return self._color_temp

    @property
    def hs_color(self):
        return self._hs_color

    def register_async_callback(self, async_callback):
        #_LOGGER.debug("register_async_callback")
        self.async_callbacks.append(async_callback)

    def unregister_async_callback(self, callback):
        #_LOGGER.debug("unregister_async_callback")
        if callback in self.async_callbacks:
            self.async_callbacks.remove(callback)

    def async_update(self):

        for async_signal_update in self.async_callbacks:
            #_LOGGER.debug("  doing update callback")
            async_signal_update()

    def set_value(self, stateName, value):
        if self._device_type == "Switch" and stateName == "active":
            _LOGGER.debug("{0} {1} Set Switch - active={2}".format(self._id, self._name, value))
            if value == 1: 
                self._state = True
                self._brightness = 255
            else:
                self._state = False
                self._brightness = 0

            #_LOGGER.debug("Update Switch: {0}".format(device.name))
            self.async_update()

        elif self._device_type == "Dimmer" and stateName == "position":
            _LOGGER.debug("{0} {1} Set Dimmer - position={2}".format(self._id, self._name, value))
            self._brightness = value * 2.55
            if value > 0:
                self._state = True
            else:
                self._state = False

            #_LOGGER.debug("Update Dimmer: {0}".format(device.name))
            self.async_update()

        else:
            _LOGGER.debug("{0} {1} NotSet {2} - {3}={4}".format(self._id, self._name, self._device_type, stateName, value))
