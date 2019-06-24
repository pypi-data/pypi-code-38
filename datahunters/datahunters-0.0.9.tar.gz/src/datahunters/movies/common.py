"""Common scraper class for movie data.
"""

import abc
import json
import os


class MovieObject(object):
  """Base class for a movie object.
  """
  # meta
  title = ""
  # description.
  desc = ""
  year = ""
  release_date = ""
  # list of internal genre names.
  genres = []
  # directors.
  directors = []
  # casts: [(last name, rest of the name)]
  casts = []
  # images.
  cover_img_url = ""
  backdrop_url = ""
  # sources: information from different sources.
  # [{name, rating, reviews}]
  source_data = []
  # trailer link.
  trailers = []
  # imdb id.
  imdb_id = ""
  # financials.
  budget = 0
  revenue = 0
  first_week_box = 0


class MovieAPIBase(object):
  """Base class for movie related api.
  """
  __metaclass__ = abc.ABCMeta
  internal_genres = []

  @abc.abstractmethod
  def __init__(self, api_key):
    """Set up class with api key. None for scraper.
    """
    # load genres.
    data_dir = os.path.join(os.path.dirname(__file__), "data")
    # with open(os.path.join(data_dir, "genre.json"), "r") as f:
    #   data = json.load(f)
    #   self.internal_genres = data["data"]
    print("init base movie api.")

  @abc.abstractmethod
  def get_movie_info(self, id):
    """Fetch movie information.

    Args:
      id: identifier for the movie, e.g. id, title.
    
    Returns:
      a movie object.
    """
    pass

  @abc.abstractclassmethod
  def search_movies(self, keywords):
    """Search movies with keywords.

    Returns:
      list of movie object.
    """
    pass

  @abc.abstractmethod
  def get_person_info(self, id):
    """Fetch info about a person.
    """
    pass

  def list_internal_genres(self):
    """A universally defined genres.
    """
    return self.internal_genres

  @abc.abstractmethod
  def map_to_internal_genre(self, genre):
    """Map a genre from a source to our internally defined one.

    Args:
      genre: name for the genre.

    Returns:
      internal genre name.
    """
    pass
