############################################################
# -*- coding: utf-8 -*-
#
# MOUNTCONTROL
#
# Python-based Tool for interaction with the 10micron mounts
# GUI with PyQT5 for python
# Python  v3.6.5
#
# Michael Würtenberger
# (c) 2018
#
# Licence APL2.0
#
############################################################
# standard libraries
import socket
import logging
# external packages
# local imports


class Connection(object):
    """
    The class Connection provides the command and reply interface to a 10 micron mount.
    There should be all commands and their return values be sent to the mount via
    IP and the responses.

    Define the number of chunks for the return bytes in case of not having them in
    bulk mode this is needed, because the mount computer  doesn't support a
    transaction base like number of chunks to be expected. It's just plain data and
    I have to find out myself how much it is. there are three types of commands:

          a) no reply               this is ok -> COMMAND_A
          b) reply without '#'      this is the bad part, don't like it -> COMMAND_B
          c) reply ended with '#'   this is normal feedback -> no special treatment

    The class itself need parameters for the host and port to be able to interact
    with the mount.

        >>> command = Connection(
        >>>                   host=('127.0.0.1', 3492),
        >>>                   )

    """

    __all__ = ['Connection',
               'communicate',
               ]
    version = '0.6'
    logger = logging.getLogger(__name__)

    # I don't want so wait to long for a response. In average I see values
    # shorter than 0.5 sec, so 5 seconds should be good
    SOCKET_TIMEOUT = 5

    # complete used command list to be checked first if valid
    # these are the commands, which were used in mountcontrol so far
    COMMANDS = [':AP', ':FLIP', ':GDUT', ':GDUTV', ':GMs', ':GREF', ':GRPRS',
                ':GRTMP', ':GS', ':GT', ':GTMP1', ':GVD', ':GVN', ':GVP', ':GVT',
                ':GVZ', ':Gdat', ':Gev', ':Gg', ':Gh', ':GINQ', ':Ginfo', ':Glms', ':Glmt',
                ':Gmte', ':GMACW', ':GMAC', ':Go', ':Gt', ':gtg', ':Guaf', ':MA', ':MS',
                ':MSao', ':MSap', ':PO', ':PO', ':PO', ':RT0', ':RT1', ':RT2', ':RT9',
                ':SREF', ':SRPRS', ':SRPRS', ':SRTMP', ':SRTMP', ':STOP', ':Sa', ':Sd',
                ':Sdat', ':Sev', ':Sev', ':Sg', ':Sg', ':Sh', ':Slms', ':Slmt', ':So',
                ':Sr', ':St', ':Suaf', ':Sw', ':Sz', ':U2',
                ':delalig', ':delalst', ':endalig', ':getain', ':getalp', ':getalst',
                ':hP', ':modelcnt', ':modeldel0', ':modelld0', ':modelnam',
                ':modelsv0', ':newalig', ':newalpt', ':shutdown',
                ]

    # Command list for commands which don't reply anything
    COMMAND_A = [':AP', ':hP', ':PO', ':RT0', ':RT1', ':RT2', ':RT9', ':STOP', ':U2',
                 ':hP', ':Suaf',
                 ]

    # Command list for commands which have a response, but have no end mark
    # mostly these commands response value of '0' or '1'
    COMMAND_B = [':FLIP', ':shutdown', ':GREF', ':Guaf',
                 ':MA', ':Sa', ':Sev', ':Sr', ':SREF', ':SRPRS',
                 ':SRTMP', ':Slmt', ':Slms', ':St', ':Sg', ':Sw', ':Sz', ':Sdat', ':Gdat',
                 ':So', ':Sh', ':Sd', ':MSap', ':MSao', ':MS',
                 ]

    def __init__(self,
                 host=None,
                 ):

        self.host = host

    def _validCommand(self, command):
        """
        validCommand test if command is valid and known.

        :param command: command for 10 micron to test
        :return: True if valid commands were issued
        """

        for key in sorted(self.COMMANDS, reverse=True):
            if command.startswith(key):
                return True
        return False

    def _validCommandSet(self, commandString):
        """
        validCommandSet test if all commands in the commandString are valid and known.

        :param commandString: command for 10 micron to test
        :return: True if valid commands were issued
        """

        commandSet = commandString.split('#')[:-1]
        for command in commandSet:
            if not self._validCommand(command):
                return False
        return True

    def _analyseCommand(self, commandString):
        """
        analyseCommand parses the provided commandString against the two command
        type A and B to evaluate if a response is expected and how many chunks of
        data show be received.

        the command slots will be sorted in reverse order to ensure that longer
        commands with the same leading characters will be tested first. otherwise
        the test will be ended before testing al commands.

        :param commandString:       string sent to the mount
        :return: chunksToReceive:   counted chunks
                 noResponse:        True, if we should not wait for receiving data
        """

        chunksToReceive = 0
        getData = False
        commandSet = commandString.split('#')[:-1]
        minBytes = 0
        for command in commandSet:
            foundCOMMAND_A = False
            for key in sorted(self.COMMAND_A, reverse=True):
                if command.startswith(key):
                    foundCOMMAND_A = True
                    break
            if not foundCOMMAND_A:
                getData = True
                for keyBad in sorted(self.COMMAND_B, reverse=True):
                    if command.startswith(keyBad):
                        minBytes += 1
                        break
                else:
                    chunksToReceive += 1
        return chunksToReceive, getData, minBytes

    def buildClient(self):
        """
        buildClient checks necessary information and tries to open a socket. if success
        it returns the client (socket connection)

        :return: client for socket connection if succeeded
        """
        if not self.host:
            message = 'no host defined'
            self.logger.error('{0}'.format(message))
            return None
        if not isinstance(self.host, tuple):
            message = 'host entry malformed'
            self.logger.error('{0}'.format(message))
            return None
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.settimeout(self.SOCKET_TIMEOUT)
        try:
            client.connect(self.host)
        except socket.timeout:
            # message = 'socket error timeout connect'
            client.close()
            # self.logger.debug('{0}'.format(message))
            return None
        except socket.error:
            # message = 'socket error general connect'
            client.close()
            # self.logger.debug('{0}'.format(message))
            return None
        except Exception as e:
            client.close()
            self.logger.error('{0}'.format(e))
            return None
        else:
            return client

    def sendData(self, client=None, commandString=''):
        """
        sendData sends all data of the command string out to the given socket client.

        :param client: socket client
        :param commandString: command to mount as string
        :return: success
        """
        try:
            client.sendall(commandString.encode())
        except socket.timeout:
            message = 'socket error timeout send'
            client.close()
            self.logger.debug('{0}'.format(message))
            return False
        except socket.error:
            message = 'socket error general send'
            client.close()
            self.logger.debug('{0}'.format(message))
            return False
        except Exception as e:
            client.close()
            self.logger.error('{0}'.format(e))
            return False
        else:
            return True

    def receiveData(self, client=None, numberOfChunks=0, minBytes=0):
        """
        receive Data waits on the give socket client for a number of chunks to be receive or
        a minimum set of bytes received. the chunks are delimited with #. the min bytes is
        necessary, because the mount computer has commands which giv a response without
        delimiter. this is bad, but status.

        :param client: socket client
        :param numberOfChunks: number of data chunks
        :param minBytes: minimum number of data bytes
        :return: success and response data
        """
        response = ''
        try:
            client.settimeout(self.SOCKET_TIMEOUT)
            while True:
                chunk = client.recv(4096).decode()
                if not chunk:
                    break
                response += chunk
                if not numberOfChunks:
                    if len(response) == minBytes:
                        break
                else:
                    if response.count('#') == numberOfChunks:
                        break
        except socket.timeout:
            message = 'socket error timeout response'
            response = ''
            self.logger.debug('{0}'.format(message))
            return False, response
        except socket.error:
            message = 'socket error general response'
            response = ''
            self.logger.debug('{0}, response: {1}'.format(message, response))
            return False, response
        except Exception as e:
            response = ''
            self.logger.error('{0}, response: {1}'.format(e, response))
            return False, response
        else:
            response = response.rstrip('#').split('#')
            self.logger.debug('response: {0}'.format(response))
            return True, response

    def communicate(self, commandString):
        """
        transfer open a socket to the mount, takes the command string for the mount,
        analyses it, check validity and finally if valid sends it to the mount. If
        response expected, wait for the response and returns the data.

        :param commandString:
        :return: success:           True or False for full transfer
                 response:          the data load
                 numberOfChunks:    number of responses chunks which were split with #
        """

        if not self._validCommandSet(commandString):
            self.logger.error('unknown commands: {0}'.format(commandString))
            return False, 'wrong commands', 0

        # analysing the command
        numberOfChunks, getData, minBytes = self._analyseCommand(commandString)
        logFormat = 'com: {0}, getData: {1}, minBytes: {2}, chunks: {3}, host: {4}'
        self.logger.debug(logFormat.format(commandString,
                                           getData,
                                           minBytes,
                                           numberOfChunks,
                                           self.host,
                                           ))

        # test if we have valid parameters
        client = self.buildClient()
        if client is None:
            return False, '', numberOfChunks

        suc = self.sendData(client=client,
                            commandString=commandString)
        if not suc:
            return False, '', numberOfChunks

        # if no response expected, we are finished
        if not getData:
            client.close()
            return True, '', numberOfChunks

        # get the response and close the client
        suc, response = self.receiveData(client=client,
                                         numberOfChunks=numberOfChunks,
                                         minBytes=minBytes)
        client.close()
        return suc, response, numberOfChunks
