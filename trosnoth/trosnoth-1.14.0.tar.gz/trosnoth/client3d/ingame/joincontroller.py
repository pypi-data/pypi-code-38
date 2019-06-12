import logging

from trosnoth.const import (
    GAME_FULL_REASON, UNAUTHORISED_REASON, NICK_USED_REASON, BAD_NICK_REASON,
    USER_IN_GAME_REASON,
)

log = logging.getLogger(__name__)


class JoinGameController(object):
    '''
    Shows and hides the join game dialog.
    '''

    def __init__(self, app, gameInterface, game):
        self.app = app
        self.world = game.world
        self.agent = gameInterface
        self.joined = False
        self.joiningInfo = None
        self.selectedSpectate = False

    def start(self):
        '''
        Called by PandaUIAgent when the user's agent has been added.
        '''
        self.maybeShowJoinDialog(autoJoin=True)

    def maybeShowJoinDialog(self, autoJoin=False):
        if self.world.isIncomplete:
            # Have not received full world data. Wait until reset message is
            # received.
            return

        if self.agent.player:
            return

        self.selectedSpectate = False
        nick = self.app.identitySettings.nick
        if autoJoin and nick and self.world.isServer:
            # Practise or local game. Join automatically.
            self.attemptGameJoin(nick, None)
        else:
            self.showJoinDialog()

    def showJoinDialog(self):
        # TODO
        log.error('Panda3D join dialog not yet coded')
        self.selectedSpectate = True
        self.agent.spectate()
        # Also:
        # self.agent.joinDialogCancelled()
        # self.attemptGameJoin(nick, team)

    def gotWorldReset(self):
        '''
        Called by PandaUIAgent whenever a world reset is received.
        '''
        if self.joinGameDialog.showing:
            self.joinGameDialog.refreshTeamButtons()
        elif not self.selectedSpectate:
            self.maybeShowJoinDialog()

    def hide(self):
        # TODO
        pass

    def attemptGameJoin(self, nick, team):
        self.joiningInfo = nick, team
        self.agent.joinGame(nick, team)

    def showMessage(self, text):
        # TODO
        pass

    def cancelJoin(self, sender):
        # TODO: cancel joining
        self.maybeShowJoinDialog()

    def joinFailed(self, reason):
        self.maybeShowJoinDialog()

        if reason == GAME_FULL_REASON:
            # Team is full.
            self.showMessage('That team is full!')
        elif reason == NICK_USED_REASON:
            # Nickname is already being used.
            self.showMessage('That name is already being used!')
        elif reason == BAD_NICK_REASON:
            # Nickname is too short or long.
            self.showMessage('That name is not allowed!')
        elif reason == UNAUTHORISED_REASON:
            self.showMessage('You are not authorised to join!')
        elif reason == USER_IN_GAME_REASON:
            self.showMessage('Cannot join the same game twice!')
        elif reason == 'timeout':
            self.showMessage('Join timed out.')
        else:
            # Unknown reason.
            self.showMessage('Join failed: %r' % (reason,))
