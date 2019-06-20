from enum import Enum
from typing import List

from rambler_kassa.models.movie import Movie
from rambler_kassa.models.schedule import Schedule
from rambler_kassa.request_manager import Request
from rambler_kassa.utils import *


class ScheduleType(Enum):
    Movie = 1


class RamblerKassa(object):

    def __init__(self, api_key: str, city_id: int, widget_id: int = 0):
        self.api_key = api_key
        self.city_id = city_id
        self.widget_id = widget_id

    def get_movies(self, **kwargs) -> List[Movie]:
        """Return of current films from the cinema."""
        data = Request \
            .get(get_movies_link(api_key=self.api_key,
                                 CityID=self.city_id, **kwargs))

        movies = []
        for item in data['List']:
            schedule = Movie(**item)
            movies.append(schedule)
        return movies

    def get_movie(self, movie_id):
        """Get detail info of movie by id"""
        data = Request \
            .get(get_movie_link(api_key=self.api_key, ObjectID=movie_id))
        return Movie(**data)

    def get_movie_schedules(self, movie_id: int, **kwargs):
        """Return schedules of movie by id."""
        return self._get_schedules(
            ScheduleType.Movie,
            ObjectID=movie_id,
            **kwargs,
        )

    def get_movies_schedules(self, **kwargs):
        """Return schedules of movies."""
        return self._get_schedules(
            ScheduleType.Movie,
            **kwargs,
        )

    def get_url_buy_ticket(self, session_id):
        if not self.widget_id:
            print("You do not set widget_id")
        return get_widget_hallplan_url(session_id=session_id,
                                       city_id=self.city_id,
                                       widget_id=self.widget_id)

    def _get_schedules(self, schedule_type: ScheduleType, **kwargs):
        url = None
        kwargs.update({
            'CityID': self.city_id,
        })
        if schedule_type.Movie:
            url = get_movie_schedules_link(api_key=self.api_key, **kwargs)

        data = Request.get(url)

        schedules = []
        for item in data['List']:
            schedule = Schedule(**item)
            schedules.append(schedule)

        return schedules
