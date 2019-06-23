import re
from .things import ThingFetcher
from .api_meta import api_meta


class MovidaAPI(ThingFetcher):

    def __init__(self, env=None, url=None):
        if url:
            if not re.match(r'http[s]?://[\w\.:]*/api$', url):
                raise ValueError('The given url is invalid, it must begin "http[s]:// and end /api')
        elif env:
            try:
                url = api_meta['movida'][env].base_url
            except:
                raise KeyError('Invalid environment name. Expected one of ' +
                               ', '.join(api_meta['movida'].keys()))
        else:
            raise ValueError('Either url or env must be given')
        ThingFetcher.__init__(self, url=url)
        # add fetcher link properties
        for key in [
                'titles', 'title_groups', 'brands', 'platforms', 'licensors', 'events', 'outlets',
                'deals', 'assets', 'requirements', 'renditions', 'rights', 'blackouts'
                'schedulings', 'images']:
            self.add_link(key)
