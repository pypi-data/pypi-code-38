import logging

from trosnoth.const import (
    GAME_FULL_REASON, UNAUTHORISED_REASON, NICK_USED_REASON, BAD_NICK_REASON,
    USER_IN_GAME_REASON,
)
from trosnoth.trosnothgui.ingame.dialogs import (
    JoinGameDialog, JoiningDialog, SpectateResult,
)
from trosnoth.gui.framework.dialogbox import DialogResult

log = logging.getLogger(__name__)


class JoinGameController(object):
    '''
    Shows and hides the join game dialog.
    '''

    def __init__(self, app, gameInterface, game):
        self.app = app
        self.world = game.world
        self.interface = gameInterface
        self.joined = False
        self.gameInterface = gameInterface
        self.selectedSpectate = False

        self.joiningScreen = JoiningDialog(self.app, self)

        self.joinGameDialog = JoinGameDialog(self.app, self, self.world)
        self.joinGameDialog.onClose.addListener(self._joinDlgClose)

    def start(self):
        '''
        Called by GameInterface when the player's agent has been added.
        '''
        self.maybeShowJoinDialog(autoJoin=True)

    def maybeShowJoinDialog(self, autoJoin=False):
        if self.world.isIncomplete:
            # Have not received full world data. Wait until reset message is
            # received.
            return

        if self.interface.player:
            return

        self.selectedSpectate = False
        nick = self.app.identitySettings.nick
        head = self.app.identitySettings.head
        if autoJoin and nick and self.world.isServer:
            # Practise or local game. Join automatically.
            self.attemptGameJoin(nick, head, None)
        elif not self.joinGameDialog.showing:
            self.joinGameDialog.show()

    def gotWorldReset(self):
        '''
        Called by GameInterface whenever a world reset is received.
        '''
        if self.joinGameDialog.showing:
            self.joinGameDialog.refreshTeamButtons()
        elif not self.selectedSpectate:
            self.maybeShowJoinDialog()

    def hide(self):
        if self.joinGameDialog.showing:
            self.joinGameDialog.close()
        if self.joiningScreen.showing:
            self.joiningScreen.close()

    def _joinDlgClose(self):
        if self.joinGameDialog.result is None:
            return
        if self.joinGameDialog.result == SpectateResult:
            self.selectedSpectate = True
            self.interface.spectate()
        elif self.joinGameDialog.result != DialogResult.OK:
            self.interface.joinDialogCancelled()
        else:
            nick = self.joinGameDialog.nickBox.value.strip()
            head = self.joinGameDialog.heads.getSelectedValue()
            self.app.identitySettings.setInfo(nick, head)

            team = self.joinGameDialog.selectedTeam
            self.attemptGameJoin(nick, head, team)

    def attemptGameJoin(self, nick, head, team):
        self.joiningScreen.show(nick)
        self.interface.joinGame(nick, head, team)

    def showMessage(self, text):
        self.joinGameDialog.cantJoinYet.setText(text)

    def cancelJoin(self, sender):
        # TODO: This doesn't actually cancel anything
        self.joiningScreen.close()
        self.maybeShowJoinDialog()

    def joinFailed(self, reason):
        if self.joiningScreen.showing:
            self.joiningScreen.close()
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
