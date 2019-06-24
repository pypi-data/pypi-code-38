"""Tests for common.
"""

import json

from datahunters.movies import common


class DummyMovieAPI(common.MovieAPIBase):
  def __init__(self, api_key):
    super(DummyMovieAPI, self).__init__(api_key)

  def get_movie_info(self, id):
    pass

  def map_to_internal_genre(self, genre):
    pass

  def get_person_info(self, id):
    pass


class TestMovieCommon(object):
  def test_genre_listing(self):
    api = DummyMovieAPI(None)
    genres = api.list_internal_genres()
    print genres