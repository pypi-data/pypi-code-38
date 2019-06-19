import pytest
from noughts_and_crosses import game, exceptions


class TestGame():

    @pytest.mark.parametrize('input_board, expected_board', [
        (None, [0] * 9),
        ([1] * 9, [1] * 9)
    ])
    def test_init(self, input_board, expected_board):
        current_game = game.NoughtsAndCrosses(input_board)
        assert current_game.winner is None
        assert current_game.board == expected_board

    def test_reset(self):
        current_game = game.NoughtsAndCrosses([1] * 9)
        assert current_game.board == [1] * 9
        current_game.reset()
        assert current_game.board == [0] * 9

    def test_place_counter(self):
        current_game = game.NoughtsAndCrosses()
        assert current_game.board == [0] * 9
        current_game.place_counter(1, 7)
        assert current_game.board == [0, 0, 0, 0, 0, 0, 0, 1, 0]
        current_game.place_counter(-1, 2)
        assert current_game.board == [0, 0, -1, 0, 0, 0, 0, 1, 0]

    def test_place_counter_raises_error(self):
        current_game = game.NoughtsAndCrosses([1, 0, 0, 0, 0, 0, 0, 0, 0])
        with pytest.raises(exceptions.PlacementException):
            current_game.place_counter(1, 0)
        with pytest.raises(exceptions.PlacementException):
            current_game.place_counter(-1, 0)

    @pytest.mark.parametrize('board, expected_winner, expected_output', [
        ([0, 0, 0, 0, 0, 0, 0, 0, 0], None, False),
        ([1, 1, -1, -1, -1, 1, 1, 1, -1], None, True),
        ([1, 0, 0, 1, 0, 0, 1, 0, 0], 1, True),
        ([0, 1, 0, 0, 1, 0, 0, 1, 0], 1, True),
        ([0, 0, 1, 0, 0, 1, 0, 0, 1], 1, True),
        ([1, 1, 1, 0, 0, 0, 0, 0, 0], 1, True),
        ([0, 0, 0, 1, 1, 1, 0, 1, 0], 1, True),
        ([0, 0, 0, 0, 0, 0, 1, 1, 1], 1, True),
        ([0, 0, 1, 0, 1, 0, 1, 0, 0], 1, True),
        ([1, 0, 0, 0, 1, 0, 0, 0, 1], 1, True),
    ])
    def test_is_over(self, board, expected_winner, expected_output):
        current_game = game.NoughtsAndCrosses(board)
        assert current_game.is_over() == expected_output
        assert current_game.winner == expected_winner

        # We check that an inversed board also leads to a correct output
        board = [counter * -1 for counter in board]
        current_game = game.NoughtsAndCrosses(board)
        assert current_game.is_over() == expected_output

