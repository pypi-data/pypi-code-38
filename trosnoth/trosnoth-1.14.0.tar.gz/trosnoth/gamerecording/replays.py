import logging
import struct

from twisted.internet import reactor

from trosnoth.const import TICK_PERIOD
from trosnoth.messages import TickMsg
from trosnoth.model.hub import Hub
from trosnoth.network.networkDefines import serverVersion
from trosnoth.network.client import clientMsgs
from trosnoth.utils.netmsg import MessageTypeError
from trosnoth.utils.twist import WeakLoopingCall
from trosnoth.utils.unrepr import unrepr

log = logging.getLogger(__name__)


class ReplayRecorder(object):
    def __init__(self, world, filename):
        self.filename = filename
        self.world = world
        self.stopped = False

        initialData = self.world.dumpEverything()
        initialData['serverVersion'] = serverVersion
        self.file = ReplayOutputFile(filename, initialData)

    def consumeMsg(self, msg):
        if self.stopped:
            return
        self.file.writeMessage(msg)

    def stop(self):
        if not self.stopped:
            self.file.close()
            self.stopped = True


class ReplayOutputFile(object):
    def __init__(self, filename, initialData):
        self.file = open(filename, 'wb')
        data = repr(initialData).encode('utf-8')
        self.file.write(struct.pack('!I', len(data)))
        self.file.write(data)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.file.close()
        return False

    def writeMessage(self, msg):
        msgData = msg.pack()
        self.file.write(struct.pack('!I', len(msgData)))
        self.file.write(msgData)

    def close(self):
        self.file.close()


class ReplayFileError(Exception):
    '''
    There is a problem with the replay file format.
    '''


def readReplay(fileObject):
    '''
    Returns (settings, messageIterator) where settings is a dict of world
    settings and messageIterator iterates through the messages in this replay.

    May raise ReplayFileError if the initial file settings cannot be read.
    '''
    try:
        length = struct.unpack('!I', fileObject.read(4))[0]
        data = fileObject.read(length)
        if len(data) != length:
            raise ReplayFileError('invalid replay format')
        decodedData = data.decode('utf-8')
    except (struct.error, MemoryError, UnicodeDecodeError):
        raise ReplayFileError('invalid replay format')

    try:
        settings = unrepr(decodedData)
    except Exception:
        raise ReplayFileError('invalid replay format')

    return settings, readReplayMessages(fileObject)


def readReplayMessages(fileObject):
    while True:
        data = fileObject.read(4)
        if not data:
            break

        length = struct.unpack('!I', data)[0]
        data = fileObject.read(length)
        try:
            yield clientMsgs.buildMessage(data)
        except MessageTypeError:
            log.warning('WARNING: UNKNOWN MESSAGE: %r' % (data,))


class ReplayPlayer(Hub):
    '''
    Emulates a normal server by outputting the same messages that a server once
    did.
    '''

    def __init__(self, filename, *args, **kwargs):
        super(ReplayPlayer, self).__init__(*args, **kwargs)
        self.tickPeriod = TICK_PERIOD
        self.finished = False
        self.loop = WeakLoopingCall(self, 'tick')
        self.agentIds = []
        self.nextAgentId = 0

        self.settings, self.msgIterator = readReplay(open(filename, 'rb'))

    def popSettings(self):
        result, self.settings = self.settings, None
        return result

    def start(self):
        self.loop.start(self.tickPeriod)

    def stop(self):
        if self.loop.running:
            self.loop.stop()

    def tick(self):
        while True:
            try:
                msg = next(self.msgIterator)
            except StopIteration:
                self.finished = True
                if self.node:
                    while self.agentIds:
                        agentId = self.agentIds.pop(0)
                        # Give 2 seconds before ending the replay
                        reactor.callLater(
                            2, self.node.agentDisconnected, agentId)
                self.loop.stop()
                break

            self.node.gotServerCommand(msg)
            if isinstance(msg, TickMsg):
                break

    def connectNewAgent(self, authTag=0):
        agentId = self.nextAgentId
        self.nextAgentId += 1
        self.agentIds.append(agentId)
        return agentId

    def disconnectAgent(self, agentId):
        self.agentIds.remove(agentId)

    def sendRequestToGame(self, agentId, msg):
        pass
