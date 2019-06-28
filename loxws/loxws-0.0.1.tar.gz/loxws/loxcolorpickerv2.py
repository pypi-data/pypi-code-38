import logging

_LOGGER = logging.getLogger(__name__)

class LoxColorPickerV2:
    """Class for node abstraction."""

    def __init__(self, id, name, device_type):
        self._id = id
        self._name = name
        self._device_type = device_type
        self._state = False
        self._brightness = 0
        self._color_temp = None
        self._hs_color = [0,0]
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
        if self._device_type == "ColorPickerV2" and stateName == "color":
            _LOGGER.debug("{0} {1} Set ColorPickerV2 - color={2}".format(self._id, self._name, value))

            if value.startswith("hsv"):
                #hsv(0,0,100)
                hsv = value.strip("hsv()").split(",")
                #_LOGGER.debug("  hsv: {0} {1}".format(value, hsv))
                self._brightness = int(hsv[2]) * 2.55
                self._hs_color = [ float(hsv[0]), float(hsv[1]) ]

                if self._brightness > 0:
                    self._state = True
                else:
                    self._state = False

            elif value.startswith("temp"):
                #temp(100,4783)
                temp = value.strip("temp()").split(",")
                #_LOGGER.debug("  temp: {0} {1}".format(value, temp))
                #############################
                # TODO - Do something????
                #############################

                #self._brightness = int(temp[2]) * 2.55
                #self._hs_color = [ float(temp[0]), float(temp[1]) ]

                #if self._brightness > 0:
                #    self._state = True
                #else:
                #    self._state = False

            #_LOGGER.debug("Update ColorPickerV2: {0}".format(self._name))
            self.async_update()
        elif self._device_type == "LightControllerV2" and stateName == "moodList":
            _LOGGER.debug("{0} {1} Set {2} - {3}={4}".format(self._id, self._name, self._device_type, stateName, value))
            #device.add_modes(value)

        else:
            _LOGGER.debug("{0} {1} NotSet {2} - {3}={4}".format(self._id, self._name, self._device_type, stateName, value))
