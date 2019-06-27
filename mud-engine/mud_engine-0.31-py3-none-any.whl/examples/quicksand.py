from mud_engine import MUDEngine
from mud_engine.geography import Geography
from mud_engine.base import StopAction
from mud_engine.player import PlayerState
from mud_engine.player import Standing
from mud_engine.player import Dead
from mud_engine.commands import Command
from mud_engine.commands import MagicSpell
from mud_engine.communication import NoColor
from mud_engine.communication import Yellow
from mud_engine.geography import GeographyFactory
from mud_engine.help import Help

@MagicSpell
class Fly(Command):

    help = """syntax: fly

Expend mana to fly into the air for a short time"""

    def do(self):
        self.player.add_state(Flying)

class Flying(PlayerState):

    # This state lasts for 10 heart beats
    duration = 10

    def deactivate(self):

        # When the flying state expires, we need to display that the user is landing
        # PlayerState.heartbeat will remove the state from the player, no need to do anything here.
        self.player.message_location("You gently float to the ground",
                                        f"{self.player.name} floats to the ground")

        if isinstance(self.player.location, QuickSand):
            self.player.add_state(Sinking)
        else:
            self.player.add_state(Standing)

    def activate(self):
        if self.player.in_state("sinking"):
            self.player.get_state("sinking").deactivate()
            self.player.remove_state("sinking")
        self.player.remove_state("standing")

        self.player.message_location(f"{Yellow}You lift into the air{NoColor}", f"{self.player.name} lifts into the air")

class Sinking(PlayerState):

    def heartbeat(self):
        super().heartbeat()

        from mud_engine.communication import Red

        # If the player is dead, we don't need to do anything
        if self.player.in_state("dead"):
            return

        # We need to remove move points. Due to exhaustion
        if self.player.move_points > 0:
            self.player.queue_message(f"{Yellow} you struggle as you sink!{NoColor}")
            self.player.move_points -= 5 + self.player.move_regen_rate
            if self.player.move_points < 0:
                self.player.move_points = 0

        # When you're sinking you become exhausted and start to lose health when you have no move left
        if self.player.move_points <= 0:
            self.player.queue_message(f"{Red} you're suffocating!{NoColor}")
            self.player.hit_points -= 5 + self.player.hit_regen_rate
            if self.player.hit_points <= 0:
                self.player.add_state(Dead)
                self.player.hit_points = 0


    def deactivate(self):

        # When the flying state expires, we need to display that the user is landing
        # PlayerState.heartbeat will remove the state from the player, no need to do anything here.
        self.player.message_location("You pull yourself free from the mud",
                                        f"{self.player.name} pulls themself free from the mud")

        self.player.add_state(Standing)

    def activate(self):

        self.player.message_location("You sink into the mud!", f"{self.player.name} sinks into the mud!")
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
            player.queue_message("You attempt to move but you're stuck!")
            raise StopAction()
        else:
            return super().action_exit(player)

from mud_engine.help import HelpInterface

orig_default_help = HelpInterface.default_help

# Let's update the default help behavior to include some QuickSand MUD details AND do the default display
def new_default_help(self):
    msg = "QuickSand MUD is now up and running!\r\n\r\n"
    return msg + orig_default_help(self)

HelpInterface.default_help = new_default_help

Help("quicksand", "Quicksand is a mud about trying to not die in quicksand!")

class QuickSandMUD(MUDEngine):

    name = "QuickSand MUD"

    def run(self):


        from mud_engine.communication import Brown
        from mud_engine.communication import NoColor

        # Lets add some quicksand north of the base room (Where people spawn)
        GeographyFactory.create_geography(
            *self.geography[0].get_direction_coordinates("north"),
            f"{Brown}A muddy quagmire{NoColor}",
            f"{Brown}A disgusting muddy quagmire{NoColor}",
            type = "quicksand",
            entrance_descriptions = {
                "default": "A filthy mud pit",
                "north": "A filthly mud pit lies to the north",
                "south": "A filthly mud pit lies to the south",
                "east": "A filthly mud pit lies to the east",
                "west": "A filthly mud pit lies to the west",
                "down": "A filthly mud pit lies below",
            }
        )

        super().run()

if __name__ == "__main__":
    import sys
    import os
    import logging

    logging.basicConfig(level=logging.DEBUG)
    host = "127.0.0.1" if not (len(sys.argv) > 2 and sys.argv[1]) else sys.argv[1]
    port = 5000 if not (len(sys.argv) > 2 and sys.argv[2]) else sys.argv[2]
    mud = MUDEngine(host, int(port))
    mud.admins.append(os.environ.get('ADMIN', 'ben'))
    mud.run()
    sys.exit(0)
