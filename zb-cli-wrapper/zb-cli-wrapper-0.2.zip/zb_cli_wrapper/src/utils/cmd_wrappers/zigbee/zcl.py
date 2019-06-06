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

import re
from ..base import CommandWrapper as BaseCmdWrapper
from . import constants
from utils.zigbee_classes.clusters.attribute import Attribute

class Commands:
    """ CLI Commands to be used with firmware which includes Zigbee CLI component with ZCL commands.
    """
    # Main command used in order to access ZCL subcommands
    MAIN = 'zcl'

    # Available ZCL commands
    PING = ' '.join([MAIN, 'ping {eui64:016X} {length}'])
    READATTR = ' '.join([MAIN, 'attr read {eui64:016X} {ep} {cluster:01X} {direction} {profile:04X} {attr:02X}'])
    WRITEATTR = ' '.join([MAIN, 'attr write {eui64:016X} {ep} {cluster:01X} {direction} {profile:04X} {attr_id:02X} {attr_type:02X} {attr_value:X}'])
    GENERIC_NO_PAYLOAD = ' '.join([MAIN, 'cmd {eui64:016X} {ep} {cluster:01X} -p {profile:04X} {cmd_id:01X}'])
    GENERIC_WITH_PAYLOAD = ' '.join([MAIN, 'cmd {eui64:016X} {ep} {cluster:01X} -p {profile:04X} {cmd_id:01X} -l {payload}'])
    SUBSCRIBE = ' '.join([MAIN, 'subscribe on {eui64:016X} {ep} {cluster:01X} {profile:04X} {attr_id:02X} {attr_type} {min_interval} {max_interval}'])

class CommandWrapper(BaseCmdWrapper):
    """ This class adds an interface for sending ZCL commands and receiving parsed
        responses through Zigbee CLI by calling methods on a device instance.
    """

    def readattr(self, eui64, attr, timeout=20.0, direction=constants.ZCLDirection.DIRECTION_CLI_TO_SRV, ep=constants.CLI_ENDPOINT, profile=constants.DEFAULT_ZIGBEE_PROFILE_ID):
        """ Sends "readattr" command and parses received response.

            Args:
                eui64 (int): destination node long address
                direction (ZCLDirection): direction of the ZCL frame (Client -> Server or Server -> Client)
                ep (int): destination node endpoint number
                profile (int): id of the profile, containing the cluster
                attr (object): Attribute object instance, representing attribute to be read
                timeout (float): maximum time, in seconds, within which CLI should return command response

            Returns:
                object: new Attribute object with values set according to the received response

            Raises:
                ValueError: if received result with an unknown formatting
                CommandError: if CLI returns error
                TimeoutError: if timeout occurred
        """
        response_re = re.compile('^(ID\:\ *)(.*)(Type\:\ *)(.*)(Value\:\ *)(.*)')

        cmd = Commands.READATTR.format(eui64=eui64, ep=ep, cluster=attr.cluster, direction='-c' if direction.value == constants.ZCLDirection.DIRECTION_SRV_TO_CLI.value else '', profile=profile, attr=attr.id)

        response = self.cli.write_command(cmd, timeout=timeout)
        resp_found = response_re.match(response[-1])
        if resp_found:
            resp = resp_found.groups()
            return Attribute(cluster=attr.cluster, id=int(resp[1]), type=int(resp[3], 16), value=resp[5], name=attr.name)
        else:
            raise ValueError("Received result in unexpected format: {}".format(response))

    def writeattr(self, eui64, attr, timeout=20.0, direction=constants.ZCLDirection.DIRECTION_CLI_TO_SRV, ep=constants.CLI_ENDPOINT, profile=constants.DEFAULT_ZIGBEE_PROFILE_ID):
        """ Sends "writeattr" command and parses received response.

            Args:
                eui64 (int): destination node long address
                direction (ZCLDirection): direction of the ZCL frame (Client -> Server or Server -> Client)
                ep (int): destination node endpoint number
                profile (int): id of the profile, containing the cluster
                attr (object): Attribute object instance, representing attribute to be written
                timeout (float): maximum time, in seconds, within which CLI should return command response

            Raises:
                ValueError: if attempts to write unsupported value type
                CommandError: if CLI returns error
                TimeoutError: if timeout occurred
        """
        cmd = Commands.WRITEATTR.format(eui64=eui64, ep=ep, cluster=attr.cluster, direction='-c' if direction.value == constants.ZCLDirection.DIRECTION_SRV_TO_CLI.value else '', profile=profile, attr_id=attr.id, attr_type=attr.type, attr_value=attr.value)
        return self.cli.write_command(cmd, timeout=timeout)

    @staticmethod
    def _parse_ping_response(response):
        """ Parse a single ping response and return a round trip time as integer (in milliseconds)
            Args:
                response (array of string): ping command response(s)

            Raises:
                ValueError: if unable to find ping response in responses

            Return:
                ping_time (int) in ms
        """
        ping_re = re.compile(r'Ping time\:\ \b(\d+)\b ms')
        ping_response_match = ping_re.match(response)
        if ping_response_match is not None:
            return int(ping_response_match.groups()[0])
        raise ValueError("Unable to find a ping time in responses: {}".format(response))

    def ping(self, eui64, timeout=20.0, length=30, wait_for_response=True):
        """ Issue a ping-style command to another CLI device of address `eui64` by using `length` bytes of payload.
            Args:
                eui64 (int): destination node long address
                timeout (float): maximum time, in seconds, within which CLI should return command response
                length (int): ping command payload length
                wait_for_response (bool): if False, suppresses timeout exception

            Raises:
                CommandError: if CLI returns error
                TimeoutError: if timeout occurred
                ValueError: if unable to parse ping response

            Return:
                ping_time (int) in ms
        """
        cmd = Commands.PING.format(eui64=eui64, length=length)
        response = self.cli.write_command(cmd, wait_for_success=wait_for_response, timeout=timeout)

        if not wait_for_response:
            return None
        return CommandWrapper._parse_ping_response(''.join(response))

    def generic(self, eui64, ep, cluster, profile, cmd_id, payload=None, timeout=20.0):
        """ Issue a generic command with no payload.

            Args:
                eui64 (int): destination node long address
                ep (int): destination endpoint
                cluster (int): destination ZCL cluster
                profile (int): profile to which the destination ZCL cluster belongs
                cmd_id (int): ID of the ZCL command to issue
                payload (list): payload of the command - list of tuples to build payload from
                                tuple shall contain value to send and type of value
                                e.g. [(0x24, constants.UINT8_TYPE), (1, constants.UINT16_TYPE)]
                timeout (float): maximum time, in seconds, within which CLI should return command response

            Raises:
                CommandError: if CLI returns error
                TimeoutError: if timeout occurred
                TypeError: if type of value given as payload can not be handled

        """

        cmd = Commands.GENERIC_NO_PAYLOAD.format(eui64=eui64, ep=ep, cluster=cluster, profile=profile, cmd_id=cmd_id)
        if payload:
            octet_list = []
            for data in payload:
                value_hex_string = ''
                byte_len = 0
                if data[1] is constants.BOOL_TYPE:
                    byte_len = 1
                    value_formatter = "".join(["{value:0", str(byte_len * 2), "X}"])
                    value_hex_string = value_formatter.format(value=data[0])

                elif data[1] in range(constants.UINT8_TYPE, constants.UINT64_TYPE + 1):
                    byte_len = data[1] - constants.UINT8_TYPE + 1
                    value_formatter = "".join(["{value:0", str(byte_len * 2), "X}"])
                    value_hex_string = value_formatter.format(value=data[0])

                elif data[1] in range(constants.SINT8_TYPE, constants.SINT64_TYPE + 1):
                    byte_len = data[1] - constants.SINT8_TYPE + 1
                    value_formatter = "".join(["{value:0", str(byte_len * 2), "X}"])
                    # Handle signed int to string of hex conversion
                    mask = (2 ** (8 * byte_len) - 1)
                    value_hex_string = value_formatter.format(value=(data[0] & mask))

                elif data[1] in [constants.ENUM8_TYPE, constants.MAP8_TYPE]:
                    byte_len = 1
                    value_formatter = "".join(["{value:0", str(byte_len * 2), "X}"])
                    value_hex_string = value_formatter.format(value=data[0])

                else:
                    # Data types other than bool, or singed/unsigned int are handled by default
                    if type(data[0]) is str:
                        octet_list.append(data[0])
                    else:
                        raise TypeError("Can not parse type of argument, argument not a string - can not handle by default")

                # Take string of hex and put from end to start by taking two chars at once - little endian byte order
                for x in range(byte_len * 2, 0, -2):
                    octet_list.append(value_hex_string[x - 2: x])
            cmd = Commands.GENERIC_WITH_PAYLOAD.format(eui64=eui64, ep=ep, cluster=cluster, profile=profile,
                                                       cmd_id=cmd_id, payload="".join(octet_list))
        self.cli.write_command(cmd, timeout=timeout)

    def subscribe(self, eui64, ep, cluster, attr, profile=constants.DEFAULT_ZIGBEE_PROFILE_ID, min_interval=None, max_interval=None):
        """
            Sends a ZCL Configure Request Request.
            Args:
                eui64 (int): destination node long address
                ep (int): destination endpoint
                cluster(int): destination ZCL cluster
                attr(Attribute): attribute to report
                profile(int): profile to which the destination ZCL cluster belongs
                min_interval(int): minimal interval between attribute reports
                max_interval(int): maximal interval between attribute reports

            Raises:
                CommandError: if CLI returns error
                TimeoutError: if timeout occurred
        """
        cmd = Commands.SUBSCRIBE.format(eui64=eui64, ep=ep, cluster=cluster, profile=profile, attr_id=attr.id,
                                        attr_type=attr.type, min_interval=('' if min_interval is None else min_interval),
                                        max_interval=('' if max_interval is None else max_interval))
        self.cli.write_command(cmd, timeout=10.0)
