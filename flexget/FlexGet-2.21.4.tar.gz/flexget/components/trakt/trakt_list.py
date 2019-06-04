from __future__ import unicode_literals, division, absolute_import

import logging
import math
from builtins import *  # noqa pylint: disable=unused-import, redefined-builtin
from collections import MutableSet

from flexget import plugin
from flexget.entry import Entry
from flexget.event import event
from flexget.utils import json
from flexget.utils.cached_input import cached
from flexget.utils.requests import RequestException, TimedLimiter
from flexget.utils.tools import split_title_year

from . import db


log = logging.getLogger('trakt_list')
IMMUTABLE_LISTS = ['trending', 'popular']


def generate_show_title(item):
    show_info = item['show']
    if show_info['year']:
        return '%s (%s)' % (show_info['title'], show_info['year'])
    else:
        return show_info['title']


def generate_episode_title(item):
    show_info = item['show']
    episode_info = item['episode']
    if show_info['year']:
        return (
            '%s (%s) S%02dE%02d %s'
            % (
                show_info['title'],
                show_info['year'],
                episode_info['season'],
                episode_info['number'],
                episode_info['title'] or '',
            )
        ).strip()
    else:
        return (
            '%s S%02dE%02d %s'
            % (
                show_info['title'],
                episode_info['season'],
                episode_info['number'],
                episode_info['title'] or '',
            )
        ).strip()


field_maps = {
    'movie': {
        'title': lambda i: '%s (%s)' % (i['movie']['title'], i['movie']['year'])
        if i['movie']['year']
        else '%s' % i['movie']['title'],
        'movie_name': 'movie.title',
        'movie_year': 'movie.year',
        'trakt_movie_name': 'movie.title',
        'trakt_movie_year': 'movie.year',
        'imdb_id': 'movie.ids.imdb',
        'tmdb_id': 'movie.ids.tmdb',
        'trakt_movie_id': 'movie.ids.trakt',
        'trakt_movie_slug': 'movie.ids.slug',
    },
    'show': {
        'title': generate_show_title,
        'series_name': generate_show_title,
        'trakt_series_name': 'show.title',
        'trakt_series_year': 'show.year',
        'imdb_id': 'show.ids.imdb',
        'tvdb_id': 'show.ids.tvdb',
        'tvrage_id': 'show.ids.tvrage',
        'tmdb_id': 'show.ids.tmdb',
        'trakt_show_id': 'show.ids.trakt',
        'trakt_show_slug': 'show.ids.slug',
    },
    'episode': {
        'title': generate_episode_title,
        'series_name': generate_show_title,
        'trakt_series_name': 'show.title',
        'trakt_series_year': 'show.year',
        'series_season': 'episode.season',
        'series_episode': 'episode.number',
        'series_id': lambda i: 'S%02dE%02d' % (i['episode']['season'], i['episode']['number']),
        'imdb_id': 'show.ids.imdb',
        'tvdb_id': 'show.ids.tvdb',
        'tvrage_id': 'show.ids.tvrage',
        'trakt_episode_id': 'episode.ids.trakt',
        'trakt_show_id': 'show.ids.trakt',
        'trakt_show_slug': 'show.ids.slug',
        'trakt_ep_name': 'episode.title',
    },
}


class TraktSet(MutableSet):
    @property
    def immutable(self):
        if self.config['list'] in IMMUTABLE_LISTS:
            return '%s list is not modifiable' % self.config['list']

    schema = {
        'type': 'object',
        'properties': {
            'username': {'type': 'string'},
            'account': {'type': 'string'},
            'list': {'type': 'string'},
            'type': {
                'type': 'string',
                'enum': ['shows', 'seasons', 'episodes', 'movies', 'auto'],
                'default': 'auto',
            },
            'strip_dates': {'type': 'boolean', 'default': False},
            'language': {'type': 'string', 'minLength': 2, 'maxLength': 2}
        },
        'required': ['list'],
        'anyOf': [
            {'required': ['username']},
            {'required': ['account']},
            # The 'trending' and 'popular' lists don't require an username
            {'properties': {'list': {'enum': ['trending', 'popular']}}},
        ],
        'error_anyOf': 'At least one of `username` or `account` options are needed.',
        'additionalProperties': False,
    }

    def __init__(self, config):
        self.config = config
        if self.config.get('account') and not self.config.get('username'):
            self.config['username'] = 'me'
        self.session = db.get_session(self.config.get('account'))
        # Lists may not have modified results if modified then accessed in quick succession.
        self.session.add_domain_limiter(TimedLimiter('trakt.tv', '2 seconds'))
        self._cached_items = None

    def __iter__(self):
        return iter(self.items)

    def __len__(self):
        return len(self.items)

    def add(self, entry):
        self.submit([entry])

    def __ior__(self, entries):
        # Optimization to submit multiple entries at same time
        self.submit(entries)

    def discard(self, entry):
        self.submit([entry], remove=True)

    def __isub__(self, entries):
        # Optimization to submit multiple entries at same time
        self.submit(entries, remove=True)

    def _find_entry(self, entry):
        for item in self.items:
            if self.config['type'] in ['episodes', 'auto'] and self.episode_match(entry, item):
                return item
            if self.config['type'] in ['seasons', 'auto'] and self.season_match(entry, item):
                return item
            if self.config['type'] in ['shows', 'auto'] and self.show_match(entry, item):
                return item
            if self.config['type'] in ['movies', 'auto'] and self.movie_match(entry, item):
                return item

    def __contains__(self, entry):
        return self._find_entry(entry) is not None

    def clear(self):
        if self.items:
            for item in self.items:
                self.discard(item)
            self._cached_items = None

    def get(self, entry):
        return self._find_entry(entry)

    # -- Public interface ends here -- #

    def get_items(self):
        """Iterator over etrieved itesms from the trakt api."""
        if self.config['list'] in ['collection', 'watched', 'trending', 'popular'] and self.config['type'] == 'auto':
            raise plugin.PluginError(
                '`type` cannot be `auto` for %s list.' % self.config['list']
            )

        limit_per_page = 1000

        endpoint = self.get_list_endpoint()

        list_type = (self.config['type']).rstrip('s')

        log.verbose('Retrieving `%s` list `%s`', self.config['type'], self.config['list'])
        try:
            page = 1
            collecting_finished = False
            while not collecting_finished:
                result = self.session.get(
                    db.get_api_url(endpoint), params={'limit': limit_per_page, 'page': page}
                )
                page = int(result.headers.get('X-Pagination-Page', 1))
                number_of_pages = int(result.headers.get('X-Pagination-Page-Count', 1))
                if page == 2:
                    # If there is more than one page (more than 1000 items) warn user they may want to limit
                    log.verbose('There are a large number of items in trakt `%s` list. You may want to enable `limit`'
                                ' plugin to reduce the amount of entries in this task.', self.config['list'])

                collecting_finished = page >= number_of_pages
                page += 1

                try:
                    trakt_items = result.json()
                except ValueError:
                    log.debug(
                        'Could not decode json from response: %s', result.text
                    )
                    raise plugin.PluginError('Error getting list from trakt.')
                if not trakt_items:
                    log.warning(
                        'No data returned from trakt for %s list %s.',
                        self.config['type'],
                        self.config['list'],
                    )
                    return

                for item in trakt_items:
                    if self.config['type'] == 'auto':
                        list_type = item['type']
                    if self.config['list'] == 'popular':
                        item = {list_type: item}
                    # Collection and watched lists don't return 'type' along with the items (right now)
                    if 'type' in item and item['type'] != list_type:
                        log.debug(
                            'Skipping %s because it is not a %s',
                            item[item['type']].get('title', 'unknown'),
                            list_type,
                        )
                        continue
                    if list_type != 'episode' and not item[list_type]['title']:
                        # Skip shows/movies with no title
                        log.warning('Item in trakt list does not appear to have a title, skipping.')
                        continue
                    entry = Entry()
                    if list_type == 'episode':
                        entry['url'] = 'https://trakt.tv/shows/%s/seasons/%s/episodes/%s' % (
                            item['show']['ids']['slug'],
                            item['episode']['season'],
                            item['episode']['number'],
                        )
                    else:
                        entry['url'] = 'https://trakt.tv/%ss/%s' % (
                            list_type,
                            item[list_type]['ids'].get('slug'),
                        )

                    entry.update_using_map(field_maps[list_type], item)

                    # get movie name translation
                    language = self.config.get('language')
                    if list_type == 'movie' and language:
                        endpoint = ['movies', entry['trakt_movie_id'], 'translations', language]
                        try:
                            result = self.session.get(db.get_api_url(endpoint))
                            try:
                                translation = result.json()
                            except ValueError:
                                raise plugin.PluginError(
                                    'Error decoding movie translation from trakt: %s.' % result.text
                                )
                        except RequestException as e:
                            raise plugin.PluginError(
                                'Could not retrieve movie translation from trakt: %s' % str(e)
                            )
                        if not translation:
                            log.warning(
                                'No translation data returned from trakt for movie %s.', entry['title']
                            )
                        else:
                            log.verbose(
                                'Found `%s` translation for movie `%s`: %s',
                                language,
                                entry['movie_name'],
                                translation[0]['title'],
                            )
                            entry['title'] = translation[0]['title']
                            if entry.get('movie_year'):
                                entry['title'] += ' (' + str(entry['movie_year']) + ')'
                            entry['movie_name'] = translation[0]['title']

                    # Override the title if strip_dates is on. TODO: a better way?
                    if self.config.get('strip_dates'):
                        if list_type in ['show', 'movie']:
                            entry['title'] = item[list_type]['title']
                        elif list_type == 'episode':
                            entry[
                                'title'
                            ] = '{show[title]} S{episode[season]:02}E{episode[number]:02}'.format(
                                **item
                            )
                            if item['episode']['title']:
                                entry['title'] += ' {episode[title]}'.format(**item)
                    if entry.isvalid():
                        if self.config.get('strip_dates'):
                            # Remove year from end of name if present
                            entry['title'] = split_title_year(entry['title'])[0]
                        yield entry
                    else:
                        log.debug('Invalid entry created? %s', entry)

        except RequestException as e:
            raise plugin.PluginError('Could not retrieve list from trakt (%s)' % e)

    @property
    def items(self):
        if self._cached_items is None:
            self._cached_items = list(self.get_items())
        return self._cached_items

    def invalidate_cache(self):
        self._cached_items = None

    def get_list_endpoint(self, remove=False, submit=False):
        if (
            not submit
            and self.config['list'] == 'collection'
            and self.config['type'] == 'episodes'
        ):
            # API restriction as they don't have an endpoint for collected episodes yet
            if self.config['list'] == 'collection':
                raise plugin.PluginError('`type` cannot be `episodes` for collection list.')
            if self.config.get('account'):
                return ('sync', 'history', 'episodes')
            else:
                raise plugin.PluginError(
                    'A trakt `account` needs to be configured to get the episode history.'
                )

        if self.config['list'] in ['collection', 'watchlist', 'watched', 'ratings']:
            if self.config.get('account'):
                endpoint = (
                    'sync',
                    'history' if self.config['list'] == 'watched' else self.config['list'],
                )
                if not submit:
                    endpoint += (self.config['type'],)
            else:
                endpoint = (
                    'users',
                    self.config['username'],
                    self.config['list'],
                    self.config['type'],
                )
        elif self.config['list'] in ['trending', 'popular']:
                endpoint = (
                    self.config['type'],
                    self.config['list'],
                )
        else:
            endpoint = (
                'users',
                self.config['username'],
                'lists',
                db.make_list_slug(self.config['list']),
                'items',
            )

        if remove:
            endpoint += ('remove',)
        return endpoint

    def show_match(self, entry1, entry2):
        return any(
            entry1.get(ident) is not None and entry1[ident] == entry2.get(ident)
            for ident in [
                'series_name',
                'trakt_show_id',
                'tmdb_id',
                'tvdb_id',
                'imdb_id',
                'tvrage_id',
            ]
        )

    def season_match(self, entry1, entry2):
        return (
            self.show_match(entry1, entry2)
            and entry1.get('series_season') is not None
            and entry1['series_season'] == entry2.get('series_season')
        )

    def episode_match(self, entry1, entry2):
        return (
            self.season_match(entry1, entry2)
            and entry1.get('series_episode') is not None
            and entry1['series_episode'] == entry2.get('series_episode')
        )

    def movie_match(self, entry1, entry2):
        if any(
            entry1.get(id) is not None and entry1[id] == entry2[id]
            for id in ['trakt_movie_id', 'imdb_id', 'tmdb_id']
        ):
            return True
        if entry1.get('movie_name') and (
            (entry1.get('movie_name'), entry1.get('movie_year'))
            == (entry2.get('movie_name'), entry2.get('movie_year'))
        ):
            return True
        return False

    def submit(self, entries, remove=False):
        """Submits movies or episodes to trakt api."""
        found = {}
        for entry in entries:
            if self.config['type'] in ['auto', 'shows', 'seasons', 'episodes'] and entry.get(
                'series_name'
            ):
                show_name, show_year = split_title_year(entry['series_name'])
                show = {'title': show_name, 'ids': db.get_entry_ids(entry)}
                if show_year:
                    show['year'] = show_year
                if (
                    self.config['type'] in ['auto', 'seasons', 'episodes']
                    and entry.get('series_season') is not None
                ):
                    season = {'number': entry['series_season']}
                    if (
                        self.config['type'] in ['auto', 'episodes']
                        and entry.get('series_episode') is not None
                    ):
                        season['episodes'] = [{'number': entry['series_episode']}]
                    show['seasons'] = [season]
                if self.config['type'] in ['seasons', 'episodes'] and 'seasons' not in show:
                    log.debug('Not submitting `%s`, no season found.', entry['title'])
                    continue
                if self.config['type'] == 'episodes' and 'episodes' not in show['seasons'][0]:
                    log.debug('Not submitting `%s`, no episode number found.', entry['title'])
                    continue
                found.setdefault('shows', []).append(show)
            elif self.config['type'] in ['auto', 'movies']:
                movie = {'ids': db.get_entry_ids(entry)}
                if not movie['ids']:
                    if entry.get('movie_name') is not None:
                        movie['title'] = entry.get('movie_name') or entry.get('imdb_name')
                        movie['year'] = entry.get('movie_year') or entry.get('imdb_year')
                    else:
                        log.debug(
                            'Not submitting `%s`, no movie name or id found.', entry['title']
                        )
                        continue
                found.setdefault('movies', []).append(movie)

        if not (found.get('shows') or found.get('movies')):
            log.debug('Nothing to submit to trakt.')
            return

        url = db.get_api_url(self.get_list_endpoint(remove, submit=True))

        log.debug('Submitting data to trakt.tv (%s): %s', url, found)
        try:
            result = self.session.post(url, data=json.dumps(found), raise_status=False)
        except RequestException as e:
            log.error('Error submitting data to trakt.tv: %s', e)
            return
        if 200 <= result.status_code < 300:
            action = 'deleted' if remove else 'added'
            res = result.json()
            # Default to 0 for all categories, even if trakt response didn't include them
            for cat in ('movies', 'shows', 'episodes', 'seasons'):
                res[action].setdefault(cat, 0)
            log.info(
                'Successfully {0} to/from list {1}: {movies} movie(s), {shows} show(s), {episodes} episode(s), '
                '{seasons} season(s).'.format(action, self.config['list'], **res[action])
            )
            for media_type, request in res['not_found'].items():
                if request:
                    log.debug('not found %s: %s', media_type, request)
            # TODO: Improve messages about existing and unknown results
            # Mark the results expired if we added or removed anything
            if sum(res[action].values()):
                self.invalidate_cache()
        elif result.status_code == 404:
            log.error('List does not appear to exist on trakt: %s', self.config['list'])
        elif result.status_code == 401:
            log.error('Authentication error: have you authorized Flexget on Trakt.tv?')
            log.debug('trakt response: %s', result.text)
        else:
            log.error('Unknown error submitting data to trakt.tv: %s', result.text)

    @property
    def online(self):
        """ Set the online status of the plugin, online plugin should be treated differently in certain situations,
        like test mode"""
        return True


class TraktList(object):
    schema = TraktSet.schema

    def get_list(self, config):
        return TraktSet(config)

    # TODO: we should somehow invalidate this cache when the list is modified
    @cached('trakt_list', persist='2 hours')
    def on_task_input(self, task, config):
        # We use the generator here rather than the cached list in case limit plugin is used.
        return TraktSet(config).get_items()


@event('plugin.register')
def register_plugin():
    plugin.register(TraktList, 'trakt_list', api_ver=2, interfaces=['task', 'list'])
