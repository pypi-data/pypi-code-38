from trosnoth.const import ZONE_CAP_DISTANCE
from trosnoth.triggers.base import Trigger
from trosnoth.utils import math
from trosnoth.utils.event import Event


class StandardTrosballScoreTrigger(Trigger):
    '''
    When the trosball goes through a target orb, trigger an event.
    '''

    def __init__(self, *args, **kwargs):
        super(StandardTrosballScoreTrigger, self).__init__(*args, **kwargs)
        self.onTrosballScore = Event(['team', 'player'])

    def doActivate(self):
        self.world.onUnitsAllAdvanced.addListener(self.unitsHaveAdvanced)

    def doDeactivate(self):
        self.world.onUnitsAllAdvanced.removeListener(self.unitsHaveAdvanced)

    def unitsHaveAdvanced(self):
        for team in self.world.teams:
            distance = math.distance(
                self.world.trosballManager.getPosition(),
                self.world.trosballManager.getTargetZoneDefn(team).pos)
            if distance < ZONE_CAP_DISTANCE:
                self.onTrosballScore(
                    team, self.world.trosballManager.lastTrosballPlayer)
