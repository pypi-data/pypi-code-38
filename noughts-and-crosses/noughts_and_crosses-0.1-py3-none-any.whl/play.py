from noughts_and_crosses import game, player, recorder


def play_episodes(number_of_episodes, number_of_games):
    """
    Play multiple games of noughts and crosses.

    Play a number of games of noughts and crosses, each of which are separated
    into different episodes. If any of the players in the game are based on
    machine learning, their parameters will be updated at the end of each
    episode.

    Parameters
    ----------
    number_of_episodes : int
        Number of episodes to play.
    number_of_games : int
        Number of games to play per episode.
    """

    current_game = game.NoughtsAndCrosses()

    players = {
        1: player.Player.initialise_ml_player(1),
        -1: player.Player.initialise_random_player(-1)
    }

    for episode_number in range(number_of_episodes):

        print('Playing episode {}'.format(episode_number + 1))

        episode_recorder = recorder.EpisodeRecorder()

        for __ in range(number_of_games):
            game_recorder = recorder.GameRecorder()
            episode_recorder.snapshot_game(current_game.play(players, game_recorder, debug=False))

        episode_recorder.finish_recording()
        episode_recorder.print_metrics()

        for current_player in players.values():
            if not current_player.position_strategy.CAN_BE_UPDATED:
                continue
            current_player.update(episode_recorder)
            current_player.position_strategy.exploration_probability *= 0.8

        print()
