from noughts_and_crosses.exceptions import PlacementException


class NoughtsAndCrosses(object):

    EMPTY_POSITION_COUNTER = 0

    COUNTER_REPRESENTATION = {
        -1: 'o',
        0: ' ',
        1: 'x'
    }

    BOARD_TEMPLATE = (
        ' {} | {} | {} '
        '\n-----------'
        '\n {} | {} | {}'
        '\n-----------'
        '\n {} | {} | {}'
    )

    WINNING_POSITIONS = [
        (0, 1, 2), (3, 4, 5), (6, 7, 8),  # Row-based winning conditions
        (0, 3, 6), (1, 4, 7), (2, 5, 8),  # Column-based winning conditions
        (2, 4, 6), (0, 4, 8)  # Diagonal-based winning conditions
    ]

    def __init__(self, board=None):
        """
        Create the noughts and crosses board.

        Parameters
        ----------
        board : list of int
            Nine-element list representing the board of a noughts and crosses
            game. Permitted characters are -1, 0 and 1. By default the board
            will be initialised to be empty.

        Examples
        --------
        >>> game = NoughtsAndCrosses([0, 0, 0, 0, 0, 0, 0, 0, 0])
        >>> game.print_board()
           |   |
        -----------
           |   |
        -----------
           |   |
        >>> game = NoughtsAndCrosses([1, -1, 1, -1, 1, -1, 1, -1, 1])
        >>> game.print_board()
         x | o | x
        -----------
         o | x | o
        -----------
         x | o | x
        """
        self.winner = None
        self.board = board or [self.__class__.EMPTY_POSITION_COUNTER] * 9

    def reset(self):
        """Reset to an empty board."""
        self.__init__()

    def place_counter(self, counter, position):
        """
        Update the board in-place with a counter at the given position.

        Parameters
        ----------
        counter : int
            Either 1 or -1. The value 1 corresponds to a cross and the value -1
            to a nought.
        position : int
            Value in the range [0, 8].

        Raises
        ------
        PlacementException
            If the function attempts to place a counter on a position already
            occupied by another counter.
        """
        if self.board[position] != self.EMPTY_POSITION_COUNTER:
            raise PlacementException

        self.board[position] = counter

    def print_board(self):
        """Print a human-readable version of the current state of the board."""
        print(
            self.BOARD_TEMPLATE.format(
                *[self.COUNTER_REPRESENTATION[counter] for counter in self.board])
        )

    def print_winner(self):
        """Print a sentence about the winner of the current game."""
        if self.winner is None:
            print('There was no winner')
        else:
            print('The winner was {}!'.format(
                self.__class__.COUNTER_REPRESENTATION[self.winner]))

    def is_over(self):
        """
        Determine whether the current game is over.

        A game of noughts and crosses is over if either (1) there are three
        noughts counters placed in a row; (2) there are three crosses counters
        placed in a row; (3) there are no remaining empty spaces on the board.

        Returns
        -------
        bool
        """
        for el1, el2, el3 in self.WINNING_POSITIONS:
            if self.board[el1] == self.board[el2] == self.board[el3]:
                if self.board[el1] == 0:
                    continue

                self.winner = self.board[el1]
                return True

        if self.__class__.EMPTY_POSITION_COUNTER not in self.board:
            return True

        return False

    def play(self, players, game_recorder, debug):
        """
        Play a game of noughts and crosses.

        Parameters
        ----------
        players : dict of (int, noughts_and_crosses.player.Player)
            Dictionary mapping an integer representation of a player counter to
            an instantiated Player object. The key 1 represents a player of
            crosses, the key -1 represents a player of noughts.
        game_recorder : noughts_and_crosses.game_recorder.GameRecorder
        debug : bool
            Should the function print out intermediate steps in the playing of
            the game? This option is not recommended if a large number of games
            will be played.

        Returns
        -------
        noughts_and_crosses.game_recorder.GameRecorder
        """
        self.reset()

        current_player_idx = 1

        if debug:
            self.print_board()

        while not self.is_over():

            current_player = players[current_player_idx]
            position = current_player.choose_position(self.board)

            try:
                self.place_counter(current_player.counter, position)
            except PlacementException:
                game_recorder.record_placement_error(
                    current_player.counter, self.board, position)
                continue

            game_recorder.record_correct_placement(current_player.counter, self.board, position)

            if debug:
                self.print_board()

            current_player_idx *= -1

        game_recorder.record_winner(self.winner)
        if debug:
            self.print_winner()

        return game_recorder
