"""An interface for searching the Matchlight fingerprints database."""
from __future__ import absolute_import

import datetime
import json

import six

import matchlight.error
import pylibfp


class SearchMethods(object):
    """Provides methods for interfacing with the search API."""

    def __init__(self, ml_connection):  # noqa: D205,D400
        """Initializes a search interface with the given Matchlight
        connection.

        Args:
            ml_connection (:class:`~.Connection`): A Matchlight
                connection instance.

        """
        self.conn = ml_connection

    def search(self, query=None, email=None, ssn=None, phone=None,
               fingerprints=None):
        """Performs a Matchlight search.

        Provides a retrospective search capability. User can only
        perform one search type at time. Search type is specified using
        keyword arguments.

        Example:

            Search for text::

                >>> ml.search(query="magic madness heaven sin")

            Search for an email address::

                >>> ml.search(email="familybird@terbiumlabs.com")

            Search for a social security number::

                >>> ml.search(ssn="000-00-0000")

            Search for a phone number::

                >>> ml.search(phone="804-222-1111")

        Args:
            query (:obj:`str`, optional): A text query.
            email (:obj:`str`, optional): A valid email address.
            ssn (:obj:`str`, optional): A social security number.
            phone (:obj:`str`, optional): A phone number.
            fingerprints (:obj:`list` of :obj:`str`, optional): A sequence of
            Matchlight fingerprints, these will be searched as if one query.


        Returns:
            :obj:`list` of :obj:`dict`: Each search result returns a
                score, url, ts.

        """
        # only search for one thing at a time.
        if sum([1 for k in [query, fingerprints, email, ssn, phone]
                if k is not None]) != 1:
            raise matchlight.error.SDKError(
                'Input Error: Must specify exactly one search type per call.')

        if email:
            fingerprints = pylibfp.fingerprints_pii_email_address(str(email))
        elif phone:
            fingerprints = pylibfp.fingerprints_pii_phone_number(str(phone))
        elif ssn:
            fingerprints = pylibfp.fingerprints_pii_ssn(str(ssn))
        elif query:
            result_json = pylibfp.fingerprint(
                query, flags=pylibfp.OPTIONS_TILED)
            result = json.loads(result_json)
            fingerprints = result['data']['fingerprints']

        # We have to convert possible lists of lists to a flat list of strings
        def flatten_iter(x):
            if not isinstance(x, list):
                yield(x)
            else:
                for i in x:
                    # same as yield from flatten_iter(i)
                    for j in flatten_iter(i):
                        yield j

        data = {'fingerprints': list(flatten_iter(fingerprints))}
        response = self.conn.request(
            '/detailed_search',
            data=json.dumps(data),
            endpoint=self.conn.search_endpoint,
        )
        try:
            results = response.json()['results']
        except KeyError:
            raise matchlight.error.SDKError('Failed to get search results')
        for result in results:
            for url in result['urls']:
                yield {
                    # PII Alerts are always 800, Search results on PII filds
                    # should be as well.
                    'score': 800 if any(
                        [email, ssn, phone]
                    ) else result['score'],
                    'ts': datetime.datetime.fromtimestamp(float(url[0])),
                    'url': url[1]
                }

    def pii_search(self, email=None, limit=50):
        """Performs a Matchlight search specifically for PII.

        Provides a retrospective search capability designed specifically for
        finding compromised PII data.
        Search results are sorted & show which fields matched on each hit.
        Only exact matches are returned.

        Example:

            >>> ml.pii_search(email="familybird@terbiumlabs.com")

        Args:
            email (:obj:`str`, required): A valid email address.
            limit (:obj:`int`, optional): The number of Alerts to return,
                defaults to 50.

        Returns:
            :obj:`list` of :obj:`dict`: Each search result returns a
                source, ts, fields

        """
        if not any(email):
            raise matchlight.error.SDKError(
                'Input Error: At least one field is required.'
            )

        request_data = {}

        if email:
            request_data['email_fingerprints'] = (
                pylibfp.fingerprints_pii_email_address(str(email))
            )

        if limit:
            request_data['limit'] = limit

        response = self.conn.request(
            '/pii_search',
            data=json.dumps(request_data),
            endpoint=self.conn.search_endpoint,
        )
        try:
            results = response.json()['results']
        except KeyError:
            raise matchlight.error.SDKError('Failed to get search results')
        for result in results:
            # This result can seemingly be in different formats.
            try:
                result['ts'] = int(result['ts'])
            except ValueError:
                pass
            if isinstance(result['ts'], six.text_type):
                result['ts'] = datetime.datetime.strptime(
                    result['ts'],
                    '%Y-%m-%dT%H:%M:%S'
                )
            elif isinstance(result['ts'], int):
                result['ts'] = datetime.datetime.fromtimestamp(
                    float(result['ts'])
                )

            yield result
