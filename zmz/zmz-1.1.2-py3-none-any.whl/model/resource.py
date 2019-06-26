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
            self.download_links = ResourceSeason.parse_download_links(data)
        except KeyError:
            raise ParseError

    @staticmethod
    def parse_download_links(data):
        if 'episodes' in data:
            download_links = []
            for episode in data['episodes']:
                download_links.append(episode['files'][1][0])
        else:
            return []
