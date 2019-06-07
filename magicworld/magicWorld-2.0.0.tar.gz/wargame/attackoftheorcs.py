from wargame.knight import Knight
from wargame.orcrider import OrcRider
from wargame.hut import Hut
import random
from wargame.gameunit import print_bold

class AttackOfTheOrcs:
    def __init__(self):
        self.huts = []
        self.player = None


    def get_occupants(self):
        """Return a list of occupant types for all huts.

        .. todo::

                Prone to bugs if self.huts is not populated.
                Chapter 2 talks about catching exceptions
        """
        return [x.get_occupant_type() for x in self.huts]

    @staticmethod
    def show_game_mission():
        """Print the game mission in the console"""
        print_bold("Mission:")
        print("  1. Fight with the enemy.")
        print("  2. Bring all the huts in the village under your control")
        print("---------------------------------------------------------\n")


    def _process_user_choice(self):
        """Process the user input for choice of hut to enter"""
        verifying_choice = True
        idx = 0
        print("Current occupants: %s" % self.get_occupants())
        while verifying_choice:
            user_choice = input("Choose a hut number to enter (1-5): ")
            try:
                idx = int(user_choice)
            except ValueError as e:
                print("You look at the five huts in front of you, you're in silence, which is %s " % e.args)
                continue
            try:
                if self.huts[idx - 1].is_acquired:
                    print("You have already acquired this hut. Try again."
                          "<INFO: You can NOT get healed in already acquired hut.>")
                else:
                    verifying_choice = False
            except IndexError:
                print("You count the number of house and find there is only 5 houses, you decide to choose again")
                continue

        return idx


    def _occupy_huts(self):
        for i in range(5):
            choice_lst = ['enemy', 'friend', None]
            computer_choice = random.choice(choice_lst)
            if computer_choice == 'enemy':
                name = 'enemy-' + str(i + 1)
                self.huts.append(Hut(i + 1, OrcRider(name)))
            elif computer_choice == 'friend':
                name = 'knight-' + str(i + 1)
                self.huts.append(Hut(i + 1, Knight(name)))
            else:
                self.huts.append(Hut(i + 1, computer_choice))

    def play(self):
        """Workhorse method to play the game.

            Controls the high level logic to play the game. This is called from
            the main program to begin the game execution.
        """
        self.player = Knight()
        self._occupy_huts()
        acquired_hut_counter = 0

        self.show_game_mission()
        self.player.show_health(bold=True)

        while acquired_hut_counter < 5:
            idx = self._process_user_choice()
            self.player.acquire_hut(self.huts[idx - 1])

            if self.player.health_meter <= 0:
                print_bold("YOU LOSE  :(  Better luck next time")
                break

            if self.huts[idx - 1].is_acquired:
                acquired_hut_counter += 1

        if acquired_hut_counter == 5:
            print_bold("Congratulations! YOU WIN!!!")


if __name__=='__main__':
    game = AttackOfTheOrcs()
    game.play()
