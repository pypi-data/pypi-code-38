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

from ..base import CommandWrapper as BaseCmdWrapper

class Commands:
    """ CLI Commands to be used with firmware which includes Logging module.
    """
    # Main command used in order to access LOG subcommands
    MAIN = 'log'

    # Available LOG commands
    ENABLE = ' '.join([MAIN, 'enable {level} {module}'])

class CommandWrapper(BaseCmdWrapper):
    """ This class adds an interface for sending LOG commands and receiving parsed
        responses through Zigbee CLI by calling methods on a device instance.
    """

    def enable_logs(self, module, level="info"):
        """ Enable the logs printing in the CLI

            Args:
                module(str): Module which to turn on the report.
                level(str): Level of the logging to turn on.
        """
        cmd = Commands.ENABLE.format(module=module, level=level)
        self.cli.write_command(cmd, wait_for_success=False)

    def gather_logs(self, aquisition_time=0):
        """ Gather the logs and also clears the received logs.

            Args:
                aquisition_time: Time to collect logs

            Returns: the list of captured logs. Every log is a dictionary of
                     module, level and string of the log.
        """
        logs = self.cli.retrieved_logs(aquisition_time=aquisition_time)
        self.cli.empty_logs()
        return logs