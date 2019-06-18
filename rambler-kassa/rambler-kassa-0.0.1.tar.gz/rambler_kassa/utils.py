import urllib.parse as urlparse
HOST = 'http://api.kassa.rambler.ru/v2/'

MOVIE_SCHEDULES_LINK = HOST + '{api_key}/json/movie/Schedule'
MOVIE_LIST_LINK = HOST + '{api_key}/json/Movie/list'
MOVIE_LINK = HOST + '{api_key}/json/Movie/Object'


def get_movie_schedules_link(**kwargs):
    api_key = kwargs.pop('api_key')
    return _set_params_to_url(MOVIE_SCHEDULES_LINK.format(api_key=api_key),
                              kwargs)


def get_movies_link(**kwargs):
    api_key = kwargs.pop('api_key')
    return _set_params_to_url(MOVIE_LIST_LINK.format(api_key=api_key), kwargs)


def get_movie_link(**kwargs):
    api_key = kwargs.pop('api_key')
    return _set_params_to_url(MOVIE_LINK.format(api_key=api_key), kwargs)


def _set_params_to_url(url, params):
    url_parts = list(urlparse.urlparse(url))
    query = dict(urlparse.parse_qsl(url_parts[4]))
    query.update(params)
    url_parts[4] = urlparse.urlencode(query)
    return urlparse.urlunparse(url_parts)
