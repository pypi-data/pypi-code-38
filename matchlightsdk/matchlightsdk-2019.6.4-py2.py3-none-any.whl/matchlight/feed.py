"""An interface for downloading and filtering Matchlight feeds."""
from __future__ import absolute_import, print_function

import datetime
import io
import json
import time

import six

import matchlight.error
import matchlight.utils

if not six.PY3:
    from backports import csv
else:
    import csv


class Feed(object):
    """Represents a Matchlight Data Feed.

    Examples:
            >>> ml = matchlight.Matchlight()
            >>> feed = ml.feeds.filter()[0]
            >>> feed
            <Feed(name="CompanyEmailAddress", recent_alerts=2)>
            >>> feed.details
            {'description': None, 'name': u'CompanyEmailAddress',
            'recent_alerts_count': 2,
            'start_timestamp': '2016-06-03T00:00:00',
            'stop_timestamp': None}

    Attributes:
        description (:obj:`str`): Description of the feed.
        name (:obj:`str`): Name of the feed.
        recent_alerts_count (int): Number of recent alerts.
        start_timestamp (:class:`datetime.datetime`): Start time of the
            feed.
        stop_timestamp (:class:`datetime.datetime`): Stop time of the
            feed.

    """

    def __init__(self, name, description, recent_alerts_count,
                 start_timestamp, stop_timestamp=None):
        """Initializes a new Matchlight feed.

        Args:
            description (:obj:`str`): Description of the feed.
            name (:obj:`str`): Name of the feed.
            recent_alerts_count (int): Number of recent alerts.
            start_timestamp (:obj:`str`): ISO 8601 formatted timestamp
                of when feed collection began.
            stop_timestamp (:obj:`str`, optional): ISO 8601 formatted
                timestamp of when feed collection ended or will end. If
                not provided, the feed is assumed to never expired.

        """
        self.name = name
        self.description = description
        self.recent_alerts_count = recent_alerts_count
        self.start_timestamp = start_timestamp
        self.stop_timestamp = stop_timestamp

    @property
    def details(self):
        """:obj:`dict`: Returns the feed details as a mapping."""
        return {
            'name': self.name,
            'description': self.description,
            'recent_alerts_count': self.recent_alerts_count,
            'start_timestamp': self.start_timestamp,
            'stop_timestamp': self.stop_timestamp,
        }

    @property
    def start(self):
        """:class:`datetime.datetime`: When feed data collection began."""
        return datetime.datetime.fromtimestamp(self.start_timestamp)

    @property
    def end(self):  # noqa: D205,D400
        """:obj:`NoneType` or :class:`datetime.datetime`: If the feed
        has a ``stop_timestamp``, returns a datetime object. Otherwise,
        returns :obj:`NoneType`.

        """
        if self.stop_timestamp:
            return datetime.datetime.fromtimestamp(self.stop_timestamp)

    def __repr__(self):  # pragma: no cover
        return '<Feed(name="{name}", recent_alerts={alerts})>'.format(
            alerts=self.recent_alerts_count, name=self.name)


class FeedMethods(object):
    """Provides methods for interfacing with the feeds API."""

    def __init__(self, ml_connection):  # noqa: D205,D400
        """Initializes a feed interface with the given Matchlight
        connection.

        Args:
            ml_connection (:class:`~.Connection`): A Matchlight
                connection instance.

        """
        self.conn = ml_connection

    def all(self):
        """Returns a list of feeds associated with a Matchlight account.

        Returns:
            :obj:`list` of :class:`matchlight.Feed`: A list of feeds
                associated with an account.

        """
        r = self.conn.request('/feeds')
        return [Feed(**feed) for feed in r.json()['feeds']]

    def counts(self, feed, start_date, end_date):
        """Daily counts for a feed for a given date range.

        Args:
            feed (:class:`~.Feed`): A feed instance or feed name.
            start_date (:class:`datetime.datetime`): Start of date range.
            end_date (:class:`datetime.datetime`): End of date range.

        Returns:
            :obj:`dict`: Mapping of dates (``YYYY-MM-DD``) to alert counts.

        """
        if isinstance(feed, six.string_types):
            feed_name = feed
        else:
            feed_name = feed.name

        data = {
            'start_date': int(matchlight.utils.datetime_to_unix(start_date)),
            'end_date': int(matchlight.utils.datetime_to_unix(end_date)),
        }
        response = self.conn.request(
            '/feeds/{feed_name}'.format(feed_name=feed_name),
            data=json.dumps(data))
        return self._format_count(response.json())

    def download(self, feed, start_date, end_date, save_path=None):
        """Downloads feed data for the given date range.

        Args:
            feed (:class:`~.Feed`): A feed instance or feed name.
            start_date (:class:`datetime.datetime`): Start of date range.
            end_date (:class:`datetime.datetime`): End of date range.
            save_path (:obj:`str`): Path to output file.

        Returns:
            :obj:`list` of :obj:`dict`: All feed hits for the given range.

        """
        if isinstance(feed, six.string_types):
            feed_name = feed
        else:
            feed_name = feed.name

        data = {
            'start_date': int(matchlight.utils.datetime_to_unix(start_date)),
            'end_date': int(matchlight.utils.datetime_to_unix(end_date)),
        }
        response = self.conn.request(
            '/feed/{feed_name}/prepare'.format(feed_name=feed_name),
            data=json.dumps(data))

        if response.status_code != 200:
            raise matchlight.error.SDKError(
                'Feed failed to be generated. Please try again later.')

        data = {'feed_response_id': response.json().get('feed_response_id')}

        status = 'pending'
        while status == 'pending':
            response = self.conn.request(
                '/feed/{feed_name}/link'.format(feed_name=feed_name),
                data=json.dumps(data))
            status = response.json().get('status', None)
            time.sleep(1)
            # TODO: backoff and timeout

        if status == 'failed':
            raise matchlight.error.SDKError(
                'Feed failed to be generated. Please try again later.')
        elif status == 'ready':
            content = self.conn._request('GET', response.json().get('url'))
        else:
            raise matchlight.error.SDKError('An unknown error occurred.')

        if save_path:
            with io.open(save_path, 'wb') as f:
                f.write(content.content)
        else:
            unicode_feed = content.content.decode('utf-8-sig')
            return [
                self._format_feed(row)
                for row in csv.DictReader(unicode_feed.split('\n'))
            ]

    def _format_count(self, counts):
        return {
            datetime.datetime.fromtimestamp(int(k)).strftime('%Y-%m-%d'): v
            for k, v in counts.items()
        }

    def _format_feed(self, feed_row):
        feed_row['ts'] = matchlight.utils.terbium_timestamp_to_datetime(
            feed_row['ts'])
        return feed_row

    def __iter__(self):
        return (item for item in self.all())
