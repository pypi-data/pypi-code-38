from . import defaultcodes


class Pin:
    DIGITAL_OUT = 0

    def __init__(self, name, defaultposition, portcommand, pintype=0):
        self.name = name
        self.portcommand = portcommand
        self.position = defaultposition
        self.pintype = pintype

        if pintype == self.DIGITAL_OUT:
            self.portcommand.set_arduino_code(
                defaultcodes.DEFAULTCODES["setpin_output"]
            )
        else:
            self.portcommand.set_arduino_code(
                defaultcodes.DEFAULTCODES["setpin_output"]
            )

    def arduinoMode(self):
        if self.pintype == self.DIGITAL_OUT:
            return "OUTPUT"
        else:
            return "OUTPUT"

    def to_json(self):
        return self.position
