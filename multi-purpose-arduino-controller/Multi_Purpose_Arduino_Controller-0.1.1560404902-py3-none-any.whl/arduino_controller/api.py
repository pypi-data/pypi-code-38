import logging
import os
import tempfile
import time

from json_dict import JsonDict

from django_websocket_server.websocket_server import SocketServer
from multi_purpose_arduino_controller.python_communicator import PythonCommunicator, TargetNotFoundException
from .datalogger import DataLogger


class ArduinoControllerAPI:
    def __init__(
            self,
            name="arduinocontrollerapi",
            python_communicator: PythonCommunicator = None,
            websocket_server: SocketServer = None,
            config=None,
            datalogger: DataLogger = None,
            logger=None,
            data_dir=None,
    ):
        self._python_communicator = None
        self.boarddata = {}
        self.websocket_server = None
        if websocket_server is not None: self.set_websocket_server(websocket_server)
        self.name = name
        self.data = {}
        self.dataupdate = 1
        self.lastupdate = 0
        self.lastsend = dict()
        self.connected_ports = set()
        self.ignored_ports = set()
        self.available_ports = set()
        self.identified_ports = set()

        self.logger = logging.getLogger(self.name) if logger is None else - logger

        self.data_dir = os.path.join(tempfile.gettempdir(), self.name + "_API") if data_dir is None else data_dir

        os.makedirs(self.data_dir, exist_ok=True)

        self.config = JsonDict(file=os.path.join(self.data_dir, "config.json"),
                               createfile=True) if config is None else config
        self.config.autosave = True

        self.sensor_ports = set([])

        self.set_communicator(PythonCommunicator() if python_communicator is None else python_communicator)

        self.datalogger = DataLogger(autosave_path=self.data_dir) if datalogger is None else datalogger

        self.running = False
        self.run_thread = None

    def set_communicator(self, communicator: PythonCommunicator):
        self._python_communicator = communicator
        self._python_communicator.add_node(self.name, self)

    def get_communicator(self):
        return self._python_communicator

    python_communicator = property(get_communicator,set_communicator)

    def ask_for_ports(self):
        try:
            self._python_communicator.cmd_out(
                cmd="get_ports",
                sender=self.name,
                targets=["serialreader"],
                data_target=self.name,
            )
        except TargetNotFoundException:
            pass

    def set_ports(self, connected_ports=None, ignored_ports=None, available_ports=None,identified_ports=None):
        self.connected_ports = set([] if connected_ports is None else connected_ports)
        self.ignored_ports = set([] if ignored_ports is None else ignored_ports)
        self.available_ports = set([] if available_ports is None  else available_ports)
        self.identified_ports = set([] if identified_ports is None  else identified_ports)
        for port in self.connected_ports.difference(self.sensor_ports): self.add_sensor_port(port)
        for port in self.sensor_ports.difference(self.connected_ports): self.add_sensor_port(port)

    def remove_sensor_port(self, port):
        self.logger.info("remove sensor port" + str(port))
        self.sensor_ports.remove(port)

    def add_sensor_port(self, port=None):
        time.sleep(1)
        if port is not None:
            self.logger.info("add sensor port" + str(port))
            self.sensor_ports.add(port)
            self._python_communicator.cmd_out(
                cmd="add_data_target", targets=[port], data_target=self.name
            )

    def data_update_time(self, data_update_time=None):
        if data_update_time is not None:
            self.dataupdate = data_update_time
            self.lastupdate = data_update_time.time() - self.dataupdate

    def datapoint(self, key=None, x=None, y=None,**kwargs):
        if key is None or x is None or y is None:
            return

        self.datalogger.add_datapoint(key, x, y)

        # self.data[message["data"]["key"]].append([message["data"]["x"], message["data"]["y"], message["data"]["t"]])

        t = time.time()
        if t - self.lastupdate > self.dataupdate:
            self.lastupdate = t

            for key, values in self.datalogger.get_last_valid_values().items():
                if key not in self.lastsend:
                    self.lastsend[key] = ("x", "y")
                if (
                        self.lastsend[key][0] != values[0]
                        or self.lastsend[key][1] != values[1]
                ):
                    self.lastsend[key] = (values[0], values[1])
                    #self._python_communicator.cmd_out(
                    #    cmd="datapoint",
                    #    key=key,
                    #    x=values[0],
                    #    y=values[1],
                    #    targets=["websocket"],
                    #)

            # for key, dates in self.data.items():
            #   self.communicator.cmd_out(
            #          sender=self.name,
            #         x=dates[-1][0],
            #        y=dates[-1][1],
            #       key=key,
            #      target="gui",
            #     t=dates[-1][2],
            #    as_string=True,
            # )

    def get_data(self, data_target=None):
        if data_target is None:
            return
        self._python_communicator.cmd_out(
            sender=self.name,
            cmd="set_data",
            target=data_target,
            as_string=True,
            data=self.data,
        )

    def boardupdate(self, boarddata=None):
        if boarddata is None:
            return
        self.boarddata[boarddata.get('port')] = boarddata
        self.logger.info("boardupdate:" + str(boarddata))

    def get_board_attribute(self, port, attribute):
        if port not in self.boarddata: return
        return self.boarddata[port].get(attribute, None)

    def port_opened(self,port):
        pass

    def port_closed(self,port):
        if port in self.sensor_ports:
            self.sensor_ports.remove(port)

    def port_identified(self,port):
        pass

    def set_websocket_server(self, websocket_server):
        self.websocket_server = websocket_server

