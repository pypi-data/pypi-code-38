from generic_sports_dataio_client import GenericSportsDataIOClient
from generic_sports_dataio_client import get_env


class SportsClientNBA (GenericSportsDataIOClient):
    def __init__(self, sd_subs_key_nba=None, custom_http_client=None):
        super().__init__(custom_http_client)
        if sd_subs_key_nba is None:
            self.secret_key = get_env('SD_SUBS_KEY_NBA')
        else:
            self.secret_key = sd_subs_key_nba

    def get_league(self):
        return 'nba'

    def __is_game_finished(self, game):
        try:
            return (game['IsClosed'] & (game['Status'] == 'Final'))
        except Exception:
            return False

    def __filter_not_finished_games(self, dataset):
        filtered_dataset = filter(lambda g: self.__is_game_finished(g),
                                  dataset)
        return list(filtered_dataset)

    def get_consolidated_games(self):
        result = super().get_games()
        return result
