#
# Copyright (c) 2019, Nordic Semiconductor ASA
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without modification,
# are permitted provided that the following conditions are met:
#
# 1. Redistributions of source code must retain the above copyright notice, this
#    list of conditions and the following disclaimer.
#
# 2. Redistributions in binary form, except as embedded into a Nordic
#    Semiconductor ASA integrated circuit in a product or a software update for
#    such product, must reproduce the above copyright notice, this list of
#    conditions and the following disclaimer in the documentation and/or other
#    materials provided with the distribution.
#
# 3. Neither the name of Nordic Semiconductor ASA nor the names of its
#    contributors may be used to endorse or promote products derived from this
#    software without specific prior written permission.
#
# 4. This software, with or without modification, must only be used with a
#    Nordic Semiconductor ASA integrated circuit.
#
# 5. Any software provided in binary form under this license must not be reverse
#    engineered, decompiled, modified and/or disassembled.
#
# THIS SOFTWARE IS PROVIDED BY NORDIC SEMICONDUCTOR ASA "AS IS" AND ANY EXPRESS
# OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES
# OF MERCHANTABILITY, NONINFRINGEMENT, AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL NORDIC SEMICONDUCTOR ASA OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE
# GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION)
# HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT
# OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

import serial
import logging
import importlib
from time import sleep
from zb_cli_wrapper.nrf_dev_map import nrfmap
from zb_cli_wrapper.src.utils.connection import UartConnection, AsciiConnection
from zb_cli_wrapper.src.utils.communicator import AdvancedLineCommunicator, CommandError


class ZigbeeAdvancedLineCommunicator(AdvancedLineCommunicator):
    """
        This is a class to set the custom prompt in AdvancedLineCommunicator.
    """

    def __init__(self, conn, read_size=128, wait_time=0.001, prompt=">", success_prefix="done", error_prefix="error:"):
        super(ZigbeeAdvancedLineCommunicator, self).__init__(conn, read_size, wait_time, prompt, success_prefix,
                                                             error_prefix)


class ZbCliDevice(object):
    COMMAND_MODULE_PATH = 'zb_cli_wrapper.src.utils.cmd_wrappers'

    def __init__(self, params):
        """
            ZbCliDevice constructor takes parameters put in 'params' dictionary:
            Cli device is connected by com_port but instead of com_port name: cdc_serial or segger number can be used
            To connect Cli device connected to specific com_port add 'com_port' : 'YOUR_COM_PORT_NAME' to dictionary
            To connect Cli device by cdc_serial given add 'cdc_serial' : 'YOUR_CDC_SERIAL' to dictionary
            To connect Cli device by segger number given add 'segger' : 'YOUR_SEGGER_NBR' to dictionary

            On creation, Init loads modules from 'self.commands', located under COMMAND_MODULE_PATH and will add
            as an attribute to the device under the name of the module, e.g.:
                - 'zigbee.zcl' will be available under 'cli_device.zcl' , where 'cli_device' is ZbCliDevice object.
        """

        self._cli = None
        self.com_port = None
        self.connection_handler = UartConnection
        self.connection_wrapper = AsciiConnection
        self.communicator_handler = ZigbeeAdvancedLineCommunicator
        self.cli_default_baud_rate = 115200
        self.baud_rate = self.cli_default_baud_rate
        self.commands = ['zigbee.bdb', 'zigbee.zcl', 'zigbee.zdo', 'zigbee.log']

        if 'segger' in params:
            self.segger = params['segger']
            try:
                self.com_port = nrfmap.ComPortMap.get_com_ports_by_id(self.segger, [nrfmap.Vendor.Segger])[0]
            except KeyError:
                logging.error("There is no board with seggger: {}".format(self.segger))

        if self.com_port is None and 'cdc_serial' in params:
            self.cdc_serial = params['cdc_serial']
            try:
                self.com_port = nrfmap.ComPortMap.get_com_ports_by_id(self.cdc_serial, [nrfmap.Vendor.CDC])[0]
            except KeyError:
                logging.error("There is no board with cdc_serial: {}".format(self.cdc_serial))

        if self.com_port is None and 'com_port' in params:
            self.com_port = params.get('com_port')

        if self.com_port is None:
            logging.warning("Com Port is {}".format(self.com_port))

        for command in self.commands:
            attribute = command.split('.')[-1]
            setattr(self, attribute,
                    importlib.import_module(self.COMMAND_MODULE_PATH + "." + command).CommandWrapper(self.get_cli))

    def get_cli(self):
        """
            Returns the current CLI object instance. Pass this to command wrappers, so that they can update their CLI handles
            when needed.
        """
        return self.cli

    @property
    def cli(self):
        """
            CLI communicator. Initializes on the first usage. Make sure that this property is not called in the constructor.
        """
        if not self._cli:
            self._cli = self.create_cli_communicator()
            self._configure_cli()
        return self._cli

    @cli.setter
    def cli(self, value):
        self._cli = value

    def _configure_cli(self):
        """
            Abstract method to configure the CLI communicator. Called after create_cli_communicator().
            To be overloaded in child classes.
            
            NOTE: Do not access the communicator with self.cli - use self._cli instead!
        """
        pass

    def close_cli(self):
        """
            Closes the CLI connection and stops the communicator thread.
        """
        if self._cli:
            logging.info("Closing CLI...")
            self._cli.stop()
            self._cli._conn.close()
            self._cli = None
            logging.info("... CLI closed.")

    def create_cli_communicator(self):
        """
            Create the communicator that allows to read and write data to and from CLI.

            Return:
                Communicator (ZigbeeAdvancedLineCommunicator) for the interaction with CLI.

        """
        self.connection_params = {"port": self.com_port, "baudrate": self.baud_rate or self.cli_default_baud_rate}

        # Starting up the connection handler.
        conn = self.connection_handler(**self.connection_params)

        # Open communicator.
        # Perform 10 attempts to avoid PermissionError(13, 'Access is denied.', None, 5) on Windows.
        attempts = 10
        while attempts:
            try:
                logging.info("Trying to open com port {}. Attempts left: {}.".format(self.com_port, attempts))
                attempts -= 1
                conn.open()
                conn._serial.dsrdtr = False
            except serial.serialutil.SerialException as e:
                sleep(1)
                if not attempts:
                    raise e
                continue
            break
        logging.info("Com port {} opened successfully.".format(self.com_port))

        # Some connections may need wrappers to parse the output properly.
        if self.connection_wrapper:
            comm = self.communicator_handler(self.connection_wrapper(conn))
        else:
            comm = self.communicator_handler(conn)

        comm.start()

        return comm

    def wait_until_connected(self, timeout=10):
        """
            Waits until CLI is connected to the network or the function times out.
            
            Args:
                self (ZbCliDevice): CLI device object.
                timeout (int): Timeout after which the function will stop attempts to connect and will return None.
                
            Return:
                Self (ZbCliDevice) specified in the parameter or None if CLI is unable to connect to the network.
        """
        for x in range(timeout):
            try:
                short_addr_resp = self.zdo.short_addr
            except CommandError:
                logging.info("Trying to connect cli to network. Attempts left: {:d}".format(timeout - x - 1))
                sleep(1)
            else:
                if isinstance(short_addr_resp, int):
                    logging.info("CLI short address: 0x{:04X}".format(short_addr_resp))
                    return self
        logging.info("Can not connect CLI to network.")
        self.close_cli()
        return None
