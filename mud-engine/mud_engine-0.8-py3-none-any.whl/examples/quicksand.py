from mud_engine import MUDEngine
from mud_engine.geography import Geography
from mud_engine.base import StopAction
from mud_engine.player import PlayerState
from mud_engine.player import Standing
from mud_engine.player import Dead
from mud_engine.commands import Command
from mud_engine.commands import MagicSpell
from mud_engine.communication import NoColor
from mud_engine.communication import LightRed
from mud_engine.communication import Yellow

@MagicSpell
class Fly(Command):

    def do(self):
        self.player.add_state(Flying)

class Flying(PlayerState):

    # This state lasts for 10 heart beats
    duration = 10

    def deactivate(self):

        # When the flying state expires, we need to display that the user is landing
        # PlayerState.heartbeat will remove the state from the player, no need to do anything here.
        self.player.message_location("\r\nYou gently float to the ground\r\n",
                                        f"\r\n{self.player.name} floats to the ground\r\n")

        if isinstance(self.player.location, QuickSand):
            self.player.add_state(Sinking)
        else:
            self.player.add_state(Standing)

    def activate(self):
        if self.player.in_state("sinking"):
            self.player.get_state("sinking").deactivate()
            self.player.remove_state("sinking")
        self.player.remove_state("standing")

        self.player.message_location(f"{Yellow}You lift into the air{NoColor}\r\n", f"{self.player.name} lifts into the air")

class Sinking(PlayerState):

    def heartbeat(self):
        super().heartbeat()

        # If the player is dead, we don't need to do anything
        if self.player.in_state("dead"):
            return

        # We need to remove move points. Due to exhaustion
        if self.player.move_points > 0:
            self.player.move_points -= 5 + self.player.move_regen_rate
            if self.player.move_points < 0:
                self.player.move_points = 0

        # When you're sinking you become exhausted and start to lose health when you have no move left
        if self.player.move_points <= 0:
            self.player.hit_points -= 5 + self.player.hit_regen_rate
            if self.player.hit_points <= 0:
                self.player.add_state(Dead)
                self.player.hit_points = 0

    def deactivate(self):

        # When the flying state expires, we need to display that the user is landing
        # PlayerState.heartbeat will remove the state from the player, no need to do anything here.
        self.player.message_location("\r\nYou pull yourself free from the mud\r\n",
                                        f"\r\n{self.player.name} pulls themself free from the mud\r\n")

        self.player.add_state(Standing)

    def activate(self):

        self.player.message_location("\r\nYou sink into the mud!\r\n", f"\r\n{self.player.name} sinks into the mud!\r\n")
        self.player.remove_state("standing")

class QuickSand(Geography):

    def action_enter(self, player):

        acts = super().action_enter(player)

        # If you aren't flying, you're gonna sink in quicksand
        if not player.in_state("flying"):
            acts += [lambda: player.add_state(Sinking)]

        return acts

    def action_exit(self, player):

        if not player.in_state("flying"):
            # If you're not flying, you're stuck
            player.queue_message("You attempt to move but you're stuck!\r\n")
            raise StopAction()
        else:
            return super().action_exit(player)

if __name__ == "__main__":

    import sys
    import logging
    from mud_engine.geography import GeographyFactory

    logging.basicConfig(level=logging.DEBUG)
    mud = MUDEngine()
    mud.admins.append("ben")

    # Lets add some quicksand north of the base room (Where people spawn)
    GeographyFactory.create_geography(
        *mud.geography[0].get_direction_coordinates("north"),
        "A muddy quagmire",
        "A disgusting muddy quagmire",
        type = "quicksand"
    )
    mud.run()

    sys.exit(0)
