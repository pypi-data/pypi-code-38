import logging

from trosnoth.const import (
    NOT_ENOUGH_COINS_REASON, PLAYER_DEAD_REASON, CANNOT_REACTIVATE_REASON,
    GAME_NOT_STARTED_REASON, TOO_CLOSE_TO_EDGE_REASON,
    TOO_CLOSE_TO_ORB_REASON, NOT_IN_DARK_ZONE_REASON, ALREADY_DISRUPTED_REASON,
    INVALID_UPGRADE_REASON, DISABLED_UPGRADE_REASON,
)
from trosnoth.messages.base import (
    AgentRequest, ServerCommand, ServerResponse, ClientCommand,
)
from trosnoth.model.universe_base import NO_PLAYER

log = logging.getLogger(__name__)


class BuyUpgradeMsg(AgentRequest):
    '''
    Signal from interface that a buy has been requested.

    In order for everything to stay in sync, an upgrade purchase works in 3
    steps.

    1. The client sends BuyUpgradeMsg.
    2. The server checks that the coins are avaliable, and replies with
        UpgradeApprovedMsg.
    3. The client sends PlayerHasUpgradeMsg, which is then broadcast to all
        clients.

    To make launching of grenades more responsive, there is a special flag on
    Upgrade classes called doNotWaitForServer. If this flag is set, the client
    assumes that the purchase is successful unless it hears otherwise, and the
    server broadcasts PlayerHasUpgradeMsg immediately at step 2. Step 3 is not
    performed in this case.
    '''
    idString = b'GetU'
    fields = 'upgradeType', 'tickId'
    packspec = 'cH'
    timestampedPlayerRequest = True

    def clientValidate(self, localState, world, sendResponse):
        upgrade = world.getUpgradeType(self.upgradeType)
        if not upgrade.doNotWaitForServer:
            # Don't bother trying to validate locally, let the server decide.
            return True

        player = localState.player
        denialReason = self.getDenialReason(player, upgrade)
        if denialReason:
            response = CannotBuyUpgradeMsg(denialReason)
            response.local = True
            sendResponse(response)
            return False
        return True

    def applyRequestToLocalState(self, localState):
        upgrade = localState.world.getUpgradeType(self.upgradeType)
        if upgrade.doNotWaitForServer:
            localState.player.activateItemByCode(
                self.upgradeType, local=localState)

    def serverApply(self, game, agent):
        player = agent.player
        if player is None:
            return

        upgrade = player.world.getUpgradeType(self.upgradeType)
        denialReason = self.getDenialReason(player, upgrade)
        if denialReason:
            agent.messageToAgent(CannotBuyUpgradeMsg(denialReason))
        else:
            if player.items.server_isApproved(upgrade):
                # Silently ignore requests for an item that's already approved
                return
            self._processUpgradePurchase(game, agent, player, upgrade)

    def getDenialReason(self, player, upgrade):
        from trosnoth.model.upgrades import allUpgrades

        if not player.world.abilities.upgrades:
            return GAME_NOT_STARTED_REASON
        if player.dead:
            return PLAYER_DEAD_REASON

        if upgrade not in allUpgrades:
            return INVALID_UPGRADE_REASON

        if not upgrade.enabled:
            return DISABLED_UPGRADE_REASON

        requiredCoins = self._getRequiredCoins(player, upgrade)
        if requiredCoins is None:
            return CANNOT_REACTIVATE_REASON

        if player.coins < requiredCoins:
            return NOT_ENOUGH_COINS_REASON

        return self._checkUpgradeConditions(player, upgrade)

    def _getRequiredCoins(self, player, upgradeClass):
        existing = player.items.get(upgradeClass)
        if existing:
            return existing.getReactivateCost()
        return upgradeClass.requiredCoins

    def _checkUpgradeConditions(self, player, upgrade):
        '''
        Checks whether the conditions are satisfied for the given player to be
        able to purchase an upgrade of the given kind. Returns None if no
        condition is violated, otherwise returns a one-byte reason code for why
        the upgrade cannot be purchased.
        '''
        from trosnoth.model.upgrades import MinimapDisruption

        if upgrade is MinimapDisruption:
            if player.team is None or player.team.usingMinimapDisruption:
                return ALREADY_DISRUPTED_REASON

        return None

    def _processUpgradePurchase(self, game, agent, player, upgrade):
        '''
        Sends the required sequence of messages to gameRequests to indicate
        that the upgrade has been purchased by the player.
        '''
        requiredCoins = self._getRequiredCoins(player, upgrade)
        game.sendServerCommand(PlayerCoinsSpentMsg(player.id, requiredCoins))

        if upgrade.doNotWaitForServer:
            game.sendServerCommand(PlayerHasUpgradeMsg(
                upgrade.upgradeType, self.tickId, player.id))
        else:
            player.items.server_approve(upgrade)
            agent.messageToAgent(UpgradeApprovedMsg(upgrade.upgradeType))

        player.onCoinsSpent(requiredCoins)


class PlayerHasUpgradeMsg(ClientCommand):
    '''
    Sent by the local client when it receives word from the server that an
    upgrade purchase has been approved.
    '''
    idString = b'GotU'
    fields = 'upgradeType', 'tickId', 'playerId'
    packspec = 'cHc'
    playerId = NO_PLAYER
    timestampedPlayerRequest = True

    def applyRequestToLocalState(self, localState):
        if __debug__:
            # If doNotWaitForServer is set, this message does not originate
            # from the client, so applyRequestToLocalState() is never called.
            upgradeClass = localState.world.getUpgradeType(self.upgradeType)
            assert not upgradeClass.doNotWaitForServer

        item = localState.player.activateItemByCode(
            self.upgradeType, local=localState)

    def serverApply(self, game, agent):
        upgradeClass = game.world.getUpgradeType(self.upgradeType)
        if agent.player and agent.player.items.server_isApproved(upgradeClass):
            self.playerId = agent.player.id
            game.sendServerCommand(self)

    def applyOrderToWorld(self, world):
        player = world.getPlayer(self.playerId)
        player.activateItemByCode(self.upgradeType)

    def applyOrderToLocalState(self, localState, world):
        if localState.player and self.playerId == localState.player.id:
            upgradeClass = world.getUpgradeType(self.upgradeType)
            upgrade = localState.player.items.get(upgradeClass)
            if upgrade:
                upgrade.serverVerified(localState)


class PlayerCoinsSpentMsg(ServerCommand):
    '''
    This message is necessary, because without it a client can't always tell
    where the PlayerHasUpgradeMsg pulled all its coins from.
    '''
    idString = b'Spnt'
    fields = 'playerId', 'count'
    packspec = 'cI'


class AwardPlayerCoinMsg(ServerCommand):
    idString = b'Coin'
    fields = 'playerId', 'count', 'sound'
    packspec = 'cI?'
    sound = False

    def applyOrderToWorld(self, world):
        player = world.getPlayer(self.playerId)
        if player:
            player.incrementCoins(self.count)
            if self.sound:
                world.onCoinSound(player)


class SetPlayerCoinsMsg(ServerCommand):
    idString = b'SetC'
    fields = 'playerId', 'value'
    packspec = 'cI'

    def applyOrderToWorld(self, world):
        player = world.getPlayer(self.playerId)
        if player:
            player.setCoins(self.value)


class CannotBuyUpgradeMsg(ServerResponse):
    '''
    Tag is the value sent in BuyUpgradeMsg.
    Valid reasonId values are defined in trosnoth.const.
    '''
    idString = b'NotU'
    fields = 'reasonId'
    packspec = 'c'
    local = False

    def applyOrderToLocalState(self, localState, world):
        if self.local:
            return
        item = localState.popUnverifiedItem()
        if item:
            item.deniedByServer(localState)


class UpgradeApprovedMsg(ServerResponse):
    '''
    Signals to the player that's trying to buy an upgrade that the purchase has
    been successful, and the player should proceed to send a
    PlayerHasUpgradeMsg to use the upgrade. This back and forth is necessary
    because the using of the upgrade needs to happen based on the location of
    the player on their own client's screen, not based on the server's idea of
    where the client is.
    '''
    idString = b'ByOk'
    fields = 'upgradeType'
    packspec = 'c'


class UpgradeChangedMsg(ServerCommand):
    '''
    A message for the clients that informs them of a change in an upgrade stat.
    statType may be:
        'S' - coin cost
        'T' - time limit
        'X' - explosion radius
        'E' - enabled
    '''
    idString = b'UpCh'
    fields = 'upgradeType', 'statType', 'newValue'
    packspec = 'ccf'
