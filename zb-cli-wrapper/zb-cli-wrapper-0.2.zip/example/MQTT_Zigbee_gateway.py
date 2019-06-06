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

import os
import sys
import time
import queue
import serial
import logging
import colorsys
import threading
import paho.mqtt.client as mqtt
from yaml import load
from math import ceil
from zb_cli_wrapper.zb_cli_dev import ZbCliDevice
from zb_cli_wrapper.src.utils.cmd_wrappers.zigbee.constants import *

# Configure logging for standard output with message formatted.
logging.basicConfig(stream=sys.stdout, level=logging.INFO, format='%(filename)s: %(levelname)s: %(message)s')

ROOT_PATH = os.path.dirname(os.path.realpath(__file__))

# Class to store data for ZCL commands, with auxiliary methods.
class ZCLRequestData:
    def __init__(self, eui64, ep, cluster, cmd_id, def_resp, payload, profile=DEFAULT_ZIGBEE_PROFILE_ID):
        self.eui64 = eui64
        self.ep = ep
        self.cluster = cluster
        self.cmd_id = cmd_id
        self.def_resp = def_resp
        self.payload = payload
        self.profile = profile

    def __str__(self):
        return ("EUI64={:016X} EP={} CLUSTER={:04X} CMD={:04X} RESP={} PAYLOAD={}".format(self.eui64, self.ep,
                                                                                          self.cluster,
                                                                                          self.cmd_id, self.def_resp,
                                                                                          self.payload))

    @staticmethod
    def set_on_off_state(device, state):
        """
            Parse specified arguments and return the object ZCLRequestData with command to send.
                
            Args:
                device (dict): Dictionary containing 'eui64' and 'ep' as key-value pairs.
                state (int): State of the Zigbee On/Off attribute to be set.

            Return:
                Object (ZCLRequestData) with the ZCL data.
        """
        # Check if state is int in range 0-1
        assert state in range(2), "Argument value out of range"

        return ZCLRequestData(eui64=device['eui64'], ep=device['ep'], cluster=ON_OFF_CLUSTER, cmd_id=int(state),
                              def_resp=True, payload=None)

    @staticmethod
    def move_to_level_control(device, level):
        """
            Parse specified arguments and return the object ZCLRequestData with command to send.
                
            Args:
                device (dict): Dictionary containing 'eui64' and 'ep' as key-value pairs.
                level (int): Level of the Zigbee Level attribute to be set.

            Return:
                Object (ZCLRequestData) with the ZCL data.
        """
        # Check if level is int in range 0-255
        assert level in range(256), "Argument value out of range"

        return ZCLRequestData(eui64=device['eui64'], ep=device['ep'], cluster=LVL_CTRL_CLUSTER,
                              cmd_id=LVL_CTRL_MV_TO_LVL_CMD, def_resp=True, payload=[(int(level), UINT8_TYPE), (1, UINT16_TYPE)])

    @staticmethod
    def move_to_hue_saturation(device, hue, saturation):
        """
            Parse specified arguments and return the object ZCLRequestData with command to send.
                
            Args:
                device (dict): Dictionary containing 'eui64' and 'ep' as key-value pairs.
                hue (int): Value of the current_hue attribute to be set.
                saturation (int): Value of the current_saturation attribute to be set.

            Return:
                Object (ZCLRequestData) with the ZCL data.
        """
        # Check if hue, saturation is int in range 0-254
        assert hue in range(255), "Argument value out of range"
        assert saturation in range(255), "Argument value out of range"

        return ZCLRequestData(eui64=device['eui64'], ep=device['ep'],
                              cluster=COLOR_CTRL_CLUSTER, cmd_id=COLOR_CTRL_MV_TO_HUE_SAT_CMD, def_resp=True,
                              payload=[(int(hue), UINT8_TYPE), (int(saturation), UINT8_TYPE), (1, UINT16_TYPE)])

    @staticmethod
    def set_lock_state(device, lock_state):
        """
            Parse specified arguments and return the object ZCLRequestData with command to send.
                
            Args:
                device (dict): Dictionary containing 'eui64' and 'ep' as key-value pairs.
                lock_state (int): Value of the lock_state attribute to be set.

            Return:
                Object (ZCLRequestData) with the ZCL data.
        """
        # Check if lock_state is int in range 0-1
        assert lock_state in range(2), "Argument value out of range"

        return ZCLRequestData(eui64=device['eui64'], ep=device['ep'], cluster=DOOR_LOCK_CLUSTER,
                              cmd_id=int(lock_state), def_resp=False, payload=None)


class ZBCLIThread(threading.Thread):
    def __init__(self, cli_device):
        threading.Thread.__init__(self)
        # Queue to store ZCL command data. By default, maxsize=0 (that is, the queue size is infinite).
        self.zcl_data_queue = queue.Queue()
        # Create dictionary to store the last published value of each topic (key).
        self.attr_value = {}
        self.CLI_THREAD_SLEEP_S = 0.073
        self.cli = cli_device

    def run(self):
        """
            Thread worker function for sending Zigbee commands.
        """
        while True:
            item = self.zcl_data_queue.get(block=True)
            if item is None:
                logging.info("Item taken from the queue is None. Trying to close CLI.")
                self.cli.close_cli()
                sys.exit()

            # If the queue object is not of the ZCLRequestData type, close CLI and terminate thread by raising unhandled exception.
            if not isinstance(item, ZCLRequestData):
                logging.info("Item taken from the queue is not of the ZCLRequestData type. Closing CLI.")
                self.cli.close_cli()
                sys.exit()

            logging.info("CLI cmd send : {}".format(str(item)))
            self.cli.zcl.generic(eui64=item.eui64, ep=item.ep, cluster=item.cluster,
                                 cmd_id=item.cmd_id, payload=item.payload, profile=item.profile)
            self.zcl_data_queue.task_done()

            # Sleep after every item taken from the queue.
            time.sleep(self.CLI_THREAD_SLEEP_S)

    def stop(self):
        """
            Stop worker thread and CLI thread.
        """
        # Put None to stop worker thread and CLI thread.
        self.zcl_data_queue.put(None)
        # Wait for CLI to close and for worker thread to stop.
        self.cli.get_cli().join(timeout=5)
        self.join(timeout=5)

    def on_message(*args):
        """
            Handler for on message MQTT callback.
                
            Args:
                args (list): List of arguments. 'self' is specified by object, 'client, user_data, msg' are specified by MQTT Client.
        """
        self, client, user_data, msg = args
        # Check whether the last value for specified topic exists.
        if msg.topic not in self.attr_value:
            self.attr_value[msg.topic] = float(-1)
            logging.info("No last value stored for topic: {}".format(msg.topic))

        # Exit earlier if topic value has not changed.
        if self.attr_value[msg.topic] == float(msg.payload):
            return
        self.attr_value[msg.topic] = float(msg.payload)
        try:
            prefix, device_alias, cluster_name, topic_rest = msg.topic.split('/', maxsplit=3)
        except ValueError:
            try:
                prefix, device_alias, cluster_name = msg.topic.split('/')
            except ValueError:
                logging.info("Problem splitting topic: {}. Topic is omitted".format(msg.topic))
                return

        device = get_device_by_alias(device_alias)
        # Exit if no known device is found.
        if device is None:
            return

        logging.info("Message - Topic: {} ,Payload: {}".format(msg.topic, msg.payload))
        if cluster_name == "lvl_ctrl":
            self.zcl_data_queue.put(
                ZCLRequestData.move_to_level_control(device, ceil(self.attr_value[msg.topic] * 255.0 / 100.0)))

        elif cluster_name == "on_off":
            self.zcl_data_queue.put(
                ZCLRequestData.set_on_off_state(device, ceil(self.attr_value[msg.topic])))

        # By default, the command is sent with no payload (works only with locks that do not require pin).
        elif cluster_name == "door_lock":
            self.zcl_data_queue.put(
                ZCLRequestData.set_lock_state(device, ceil(self.attr_value[msg.topic])))

        elif cluster_name == "color_ctrl":
            red = self.attr_value["home/{}/{}/r".format(device_alias, cluster_name)]
            green = self.attr_value["home/{}/{}/g".format(device_alias, cluster_name)]
            blue = self.attr_value["home/{}/{}/b".format(device_alias, cluster_name)]
            brightness = self.attr_value["home/{}/lvl_ctrl/lvl".format(device_alias)]

            # Convert color from rgb color_space to hsv color_space, scaled to the specified brightness.
            hue, saturation, value = colorsys.rgb_to_hsv(red / 100.0 * brightness / 100.0,
                                                         green / 100.0 * brightness / 100.0,
                                                         blue / 100.0 * brightness / 100.0)
            self.zcl_data_queue.put(ZCLRequestData.move_to_hue_saturation(device, ceil(hue * 254.0),
                                                                          ceil(saturation * 254.0)))


def get_device_by_alias(alias):
    """
        Find and return dictionary with device parameters. Search based on the specified alias.
            
        Args:
            alias (string): Alias of the device parameters to find.

        Return:
            Dictionary (dict) with device parameters.
    """
    for device in config['device']:
        if device['alias'] == alias:
            return device
    return None


def connect_to_broker(client, broker_address, broker_port, bind_address, reconnect_tries):
    """
        Connect to MQTT broker with multiple reconnect attempts (tries).
            
        Args:
            client (object): MQTT client object.
            broker_address (string): Broker address to connect to.
            broker_port (int): Broker port to connect to.
            bind_address (string): IP address of a local network interface to bind to if multiple interfaces exist.
            reconnect_tries (int): Number of the reconnect attempts (tries).
    """
    for x in range(reconnect_tries):
        try:
            client.connect(broker_address, port=broker_port, bind_address=bind_address)
        except ConnectionRefusedError:
            if x >= (reconnect_tries - 1):
                logging.info('Can not connect to broker')
                return False
            else:
                logging.info("Trying to connect to broker. Attempts left: {:d}".format(reconnect_tries - x - 1))
                time.sleep(1)
        else:
            # If connected to broker, break.
            return True


def create_cli_device(config_dict):
    """
        Create CLI device with parameters specified as argument. Return the created CLI device object.
            
        Args:
            config_dict (dict): Dictionary with configuration parameters.
            
        Return:
            CLI device object (ZbCliDevice), created and connected. If error occurs, return None.
    """
    # Read config_dict and prepare parameter for creating ZbCliDevice
    param = {}
    for cli_id in ['segger', 'cdc_serial', 'com_port']:
        if cli_id in config_dict['CLIDevice']:
            param[cli_id] = config_dict['CLIDevice'][cli_id]

    try:
        cli_dev = ZbCliDevice(param)
        cli_dev.bdb.channel = config_dict['CLIDevice']['channels']
        cli_dev.bdb.role = config_dict['CLIDevice']['role']
    except serial.serialutil.SerialException:
        logging.info('Can not create CLI device')
        cli_dev.close_cli()
        return None

    logging.info("CLI device created, trying to connect ...")
    # Start commissioning.
    cli_dev.bdb.start()

    return cli_dev.wait_until_connected()


def main(config_dict):
    """
        Application main function.

        Args:
            config_dict (dict): Dictionary with configuration parameters.
    """
    # Create the MQTT client.
    client = mqtt.Client(client_id='MQTT Zigbee gateway', userdata='')
    client.username_pw_set(config_dict['MQTTClient']['MQTT_CLIENT_NAME'],
                           password=config_dict['MQTTClient']['MQTT_CLIENT_PASSWD'])

    # Try to connect to broker.
    if not connect_to_broker(client,
                             config_dict['MQTTClient']['BROKER_ADDRESS'],
                             config_dict['MQTTClient']['BROKER_PORT'],
                             config_dict['MQTTClient']['BIND_ADDRESS'],
                             config_dict['MQTTClient']['MQTT_RECONNECT_TRIES']):
        logging.info("Exiting...")
        sys.exit()

    logging.info("Connected to broker. Starting CLI...")

    # If connected to broker, try to create the CLI communicator.
    cli_dev = create_cli_device(config)
    if not cli_dev:
        logging.info("Problem with creating the CLI communicator. Exiting...")
        sys.exit()

    # Create the ZBCLIThread object.
    try:
        cli_thread = ZBCLIThread(cli_dev)
        cli_thread.start()
    except RuntimeError:
        logging.info("Error while creating thread.")
        cli_thread.stop()
        sys.exit()

    # Assign the cli_thread.on_message handle function to MQTT client on message function.
    client.on_message = cli_thread.on_message

    # Subscribe to topics stored in the configuration dictionary.
    for device in config['device']:
        for topic in device['subscribe']:
            client.subscribe(topic)

    logging.info("Client started.")

    """
        Start handling MQTT messages. Periodically check if CLI threads are alive.
        The except for Keyboard Interrupt allows for closing CLI before closing the application. 
    """
    try:
        while True:
            client.loop(timeout=0.5)
            if not cli_dev.get_cli().is_alive() or not cli_thread.is_alive():
                logging.info('Problem with CLI communication - thread not alive. Closing...')
                # Try to close the communicator and wait for threads to close.
                cli_thread.stop()
                break

    except KeyboardInterrupt:
        logging.info("Keyboard interrupt. Closing...")
        # Try to close the communicator and wait for threads to close.
        cli_thread.stop()
        return


if __name__ == '__main__':
    # Load the device configuration from config.yaml into config.
    with open(os.path.join(ROOT_PATH, 'config.yaml')) as f:
        config = load(f.read())
    main(config)
