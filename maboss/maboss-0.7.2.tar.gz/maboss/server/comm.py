# coding: utf-8
# MaBoSS (Markov Boolean Stochastic Simulator)
# Copyright (C) 2011-2018 Institut Curie, 26 rue d'Ulm, Paris, France
   
# MaBoSS is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
   
# MaBoSS is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
   
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA 

# Module: maboss/comm.py
# Authors: Eric Viara <viara@sysra.com>
# Date: May-December 2018

from __future__ import print_function

from .result import Result
#
# MaBoSS Communication Layer
#

PROTOCOL_VERSION_NUMBER = "1.0"

MABOSS_MAGIC = "MaBoSS-2.0"
PROTOCOL_VERSION = "Protocol-Version:"
FLAGS = "Flags:"
HEXFLOAT_FLAG = 0x1
OVERRIDE_FLAG = 0x2
AUGMENT_FLAG = 0x4
COMMAND = "Command:"
RUN_COMMAND = "run"
CHECK_COMMAND = "check"
PARSE_COMMAND = "parse"
NETWORK = "Network:"
CONFIGURATION = "Configuration:"
CONFIGURATION_EXPRESSIONS = "Configuration-Expressions:"
CONFIGURATION_VARIABLES = "Configuration-Variables:"
RETURN = "RETURN"
STATUS = "Status:"
ERROR_MESSAGE = "Error-Message:"
STATIONARY_DISTRIBUTION = "Stationary-Distribution:"
TRAJECTORY_PROBABILITY = "Trajectory-Probability:"
TRAJECTORIES = "Trajectories:"
FIXED_POINTS = "Fixed-Points:"
RUN_LOG = "Run-Log:"

class HeaderItem:

    def __init__(self, directive, _from = None, to = None, value = None):
        self._directive = directive
        self._from = _from
        self._to = to
        self._value = value

    def getDirective(self):
        return self._directive

    def getFrom(self):
        return self._from

    def getTo(self):
        return self._to

    def getValue(self):
        return self._value

class DataStreamer:

    @staticmethod
    def buildStreamData(client_data, hints = None):
        data = ""
        offset = 0
        o_offset = 0

        if hints:
            hexfloat = "hexfloat" in hints and hints["hexfloat"]
            override = "override" in hints and hints["override"]
            augment = "augment" in hints and hints["augment"]
            verbose = "verbose" in hints and hints["verbose"]
        else:
            hexfloat = False
            override = False
            augment = False
            verbose = False

        command = client_data.getCommand()
        flags = 0
        if hexfloat:
            flags |= HEXFLOAT_FLAG
        if override:
            flags |= OVERRIDE_FLAG
        if augment:
            flags |= AUGMENT_FLAG

        header = MABOSS_MAGIC + "\n"
        header += PROTOCOL_VERSION + PROTOCOL_VERSION_NUMBER + "\n";
        header += FLAGS + str(flags) + "\n";
        header += COMMAND + command + "\n";

        config_data = client_data.getConfig()
        offset += len(config_data)
        data += config_data

        (header, o_offset) = DataStreamer._add_header(header, CONFIGURATION, o_offset, offset)

        network_data = client_data.getNetwork()
        offset += len(network_data)
        data += network_data

        (header, o_offset) = DataStreamer._add_header(header, NETWORK, o_offset, offset)

        if verbose:
            print("======= sending header\n", header)
            print("======= sending data[0:200]\n", data[0:200], "\n[...]\n")
        return header + "\n" + data

    @staticmethod
    def parseStreamData(ret_data, simulation, hints = None):
        verbose = False
        if hints:
            verbose = "verbose" in hints and hints["verbose"]

        result_data = Result(simulation)
        magic = RETURN + " " + MABOSS_MAGIC
        magic_len = len(magic)
        if ret_data[0:magic_len] != magic:
            result_data.setStatus(1)
            result_data.setErrorMessage("magic " + magic + " not found in header")
            return result_data

        offset = magic_len
        pos = ret_data.find("\n\n", magic_len)
        if pos < 0:
            result_data.setStatus(2)
            result_data.setErrorMessage("separator double nl found in header")
            return result_data

        offset += 1
        header = ret_data[offset:pos+1]
        data  = ret_data[pos+2:]
        if verbose:
            print("======= receiving header \n", header)
            print("======= receiving data[0:200]\n", data[0:200], "\n[...]\n")

        header_items = []
        err_data = DataStreamer._parse_header_items(header, header_items)
        if err_data:
            result_data.setStatus(3)
            result_data.setErrorMessage(err_data)
            return result_data

        for header_item in header_items:
            directive = header_item.getDirective()
            if directive == STATUS:
                result_data.setStatus(int(header_item.getValue()))
            elif directive == ERROR_MESSAGE:
                result_data.setErrorMessage(header_item.getValue())
            else:
                data_value = data[header_item.getFrom():header_item.getTo()+1]
                if directive == STATIONARY_DISTRIBUTION:
                    result_data.setStatDist(data_value)
                elif directive == TRAJECTORY_PROBABILITY:
                    result_data.setProbTraj(data_value)
                elif directive == TRAJECTORIES:
                    result_data.setTraj(data_value)
                elif directive == FIXED_POINTS:
                    result_data.setFP(data_value)
                elif directive == RUN_LOG:
                    result_data.setRunLog(data_value)
                else:
                    result_data.setErrorMessage("unknown directive " + directive)
                    result_data.setStatus(4)
                    return result_data

        return result_data

    @staticmethod
    def _parse_header_items(header, header_items):
        opos = 0
        pos = 0
        while True:
            pos = header.find(':', opos)
            if pos < 0:
                break
            directive = header[opos:pos+1]
            opos = pos+1
            pos = header.find("\n", opos)
            if pos < 0:
                return "newline not found in header after directive " + directive

            value = header[opos:pos]
            opos = pos+1
            pos2 = value.find("-")
            if directive == STATUS or directive == ERROR_MESSAGE:
                header_items.append(HeaderItem(directive = directive, value = value))
            elif pos2 >= 0:
                header_items.append(HeaderItem(directive = directive, _from = int(value[0:pos2]), to = int(value[pos2+1:])))
            else:
                return "dash - not found in value " + value + " after directive " + directive

        return ""

    @staticmethod
    def _add_header(header, directive, o_offset, offset):
        if o_offset != offset:
            header += directive + str(o_offset) + "-" + str(offset-1) + "\n"

        return (header, offset)
