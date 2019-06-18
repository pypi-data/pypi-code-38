from datetime import datetime, timedelta
from os import environ
# from pprint import pprint
from default_http_client import DefaultHttpClient
from abc import abstractmethod
import sys
import json
import threading


def get_env(var_name, default_value=None):
    return environ.get(var_name) if environ.get(var_name) else default_value


class GenericSportsDataIOClient:
    def __init__(self, custom_http_client=None):
        self.base_url = get_env('SPORT_RADAR_BASE_URL',
                                'https://api.sportsdata.io/v3')
        self.secret_key = None
        self.auth_header = 'Ocp-Apim-Subscription-Key'
        self.http_client = custom_http_client if custom_http_client \
            else DefaultHttpClient()
        self.max_threads = 15
        self.thread_args = {}
        self.threads = []

    def __get_auth_headers(self, headers={}):
        altered_headers = headers.copy()
        altered_headers[self.auth_header] = self.secret_key
        return altered_headers

    def __build_func_url(self, func_url, **place_holders):
        try:
            return self.base_url + func_url % place_holders
        except Exception as e:
            sys.stderr.write(repr(e) + "\n")
            return self.base_url

    def __do_api_call(self, full_url, headers={}):
        auth_headers = self.__get_auth_headers(headers)
        response = self.http_client.get(full_url, auth_headers)
        return json.loads(response) if response else None

    def __date_range(self, start_date, end_date):
        for n in range(int((end_date - start_date).days)+1):
            yield start_date + timedelta(n)

    @abstractmethod
    def get_league(self):
        return None

    def getTeams(self):
        league_name = self.get_league()
        current_secret_key = self.secret_key
        self.secret_key = get_env('SD_FREE_SUBS_KEY')
        full_url = \
            self.__build_func_url('/%(league)s/scores/json/'
                                  'teams',
                                  league=league_name)
        response = self.__do_api_call(full_url)
        self.secret_key = current_secret_key
        return response

    def get_season(self):
        current_year = str(datetime.now().year)
        return current_year

    def get_games(self):
        league_name = self.get_league()
        current_secret_key = self.secret_key
        self.secret_key = get_env('SD_FREE_SUBS_KEY')
        season = self.get_season()
        full_url = \
            self.__build_func_url('/%(league)s/scores/json/'
                                  'Games/%(season)s',
                                  league=league_name, season=season)
        response = self.__do_api_call(full_url)
        self.secret_key = current_secret_key
        return response

    def get_pre_game_odds_by_date(self, date=None):
        now = date if date else datetime.now().date()
        now_iso = now.isoformat()
        league_name = self.get_league()
        full_url = \
            self.__build_func_url('/%(league)s/odds/json/'
                                  'GameOddsByDate/%(date)s',
                                  date=now_iso, league=league_name)
        response = self.__do_api_call(full_url)
        return response

    def __get_pre_game_odds_by_dates(self, dates, response_hash, th_id):
        odds_for_dates = []
        for now in dates:
            odds = self.get_pre_game_odds_by_date(now)
            odds_for_dates.append(odds)
        response_hash[th_id] = odds_for_dates

    def __spread_dates(self, start_date, end_date):
        self.thread_args = {}
        index = 0
        for d in self.__date_range(start_date, end_date):
            try:
                self.thread_args[index].append(d.date())
            except Exception:
                self.thread_args[index] = []
                self.thread_args[index].append(d.date())
                index = (index + 1) % self.max_threads

    def __create_threads(self, response_hash):
        self.threads = []
        index = 0
        for (k, dates) in self.thread_args.items():
            self.threads.append(
                threading.Thread(
                    target=self.__get_pre_game_odds_by_dates,
                    args=(dates, response_hash, index)))
            index = index + 1

    # start_date and end_date are strings %Y-%m-%d (isodate)
    def get_pre_game_odds(self, start_date=None, end_date=None):
        pre_games = []
        threads_data = {}

        sdate = datetime.strptime(start_date, '%Y-%m-%d') if start_date else \
            datetime.now()
        edate = datetime.strptime(end_date, '%Y-%m-%d') if end_date else \
            sdate + timedelta(days=15)

        self.__spread_dates(sdate, edate)
        self.__create_threads(threads_data)

        for th in self.threads:
            th.start()

        for th in self.threads:
            th.join()

        for (i, thread_odds) in threads_data.items():
            for th_jdds in thread_odds:
                if th_jdds:
                    for odds in th_jdds:
                        pre_games.append(odds)
        return pre_games
