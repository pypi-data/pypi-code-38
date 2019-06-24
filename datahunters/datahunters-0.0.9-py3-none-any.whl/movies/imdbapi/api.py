"""Scraper/api for imdb.
"""

from imdb import IMDb

from datahunters.movies import common


class IMDBAPI(common.MovieAPIBase):
  """Class for IMDB.
  """
  engine = NotImplemented

  def __init__(self, api_key=None):
    super(IMDBAPI, self).__init__(api_key)
    self.engine = IMDb()
    print("init imdb api")

  def get_movie_info(self, id):
    data_mat = self.engine.get_movie(id)
    # print data_mat["full-size cover url"]
    # print data_mat["genres"]
    # print data_mat["cast"]

  def get_person_info(self, name):
    pass

  def map_to_internal_genre(self, genre):
    pass


if __name__ == "__main__":
  api = IMDBAPI()
  api.get_movie_info("3170832")
