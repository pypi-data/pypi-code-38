import re
import struct

from .portrequest import generate_port_message


class PortCommand:
    def __init__(
        self,
        module,
        name,
        byteid=None,
        receivetype=None,
        sendtype=None,
        receivefunction=None,
        sendfunction=None,
        arduino_code=None,
    ):
        global FIRSTFREEBYTEID
        self.module = module

        self.sendlength = struct.calcsize(sendtype) if sendtype is not None else 0
        self.receivelength = (
            struct.calcsize(receivetype) if receivetype is not None else 0
        )

        self.sendtype = sendtype
        self.receivetype = receivetype

        if sendfunction is None:
            sendfunction = self.defaultsendfunction

        self.sendfunction = sendfunction
        self.receivefunction = receivefunction
        self.name = re.sub(r"\s+", "", name, flags=re.UNICODE)
        if byteid == None:
            byteid = module.firstfreebyteid
        self.byteid = byteid
        self.arduino_code = ""
        self.set_arduino_code(arduino_code)

    def set_arduino_code(self, arduino_code):
        if arduino_code is not None:
            self.arduino_code = arduino_code.replace(
                "{BYTEID}", str(self.byteid)
            ).replace("{NAME}", str(self.name))
        else:
            self.arduino_code = ""

    def defaultsendfunction(self, numericaldata=None):
        if numericaldata is None:
            data = bytearray()
        else:
            data = struct.pack(self.sendtype, numericaldata)
        self.module.serialport.write(
            bytearray(generate_port_message(self.byteid, self.sendlength, *data))
        )

    def receive(self, bytearray):
        #print(self.receivetype,bytearray)
        self.receivefunction(self.module,struct.unpack(self.receivetype, bytearray)[0])
