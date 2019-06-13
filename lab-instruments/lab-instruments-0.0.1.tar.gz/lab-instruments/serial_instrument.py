import serial.tools.list_ports
import serial

import logging
from threading import Thread
from queue import Queue
from time import sleep
import re

logger = logging.getLogger()
logger.setLevel(logging.INFO)


class SerialInstrument:

    def __init__(self):
        self.connection = None
        self.should_disconnect = False
        self.command_queue = Queue()

        self.is_connected = False
        self.read_thread = Thread(target=self._read_command,
                                  name="Read Thread",
                                  kwargs={'refresh_time': 0.1})
        self.process_thread = Thread(target=self._process_command,
                                     name="Process Thread",
                                     kwargs={'refresh_time': 0.1})

    def start_connection(self, connection, baudrate=115200):
        """
        Start a serial connection, this launch two thread: Read and Process.

        :param connection:
        :param baudrate:
        :return:
        """
        self.port_info = connection
        logger.info(f'Start connexion with {connection.description}')
        try:
            self.connection = serial.Serial(connection.device, baudrate=baudrate, timeout=5)
            if self.connection.is_open is False:
                logger.debug("Open Serial Port")
                self.connection.baudrate = baudrate
                self.connection.open(timeout=5)

            self.is_connected = self.connection.is_open

            self.should_disconnect = False

            self.read_thread = Thread(target=self._read_command,
                                      name="Read Thread",
                                      kwargs={'refresh_time': 0.1})

            self.process_thread = Thread(target=self._process_command,
                                         name="Process Thread",
                                         kwargs={'refresh_time': 0.1})

            self.read_thread.start()
            self.process_thread.start()
            self.connection_ready()

        except serial.SerialException:
            logger.error("Can't connect to Instrument")
            self.is_connected = False

    def connection_ready(self):
        pass

    def _read_command(self, refresh_time):
        logger.debug(f"Start Read Command thread")
        while not self.should_disconnect:
            while (self.connection.in_waiting > 0) and (not self.should_disconnect):
                # start_time = time()
                data = self._receive_command()
                self.command_queue.put(data)
                # self.process_command(data)
                # logger.debug(f"Read command: {data}")

            sleep(refresh_time)

        logger.debug("End Reading Thread")

    def _process_command(self, refresh_time):
        logger.debug(f"Start Process Command thread")
        while not self.should_disconnect:
            while (not self.command_queue.empty()) and (not self.should_disconnect):
                command = self.command_queue.get()
                # logger.debug(f"Process command: {command}")
                self.process_command(command)
            sleep(refresh_time)
        logger.debug("End Process Command Thread")

    def send_command(self, command):
        command = str.encode(command)
        # logger.debug(f"Send {command}")
        if self.connection:
            # while self.connexion.out_waiting > 0:
            #     sleep(0.1)

            self.connection.write(command)
        else:
            raise InstrumentConexionError

    def process_command(self, command):
        """
        Override this method to process the commands from serial port
        :param command:
        :return:
        """
        pass

    def disconnect(self):
        self.pre_disconnection()
        logger.info(f"Disconnecting from {self.port_info.description}")
        self.should_disconnect = True
        if self.read_thread.is_alive():
            self.read_thread.join(100)

        if self.process_thread.is_alive():
            self.process_thread.join(100)

        if self.connection:
            try:
                self.connection.close()
                self.disconnection_ready()
            except AttributeError:
                raise InstrumentConexionError

        self.is_connected = self.connection.is_open

    def pre_disconnection(self):
        pass

    def disconnection_ready(self):
        pass

    def _receive_command(self):
        """
        Internal function - Receive a response
        :return: Response with the regex parse

        """
        try:
            # logger.debug('Try to read command')
            response = self._read_with_carry_return()

        except serial.SerialException as e:
            logger.error("Serial Exception in Serial monitor: %s", str(e))
            response = ''

        return response

    def _read_with_carry_return(self):

        response = self.connection.readline().decode("utf-8", 'replace').strip()
        return response

    def _read_with_eol(self):
        response = ""
        while True and (not self.should_disconnect):
            oneByte = self.connection.read(1)
            if oneByte == b"\r":  # method should returns bytes
                # print(command)
                break
            else:
                response += oneByte.decode()
        return response

    @staticmethod
    def decode_with_regex(command, regex_expression):
        p = re.compile(regex_expression)
        return p.search(command)

    @staticmethod
    def serial_port_for_description(port_description):
        serial_list = serial.tools.list_ports.comports()
        for serial_port in serial_list:
            if port_description == serial_port.description:
                return serial_port

        return None


class InstrumentConexionError(Exception):
    pass
