from bs4 import BeautifulSoup
import requests
import pandas as pd


class FanGraphs:
    """Pulls baseball stats for a single player from fangraphs.com

    :param player_id: FanGraph player ID
    :type player_id: str
    """
    def __init__(self, player_id):
        self.player_id = player_id
        self.raw_source = None

    def scrape(self, instance):
        """Generate a DataFrame of the stats that we pulled from fangraphs.com

        :param instance: What data instance to pull the stats from.  A data
           instance is a pair of year and team/projection system.  For example,
           an instance could be historical data from the Brewers (AAA) in 2009.
           Or it can be a projection system (e.g. Steamer).
        :type projection_sys: str
        :return: panda DataFrame of stat categories for the player.  Returns an
           empty DataFrame if projection system is not found.
        :rtype: DataFrame
        """
        self._cache_source()
        return self._source_to_df(instance)

    def instances(self):
        """Return a list of available data instances for the player

        A data instance can be historical data of a particular year/team or it
        can be from a prediction system.

        :return: Names of the available sources
        :rtype: list(str)
        """
        self._cache_source()
        avail = []
        tbody = self._find_stats_table().find_all(
            attrs={"class": "rgRow grid_projectionsin_show"})
        for row in tbody:
            avail.append(row.find_all('td')[1].a.text.strip())
        return avail

    def set_source(self, s):
        self.raw_source = s

    def save_source(self, f):
        assert(self.raw_source is not None)
        with open(f, "w") as fo:
            fo.write(self.raw_source.prettify())

    def _uri(self):
        return "https://www.fangraphs.com/statss.aspx?playerid={}".format(
            self.player_id)

    def _cache_source(self):
        if self.raw_source is None:
            self._soup()

    def _soup(self):
        uri = self._uri()
        s = requests.get(uri).content
        self.raw_source = BeautifulSoup(s, "lxml")

    def _find_stats_table(self):
        assert(self.raw_source is not None)
        return self.raw_source.find_all('table')[8]

    def _scrape_col_names(self):
        col_names = []
        thead = self._find_stats_table().find_all('thead')[0]
        for col in thead.find_all('th'):
            if col.a is not None:
                col_names.append(col.a.text.strip())
        return col_names

    def _scrape_incl_columns(self):
        incl_cols = []
        thead = self._find_stats_table().find_all('thead')[0]
        for col in thead.find_all('th'):
            if col.a is not None:
                incl_cols.append(True)
            else:
                incl_cols.append(False)
        return incl_cols

    def _scrape_stats(self, instance, incl_cols):
        data = []
        tbody = self._find_stats_table().find_all('tbody')[0]
        for row in tbody.find_all('tr'):
            cols = row.find_all('td')
            if cols[1].a is not None and cols[1].a.text.strip() == instance:
                scols = [ele.text.strip() for ele in cols]
                for col, incl in zip(scols, incl_cols):
                    if incl:
                        if col == '':
                            data.append(None)
                        else:
                            try:
                                data.append(int(col))
                            except ValueError:
                                data.append(float(col))
        return data

    def _source_to_df(self, instance):
        incl_cols = self._scrape_incl_columns()
        col_names = self._scrape_col_names()
        data = self._scrape_stats(instance, incl_cols)
        df = pd.DataFrame([data], columns=col_names)
        df.fillna(value=pd.np.nan, inplace=True)
        return df
