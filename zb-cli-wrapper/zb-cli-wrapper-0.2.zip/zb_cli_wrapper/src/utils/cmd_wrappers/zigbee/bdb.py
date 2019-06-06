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

class Role:
    """ Enumeration describing a Zigbee device role.
    """
    COORDINATOR = 'zc'
    ROUTER = 'zr'
    END_DEVICE = 'zed'

class Commands:
    """ CLI Commands to be used with firmware which includes Zigbee CLI component with BDB commands.
    """
    # Main command used in order to access BDB subcommands
    MAIN = 'bdb'

    # Available BDB commands
    ROLE = ' '.join([MAIN, 'role {role}'])
    START = ' '.join([MAIN, 'start'])
    IC_ADD = ' '.join([MAIN, 'ic add {ic:036X} {eui64:016X}'])
    IC_SET = ' '.join([MAIN, 'ic set {ic:036X}'])
    IC_POLICY = ' '.join([MAIN, 'ic policy {state}'])
    PAN_ID = ' '.join([MAIN, 'panid {panid}'])
    CHANNEL_GET = ' '.join([MAIN, 'channel'])
    CHANNEL_SET = ' '.join([MAIN, 'channel {bitmask:08X}'])
    LEGACY = ' '.join([MAIN, 'legacy {state}'])
    FACTORY_RESET = ' '.join([MAIN, 'factory_reset'])

class CommandWrapper(BaseCmdWrapper):
    """ This class adds an interface for sending BDB commands and receiving parsed
        responses through Zigbee CLI by calling methods on a device instance.
    """

    def start(self):
        """ Start top level commissioning.

            Raises:
                ValueError: if received result with an unknown formatting
                CommandError: if CLI returns error
                TimeoutError: if timeout occurred
        """
        self.cli.write_command(Commands.START)

    @property
    def role(self):
        """ Reads device role.

            Raises:
                ValueError: if received result with an unknown formatting
                CommandError: if CLI returns error
                TimeoutError: if timeout occurred
        """
        cmd = Commands.ROLE.format(role='')
        responses = self.cli.write_command(cmd)
        if responses[0] == str(Role.COORDINATOR):
            return Role.COORDINATOR
        elif responses[0] == str(Role.ROUTER):
            return Role.ROUTER
        elif responses[0] == str(Role.END_DEVICE):
            return Role.END_DEVICE
        else:
            raise ValueError("Unrecognized Zigbee role received: {}".format(responses[0]))

    @role.setter
    def role(self, role):
        """ Set the device role.

            Args:
                role (str): new device role. Can be either 'zc' or 'zr'
                timeout (float): maximum time, in seconds, within which CLI should return command response

            Raises:
                CommandError: if CLI returns error
                TimeoutError: if timeout occurred

            Return:
                response
        """
        cmd = Commands.ROLE.format(role=role)
        return self.cli.write_command(cmd)

    @property
    def panid(self):
        """ Reads PAN ID.

            Raises:
                ValueError: if received result with an unknown formatting
                CommandError: if CLI returns error
                TimeoutError: if timeout occurred
        """
        cmd = Commands.PAN_ID.format(panid='')
        responses = self.cli.write_command(cmd)
        return responses[0]

    @panid.setter
    def panid(self, panid):
        """ Set the device PAN ID. 

            The PAN ID must be set before calling start().

            Args:
                panid (int): device PAN ID

            Raises:
                CommandError: if CLI returns error
                TimeoutError: if timeout occurred

            Return:
                response
        """
        cmd = Commands.PAN_ID.format(panid=panid)
        return self.cli.write_command(cmd)

    def ic_add(self, ic, eui64):
        """ Add the Install Code to the Trust Center.

            Args:
                ic (int): Install Code of the device to introduce
                eui64 (int): EUI64 address of the device to introduce

            Raises:
                CommandError: if CLI returns error
                TimeoutError: if timeout occurred

            Return:
                response
        """
        cmd = Commands.IC_ADD.format(ic=ic, eui64=eui64)
        return self.cli.write_command(cmd)

    def ic_set(self, ic):
        """ Set the Install Code on the device.

            Args:
                ic (int): Install Code of the device to introduce

            Raises:
                CommandError: if CLI returns error
                TimeoutError: if timeout occurred

            Return:
                response
        """
        cmd = Commands.IC_SET.format(ic=ic)
        return self.cli.write_command(cmd)

    def ic_set_policy(self, enabled):
        """ Set the Install Code policy of the Trust Center.

            Args:
                enabled (bool): Whether the policy should be enabled.

            Raises:
                CommandError: if CLI returns error
                TimeoutError: if timeout occurred

            Return:
                response
        """
        cmd = Commands.IC_POLICY.format(state="enable" if enabled else "disable")
        return self.cli.write_command(cmd)

    def factory_reset(self):
        """ Perform factory reset by local action as stated in BDB specification chapter 9.5

            Raises:
                CommandError: if CLI returns error
                TimeoutError: if timeout occurred
        """
        self.cli.write_command(Commands.FACTORY_RESET)

    @property
    def legacy(self):
        """ Read the state of Legacy mode.
 
            Raises:
                CommandError: if CLI returns error
                TimeoutError: if CLI timeout occured

            Return:
                True if enabled, False if disabled
        """
        cmd = Commands.LEGACY.format(state="")
        response = self.cli.write_command(cmd)

        if response[0] == "on":
            return True
        if response[0] == "off":
            return False
        raise CommandError("Unknown value")

    @legacy.setter
    def legacy(self, enabled):
        """ Set or unset the legacy (pre ZB 3.0) mode

            Args:
                enabled (bool): Whether the legacy should be enabled.

            Raises:
                CommandError: if CLI returns error
                TimeoutError: if timeout occurred

            Return:
                response
        """
        cmd = Commands.LEGACY.format(state="enable" if enabled else "disable")
        return self.cli.write_command(cmd)

    @property
    def channel(self):
        """ Read CLI channels list.

            Raises:
                CommandError: if CLI returns error
                TimeoutError: if CLI timeout occured

            Return:
                channels (tuple) as a tuple with two lists of channels - primary and secondary
        """
        response = self.cli.write_command(Commands.CHANNEL_GET)
        primary_channel_rgx = re.compile('(Primary\ *channel\ *\(\ *s\ *\)\s*:\ *)((\d{2}\ *)*)')
        secondary_channel_rgx = re.compile('(Secondary\ *channel\ *\(\ *s\ *\)\s*:\ *)((\d{2}\ *)*)')

        primary_channel_match = primary_channel_rgx.search(response[0]).groups()
        secondary_channel_match = secondary_channel_rgx.search(response[1]).groups()

        primary_channels = [int(x) for x in primary_channel_match[1].split()]
        secondary_channels = [int(x) for x in secondary_channel_match[1].split()]

        return (primary_channels, secondary_channels)

    @channel.setter
    def channel(self, new_channel_list):
        """ Set CLI channels.

            Args:
                new_channel_list (list): list of channels to set

            Raises:
                CommandError: if CLI returns error
                TimeoutError: if CLI timeout occured

            Return:
                 response
        """
        channel_bitmask = 0
        for channel_nbr in new_channel_list:
            channel_bitmask |= (2 ** channel_nbr)

        return self.cli.write_command(Commands.CHANNEL_SET.format(bitmask=channel_bitmask))
