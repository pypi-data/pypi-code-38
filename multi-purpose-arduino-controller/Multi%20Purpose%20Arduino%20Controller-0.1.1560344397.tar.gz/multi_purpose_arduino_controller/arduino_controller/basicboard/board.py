import time
from collections import OrderedDict

import numpy as np

from multi_purpose_arduino_controller.arduino_controller.arduino_variable import arduio_variable
from multi_purpose_arduino_controller.arduino_controller.basicboard import arduino_data
from multi_purpose_arduino_controller.arduino_controller.basicboard.ino_creator import InoCreator
from multi_purpose_arduino_controller.arduino_controller.basicboard.pin import Pin
from multi_purpose_arduino_controller.arduino_controller.portcommand import PortCommand
import inspect

MAXATTEMPTS = 3
IDENTIFYTIME = 2


# noinspection PyBroadException
class ArduinoBasicBoard:
    FIRMWARE = 0

    FIRSTFREEBYTEID = 0

    def get_first_free_byteid(self):
        ffbid = self.FIRSTFREEBYTEID
        self.FIRSTFREEBYTEID += 1
        return ffbid

    firstfreebyteid = property(get_first_free_byteid)

    firmware = arduio_variable(name='firmware', type='uint64_t', arduino_setter=False,default=-1)
    datarate = arduio_variable(name='datarate', type='uint32_t',default=200,minimum=1,eeprom=True)


    def __init__(self):
        self.inocreator = InoCreator(self)
        self.inocreator.add_creator(arduino_data.create)
        self._pins = dict()
        self.save_attributes = OrderedDict()
        self.static_attributes = set()
        self.free_digital_pins = list(range(2, 12))
        self.name = None
        self.port = None
        self.lastdata = None
        self.updatetime = 2
        self.identify_attempts = 0

        self.save_attributes.update(
            {
                "firmware": "int+",
                "port": "string",
                "id": "int+",
                "name": "string",
                "updatetime": "double+",
                "pins": "int+0",
            }
        )

        self.static_attributes.update(["firmware", "id", "port"])
        self.identified = False
        self.id = None
        self.portcommands = []
        self.serialport = None
        self.add_port_command(
            PortCommand(
                module=self,
                name="identify",
                receivetype="Q",
                sendtype="?",
                receivefunction=ArduinoBasicBoard.receive_id,
                byteid=self.firstfreebyteid,
                arduino_code="identified=data[0];uint64_t id = get_id();write_data(id,{BYTEID});",
            )
        )

        for attr, ard_var in self.get_arduino_vars().items():
            if ard_var.arduino_setter is not None:
                self.add_port_command(
                    PortCommand(
                        module=self,
                        byteid=self.get_first_free_byteid(),
                        name="set_" + ard_var.name,
                        sendtype=ard_var.sendtype,
                        receivetype=None,
                        receivefunction=ard_var.set_without_sending_to_board,
                        arduino_code=ard_var.arduino_setter,
                    )
                )
            if ard_var.arduino_getter is not None:
                self.add_port_command(
                    PortCommand(
                        module=self,
                        byteid=self.get_first_free_byteid(),
                        name="get_" + ard_var.name,
                        sendtype=None,
                        receivetype=ard_var.receivetype,
                        receivefunction=ard_var.set_without_sending_to_board,
                        arduino_code=ard_var.arduino_getter,
                    )
                )

    def get_arduino_vars(self):
        ardvars = {}
        classes = inspect.getmro(self.__class__)
        for cls in reversed(classes):
            for attr, ard_var in cls.__dict__.items():
                if isinstance(ard_var, arduio_variable):
                    ardvars[attr] = ard_var
        return ardvars


    def set_serial_port(self, serialport):
        self.serialport = serialport
        self.port = serialport.port
        if self.name is None:
            self.name = self.port

    def add_pin(self, pinname, defaultposition, pintype=Pin.DIGITAL_OUT):
        portcommand = PortCommand(
            module=self,
            name=pinname,
            receivetype="B",
            sendtype="B",
            receivefunction=lambda data: (ArduinoBasicBoard.set_pin(pinname, data, to_board=False)),
            byteid=self.firstfreebyteid,
        )
        pin = Pin(
            name=pinname,
            defaultposition=defaultposition,
            portcommand=portcommand,
            pintype=pintype,
        )
        self.set_pin(pinname, pin, to_board=False)
        self.add_port_command(portcommand)

    def get_first_free_digitalpin(self, catch=True):
        fp = self.free_digital_pins[0]
        if catch:
            self.free_digital_pins.remove(fp)
        return fp

    def identify(self):
        from multi_purpose_arduino_controller.arduino_controller.serialport import BAUDRATES
        for b in set([self.serialport.baudrate] + list(BAUDRATES)):
            self.identify_attempts = 0
            self.serialport.logger.info(
                "intentify with baud " + str(b) + " and firmware " + str(self.FIRMWARE)
            )
            try:
                self.serialport.baudrate = b
                while self.id is None and self.identify_attempts < MAXATTEMPTS:
                    self.get_portcommand_by_name("identify").sendfunction(0)
                    self.identify_attempts += 1
                    time.sleep(IDENTIFYTIME)
                if self.id is not None:
                    self.identified = True
                    break
            except Exception as e:
                self.serialport.logger.exception(e)
                pass
        if not self.identified:
            return False

        self.identified = False
        self.identify_attempts = 0
        while self.firmware == -1 and self.identify_attempts < MAXATTEMPTS:
            self.get_portcommand_by_name("get_firmware").sendfunction()
            self.identify_attempts += 1
            time.sleep(IDENTIFYTIME)
        if self.firmware > -1:
            self.identified = True
        return self.identified

    #def specific_identification(self):
    #    self.identified = False
    #    self.identify_attempts = 0
    #    while self._datarate <= 0 and self.identify_attempts < MAXATTEMPTS:
    #        self.get_portcommand_by_name("datarate").sendfunction(0)
    #        self.identify_attempts += 1
    #        time.sleep(IDENTIFYTIME)
    #    if self._datarate > 0:
    #        self.identified = True
    #    if not self.identified:
    #        return False

     #   return self.identified

    def receive_from_port(self, cmd, data):
        self.serialport.logger.debug(
            "receive from port cmd: " + str(cmd) + " " + str([i for i in data])
        )
        portcommand = self.get_portcommand_by_cmd(cmd)
        if portcommand is not None:
            portcommand.receive(data)
        else:
            self.serialport.logger.debug("cmd " + str(cmd) + " not defined")

    def add_port_command(self, port_command):
        if (
                self.get_portcommand_by_cmd(port_command.byteid) is None
                and self.get_portcommand_by_name(port_command.name) is None
        ):
            self.portcommands.append(port_command)
        else:
            self.serialport.logger.error(
                "byteid of "
                + str(port_command)
                + " "
                + port_command.name
                + " already defined"
            )

    def get_portcommand_by_cmd(self, byteid):
        for p in self.portcommands:
            if p.byteid == byteid:
                return p
        return None

    def get_portcommand_by_name(self, command_name):
        for p in self.portcommands:
            if p.name == command_name:
                return p
        return None

    def receive_id(self, data):
        self.id = int(np.uint64(data))

    def datapoint(self, name, data):
        self.lastdata = data
        if self.identified:
            self.serialport.add_datapoint(self,key=str(self.id) + "_"+str(name), y=data, x=None)

    def restore(self, data):
        for key, value in data.items():
            if key not in self.static_attributes:
                if getattr(self, key, None) != value:
                    setattr(self, key, value)

        for attr, ard_var in self.get_arduino_vars().items():
            if ard_var.save and attr in data:
                setattr(self, attr, data[attr])

    def set_pins(self, pindict):
        for pin_name, pin in pindict.items():
            self.set_pin(pin_name, pin)

    def get_pins(self):
        return self._pins

    pins = property(get_pins, set_pins)

    def set_pin(self, pin_name, pin, to_board=True):
        if isinstance(pin, Pin):
            if self._pins.get(pin_name, None) == pin:
                return
            elif self._pins.get(pin_name, None) is not None:
                if self._pins[pin_name].position == pin.position:
                    self._pins[pin_name] = pin
                    return
            else:
                self._pins[pin_name] = pin
        else:
            if pin_name in self._pins:
                if self._pins[pin_name].position == pin:
                    return
                else:
                    self._pins[pin_name].position = pin
            else:
                return
        try:
            self.serialport.logger.info(
                "set Pin " + pin_name + " to " + str(self._pins[pin_name].position)
            )
        except Exception as e:
            pass
        if to_board:
            self._pins[pin_name].portcommand.sendfunction(pin)

    def get_pin(self, pin_name):
        return self._pins.get(pin_name, None)

    def serialize_attribute(self, value):
        try:
            return value.to_json()
        except Exception as e:
            pass

        if isinstance(value, dict):
            return {key: self.serialize_attribute(val) for key, val in value.items()}
        if isinstance(value, list):
            return [self.serialize_attribute(val) for val in value]
        return value

    def save(self):
        data = {}
        for attribute in self.save_attributes:
            val = getattr(self, attribute, None)
            val = self.serialize_attribute(val)
            data[attribute] = val
        for attr, ard_var in self.get_arduino_vars().items():
            if ard_var.save:
                data[attr] = ard_var.value
        return data

    def get_board(self):
        board = {
            'arduino_variables': {}
        }
        for attr, ard_var in self.get_arduino_vars().items():
            board['arduino_variables'][attr] = {
                'form': ard_var.html_input.replace("{{value}}", str(getattr(self, attr, '')))
            }
        return board



    def create_ino(self):
        import inspect
        import os
        self.firmware = self.FIRMWARE
        ino = self.inocreator.create()
        dir = os.path.dirname(inspect.getfile(self.__class__))
        name = os.path.basename(dir)
        with open(os.path.join(dir, name + ".ino"), "w+") as f:
            f.write(ino)


if __name__ == "__main__":
    ins = ArduinoBasicBoard()
    ins.create_ino()