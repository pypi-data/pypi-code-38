from bs4 import BeautifulSoup
import requests
import pandas as pd
import pickle
import importlib.resources as pkg_resources


class Scraper:
    """Pulls baseball stats for a single player from fangraphs.com

    :param player_id: FanGraph ID of the player to lookup.  This optional for
        class init.  It can be set with the set_player_id API.
    :type player_id: str
    """
    def __init__(self, player_id=None):
        self.player_id = player_id  # Current player_id we are working on
        self.instance = None
        self.raw_source = {}   # A map of the raw source.  Key is the player_id
        self.df_source = {}    # A map of the DataFrames.  Key is the player_id
        self.cache_only = False  # Toggle to avoid calling out to scrape.

    def scrape(self, instance):
        """Generate a DataFrame of the stats that we pulled from fangraphs.com

        :param instance: What data instance to pull the stats from.  A data
           instance is a pair of year and team/projection system.  For example,
           an instance could be historical data from the Brewers (AAA) in 2009.
           Or it can be a projection system (e.g. Steamer).  Use the
           instances() API to get a list of data instances available.
        :type instance: str
        :return: panda DataFrame of stat categories for the player.  Returns an
           empty DataFrame if projection system is not found.
        :rtype: DataFrame
        """
        self._assert_playerid()
        self.instance = instance
        self._cache_source()
        return self.df_source[self.player_id]

    def instances(self):
        """Return a list of available data instances for the player

        A data instance can be historical data of a particular year/team or it
        can be from a prediction system.

        :return: Names of the available sources
        :rtype: list(str)
        """
        self._assert_playerid()
        self._cache_source()
        avail = set([])
        for table in self._find_stats_table():
            for row in table.find_all(attrs={"class":
                                             "rgRow grid_projectionsin_show"}):
                avail.add(row.find_all('td')[1].a.text.strip())
        return list(avail)

    def set_player_id(self, player_id):
        """Set the player_id for the next scrape

        :param player_id: FanGraph ID of the player to scrape
        :type player_id: str
        """
        self.player_id = str(player_id)

    def set_source(self, s):
        self._assert_playerid()
        self.raw_source[self.player_id] = s

    def save_source(self, f):
        assert(self.player_id in self.raw_source)
        with open(f, "w") as fo:
            fo.write(self.raw_source[self.player_id].prettify())

    def save_universe(self, f):
        with open(f, "wb") as fo:
            pickle.dump(self.df_source, fo)

    def load_universe(self, f):
        with open(f, "rb") as fo:
            self.df_source = pickle.load(fo)

    def load_fake_cache(self):
        with pkg_resources.open_binary('baseball_scraper',
                                       'sample.fangraphs.universe.pkl') as fo:
            self.df_source = pickle.load(fo)
        self.set_cache_only(True)

    def set_cache_only(self, v):
        self.cache_only = v

    def _assert_playerid(self):
        if self.player_id is None:
            raise RuntimeError("The player ID be set prior to calling this " +
                               "API.  Use set_player_id().")

    def _uri(self):
        return "https://www.fangraphs.com/statss.aspx?playerid={}".format(
            self.player_id)

    def _cache_source(self):
        if self.player_id not in self.df_source:
            if self.player_id not in self.raw_source:
                if self.cache_only:
                    raise RuntimeError("Cache-only request and player not "
                                       "available in the cache")
                self._soup()
            self._raw_source_to_df()

    def _soup(self):
        assert(self.player_id is not None)
        uri = self._uri()
        s = requests.get(uri).content
        self.raw_source[self.player_id] = BeautifulSoup(s, "lxml")

    def _find_stats_table(self):
        def _is_stats_table(tag):
            """Filter function used with BeautifulSoup to find stats"""
            table_ids = ["SeasonStats1_dgSeason1_ctl00",
                         "SeasonStats1_dgSeason2_ctl00"]
            return tag.name == "table" and tag.has_attr("id") and \
                tag["id"] in table_ids

        assert(self.player_id in self.raw_source)
        for table in self.raw_source[self.player_id].find_all(_is_stats_table):
            yield table

    def _td_applies_to_instance(self, cols):
        return len(cols) > 1 and cols[1].a is not None and \
            cols[1].a.text.strip() == self.instance

    def _scrape_col_names(self):
        col_names = []
        incl_cols = []
        for table in self._find_stats_table():
            table_incl_cols = []
            tbody = table.find_all('tbody')[0]
            table_applies = False
            for row in tbody.find_all('tr'):
                if self._td_applies_to_instance(row.find_all('td')):
                    table_applies = True
                    break

            if table_applies:
                thead = table.find_all('thead')[0]
                for col in thead.find_all('th'):
                    if col.a is not None:
                        name = col.a.text.strip()
                        if name not in col_names:
                            col_names.append(name)
                            table_incl_cols.append(True)
                        else:
                            table_incl_cols.append(False)
                    else:
                        table_incl_cols.append(False)
                incl_cols.append(table_incl_cols)
        return (col_names, incl_cols)

    def _scrape_stats(self, incl_cols):
        data = []
        for i, table in enumerate(self._find_stats_table()):
            tbody = table.find_all('tbody')[0]
            for row in tbody.find_all('tr'):
                cols = row.find_all('td')
                if self._td_applies_to_instance(cols):
                    scols = [ele.text.strip() for ele in cols]
                    for col, incl in zip(scols, incl_cols[i]):
                        if incl:
                            if col == '':
                                data.append(None)
                            elif col.endswith("%"):
                                data.append(float(col[:-2])/100)
                            else:
                                try:
                                    data.append(int(col))
                                except ValueError:
                                    data.append(float(col))
        return data

    def _raw_source_to_df(self):
        (col_names, incl_cols) = self._scrape_col_names()
        data = self._scrape_stats(incl_cols)
        df = pd.DataFrame([data], columns=col_names)
        df.fillna(value=pd.np.nan, inplace=True)
        self.df_source[self.player_id] = df
