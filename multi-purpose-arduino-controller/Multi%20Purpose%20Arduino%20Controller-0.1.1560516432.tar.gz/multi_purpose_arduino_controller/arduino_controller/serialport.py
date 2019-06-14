import logging
import threading
import time

import serial

from .parseboards import board_by_firmware
from multi_purpose_arduino_controller.arduino_controller.serialreader.serialreader import SerialReader
from .basicboard.board import ArduinoBasicBoard
from .portrequest import validate_buffer
from multi_purpose_arduino_controller.python_communicator import PythonCommunicator

PORTREADTIME = 0.01
BAUDRATES = (
    9600,
    115200,
    #   19200,
    #   38400,
    #   57600,
    #    230400,
    #    460800,
    #    500000,
    #    576000,
    #    921600,
    #    1000000,
    #    1152000,
    #    1500000,
    #    2000000,
    #    2500000,
    #    3000000,
    #    3500000,
    #    4000000,
)


class SerialPort(serial.Serial):
    def __init__(
        self,
        serialreader,
        port,
        config=None,
        logger=None,
        communicator: PythonCommunicator = None,
        baudrate=9600,
        **kwargs,
    ):

        self.serialreader: SerialReader = serialreader
        self.data_targets = set([])

        if logger is None:
            logger = logging.getLogger("serialreader " + port)
        self.logger = logger

        self.board: ArduinoBasicBoard = None
        self.workthread = None
        self.updatethread = None
        self.readbuffer = []
        self.time = time.time()

        if config is None:
            config = serialreader.config
        self.config = config

        try:
            super().__init__(port, baudrate=baudrate, timeout=0, **kwargs)
        except Exception as e:
            serialreader.deadports.add(port)
            self.logger.exception(e)
            return
        self.logger.info("port found " + self.port)
        serialreader.connected_ports.add(self)

        if communicator is None:
            communicator = PythonCommunicator()
        self.communicator:PythonCommunicator = communicator

        self.communicator.add_node(port, self)

        self.to_write = []
        self.start_read()

        newb = board_by_firmware(config.get("portdata", self.port, "firmware", default=0))
        if newb is not None:
            self.set_board(newb["classcaller"])
        else:
            self.set_board(ArduinoBasicBoard)

    def add_data_target(self, data_target=None):
        if data_target is not None:
            self.data_targets.add(data_target)

    def remove_data_target(self, data_target):
        if data_target in self.data_targets:
            self.data_targets.remove(data_target)

    def boardfunction(self, board_cmd, **kwargs):
        try:
            getattr(self.board, board_cmd)(**kwargs)
        except:
            self.logger.exception(Exception)

    def set_board_attribute(self, attribute,value):
        try:
            setattr(self.board,attribute,value)
        except:
            self.logger.exception(Exception)

    def add_datapoint(self,board, key, y, x=None):
        t = time.time() - self.time
        if x is None:
            x = t
        self.serialreader.datalogger.add_datapoint(key, x=x, y=y)
        self.communicator.cmd_out(cmd="datapoint", key=key, x=x, y=y, targets=list(self.data_targets),port=board.port)

    def set_board(self, BoardClass):
        self.board = BoardClass()
        self.board.set_serial_port(self)
        time.sleep(2)
        self.board.identify()

        if not self.board.identified:
            self.stop_read()
            self.serialreader.ignored_ports.add(self.port)
            raise ValueError("unable to identify " + self.port)

        if self.board.FIRMWARE != self.board.firmware:
            newb = board_by_firmware(self.board.firmware)
            if newb is not None:
                return self.set_board(newb["classcaller"])
            else:
                self.stop_read()
                self.serialreader.ignored_ports.add(self.port)
                raise ValueError("firmware not found " + str(self.board.firmware))

        #self.board.specific_identification()
        if not self.board.identified:
            self.stop_read()
            self.serialreader.ignored_ports.add(self.port)
            raise ValueError(
                "unable to specificidentify "
                + self.port
                + "with firmware:"
                + str(self.board.firmware)
            )

        self.logger.info(str(self.port) + " identified ")

        self.serialreader.identified_ports.add(self)

        self.config.put("portdata", self.port, "baud", value=self.baudrate)
        self.config.put("portdata", self.port, "firmware", value=self.board.firmware)
        self.board.restore(self.config.get("boarddata", self.board.id, default={}))
        self.board.get_portcommand_by_name("identify").sendfunction(True)
        self.communicator.cmd_out(cmd="port_identified",port=self.port)
        return True

    def board_updater(self):
        while self.is_open:
            if self.board is not None:
                self.send_board_data()
                time.sleep(self.board.updatetime)

    def send_board_data(self, **kwargs):
        if self.board is not None:
            if self.board.identified:
                data = self.board.save()
                self.config.put("boarddata", self.board.id, value=data)
                msg_d = dict(
                    targets=list(self.data_targets),
                    cmd="boardupdate",
                    boarddata=data,
                    **kwargs,
                )
                msg = self.communicator.cmd_out(**msg_d)
                self.logger.debug(msg_d)

    def work_port(self):
        while self.is_open:
            try:
                while len(self.to_write) > 0:
                    t = self.to_write.pop()
                    self.logger.debug("write to " + self.port + ": " + str(t))
                    super().write(t)
                c = self.read()

                while len(c) > 0:
                    self.readbuffer.append(c)
                    validate_buffer(self)
                    c = self.read()
            except serial.serialutil.SerialException:pass
            except Exception as e:
                self.logger.exception(e)
                break
            time.sleep(PORTREADTIME)
        self.logger.error("work_port stopped")
        self.stop_read()

    def start_read(self):
        self.logger.info("port opened " + self.port)
        self.communicator.cmd_out(
            sender=self.port, cmd="port_opened",port=self.port,baud=self.baudrate)

        if not self.is_open:
            self.open()
        self.workthread = threading.Thread(target=self.work_port)
        self.updatethread = threading.Thread(target=self.board_updater)
        self.workthread.start()
        self.updatethread.start()

    def write(self, data):
        self.to_write.append(data)

    def stop_read(self):
        self.close()
        try:
            self.workthread.join()
        except:
            pass
        self.workthread = None
        try:
            self.updatethread.join()
        except:
            pass
        self.close()
        self.updatethread = None
        self.logger.info("port closed " + self.port)
        self.communicator.cmd_out(
            sender=self.port,
            cmd="port_closed",
            port = self.port
        )
        if self in self.serialreader.connected_ports:
            self.serialreader.connected_ports.remove(self)
        if self in self.serialreader.identified_ports:
            self.serialreader.identified_ports.remove(self)
        del self

    #def update(self, **kwargs):
    #    if self.board is not None:
    #        if self.board.id is not None:
    #            self.board.restore(**kwargs)
    #           self.send_board_data(force_update=True)

    def get_board(self,data_target=None):
        if data_target is None: return
        board = self.board.get_board()
        self.communicator.cmd_out("set_board",targets=[data_target],board=board,port=self.port)

