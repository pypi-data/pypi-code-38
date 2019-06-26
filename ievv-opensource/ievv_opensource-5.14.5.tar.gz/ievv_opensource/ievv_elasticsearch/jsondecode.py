"""
Utilities for decoding the JSON returned by ElasticSearch.
"""
import dateutil.parser


def datetime(datetimestring):
    """
    Convert a datetime object from ElasticSearch (iso format)
    into a timezone-aware ``datetime.datetime`` object.
    """
    return dateutil.parser.parse(datetimestring, ignoretz=False)
