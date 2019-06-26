from zmz.utility.error import ParseError


class Resource(object):

    def __init__(self, data):
        try:
            self.id = data['detail']['id']
            self.title = data['detail']['cnname']
            self.seasons = list(map(lambda season: ResourceSeason(season), data['list']))
        except KeyError:
            raise ParseError


class ResourceSeason(object):

    def __init__(self, data):
        try:
            self.title = data['season_name']
            self.download_links = list(map(lambda episode: episode['files']['MP4'][0]['address'], data['episodes']))
        except KeyError:
            raise ParseError
