import logging
import threading
import time

from json_dict import JsonDict

from multi_purpose_arduino_controller import python_communicator
from ..datalogger import DataLogger
from ..serialreader import serialdetector

AUTOCHECKPORTS = True
PORTCHECKTIME = 2


class SerialReader:
    def __init__(
            self,
            config: JsonDict = None,
            communicator: python_communicator.PythonCommunicator = None,
            logger=None,
            autocheckports=AUTOCHECKPORTS,
            port_check_time=PORTCHECKTIME,
            permanently_ignored_ports=None,
            datalogger: DataLogger = None,
            start_in_background=False
    ):

        self.ignored_ports = set()
        self.deadports = set()
        self.connected_ports = set()
        self.available_ports = set()
        self.identified_ports = set()

        self.datalogger = DataLogger() if datalogger is None else datalogger

        self.config = JsonDict("portdata.json") if config is None else config

        if permanently_ignored_ports is None:
            permanently_ignored_ports = []

        self.port_check_time = port_check_time
        self.autocheckports = autocheckports
        self.permanently_ignored_ports = set(permanently_ignored_ports)

        self.set_communicator(python_communicator.PythonCommunicator() if communicator is None else communicator)


        self.logger = logging.getLogger("SerialReader") if logger is None else logger

        if start_in_background:
            self.run_in_background()

    def reactivate_port(self,port=None):
        if port is None:
            return
        try:
            self.ignored_ports.remove(port)
        except:
            pass

        try:
            self.deadports.remove(port)
        except:
            pass

    def deactivate_port(self,port=None):
        if port is None:
            return
        self.ignored_ports.add(port)
        self._communicator.cmd_out(targets=[port], cmd="stop_read")

    def run_in_background(self):
        threading.Thread(target=self.read_forever).start()

    def set_communicator(self, communicator: python_communicator.PythonCommunicator):
        self._communicator = communicator
        self._communicator.add_node("serialreader", self)

    def get_communicator(self):
        return self._communicator

    communicator = property(get_communicator, set_communicator)

    def sendports(self, data_target=None):
        try:
            self._communicator.cmd_out(
                cmd="set_ports",
                sender="serialreader",
                targets=(None if data_target is None else (data_target if isinstance(data_target,list) else [data_target])),
                available_ports=list(self.available_ports),
                ignored_ports=list(self.ignored_ports | self.permanently_ignored_ports),
                connected_ports=[sp.port for sp in self.connected_ports],
                identified_ports=[sp.port for sp in self.identified_ports],
            )
        except python_communicator.TargetNotFoundException:
            pass

    get_ports = sendports

    def read_forever(self):
        while 1:
            if self.autocheckports:
                self.available_ports, self.ignored_ports = serialdetector.get_avalable_serial_ports(
                    ignore=self.ignored_ports | self.permanently_ignored_ports | set([sp.port for sp in self.connected_ports])
                )
                self.deadports = self.available_ports.intersection(self.deadports)
                newports = self.available_ports - (
                        self.ignored_ports | self.deadports | self.permanently_ignored_ports
                )
                self.logger.debug(
                    "available Ports: "
                    + str(self.available_ports)
                    + "; new Ports: "
                    + str(newports)
                    + "; ignored Ports: "
                    + str(self.ignored_ports | self.permanently_ignored_ports)
                    + "; ignored Ports: "
                    +str([sp.port for sp in self.connected_ports])
                    + "; ignored Ports: "
                    +str([sp.port for sp in self.identified_ports]),
                )

                self.sendports()
                for port in newports.copy():
                    try:
                        self.open_port(port)
                    except Exception as e:
                        self.logger.exception(e)
                        pass
            time.sleep(self.port_check_time)

    def open_port(self, port):
        try:
            self.available_ports.remove(port)
        except:
            pass
        try:
            self.ignored_ports.remove(port)
        except:
            pass
        try:
            self.permanently_ignored_ports.remove(port)
        except:
            pass

        from ..serialport import SerialPort
        t = threading.Thread(
            target=SerialPort,
            kwargs={
                **{
                    "communicator": self._communicator,
                    "serialreader": self,
                    "config": self.config,
                    "port": port,
                    "baudrate": self.config.get("portdata", port, "baud", default=9600),
                },
                # **kwargs,
            },
        )
        t.start()


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)

    sr = SerialReader()

    sr.read_forever()
