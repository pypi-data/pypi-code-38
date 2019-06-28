from sports_client_nba import SportsClientNBA


class SportsClientFactory():
    __instance_client_nba = None

    def __get_intance_client_nba(self, sd_subs_key_nba=None):
        if self.__instance_client_nba is None:
            self.__instance_client_nba = SportsClientNBA(sd_subs_key_nba)
        return self.__instance_client_nba

    def get_api_client(self, league, sd_subs_key_nba=None):
        if league == 'nba':
            return self.__get_intance_client_nba(sd_subs_key_nba)
