import logging

from trosnoth.utils.message import UnhandledMessage
from trosnoth.utils.netmsg import NetworkMessage

log = logging.getLogger(__name__)


TICK_LIMIT = 1 << 16 - 1


####################
# Base Classes
####################

class AgentRequest(NetworkMessage):
    isControl = False
    timestampedPlayerRequest = False

    def clientValidate(self, localState, world, sendResponse):
        '''
        Called on the client to determine whether this message should even be
        passed on. Should return a boolean indication whether to continue to
        propagate this message.
        '''
        return True

    def applyRequestToLocalState(self, localState):
        '''
        Called on client->server messages before the message is sent to the
        server. This is used to update the local state information.
        '''
        pass

    def serverApply(self, game, agent):
        '''
        Called server-side for requests from agents.

        game:       a LocalGame
        agent:      an Agent

        Typically, a serverApply method will either do nothing, call
        game.sendServerCommand(), call game.sendResync(), or call
        agent.messageToAgent().
        '''
        raise UnhandledMessage('Validator did not expect to receive %s' % (
            self.__class__.__name__,))


class ServerCommand(NetworkMessage):
    isControl = False

    def applyOrderToWorld(self, world):
        '''
        Called when this order arrives at a Universe (on client and server) to
        update the state of the universe.
        '''
        pass

    def applyOrderToLocalState(self, localState, world):
        '''
        Called when this order arrives at the client, to update the local state
        of the client.
        '''
        pass


class ServerResponse(ServerCommand):
    isControl = True


class ClientCommand(AgentRequest, ServerCommand):
    '''
    A command that originates on the client and is validated on the server
    before being passed on.
    '''
    pass
