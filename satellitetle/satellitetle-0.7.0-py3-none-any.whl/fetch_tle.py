import csv
import requests
import pkg_resources
import logging

from lxml import html
from sgp4.earth_gravity import wgs72
from sgp4.io import twoline2rv

logger = logging.getLogger(__name__)


SOURCES_LIST = pkg_resources.resource_filename('satellite_tle', 'sources.csv')

REQUESTS_TIMEOUT = 20  # seconds


def get_tle_sources():
    '''
    Returns a list of (source, url)-tuples for well-known TLE sources.
    '''

    sources = []

    with open(SOURCES_LIST) as csvfile:
        csv_reader = csv.reader(csvfile,
                                delimiter=',',
                                quotechar='\'',
                                quoting=csv.QUOTE_NONNUMERIC)
        for row in csv_reader:
            source, url = row
            sources.append((source, url))

    return sources


def fetch_tle_from_celestrak(norad_cat_id, verify=True):
    '''
    Returns the TLE for a given norad_cat_id as currently available from CelesTrak.
    Raises IndexError if no data is available for the given norad_cat_id.

    Parameters
    ----------
    norad_cat_id : string
        Satellite Catalog Number (5-digit)
    verify : boolean or string, optional
        Either a boolean, in which case it controls whether we verify
        the server's TLS certificate, or a string, in which case it must be a path
        to a CA bundle to use. Defaults to ``True``. (from python-requests)
    '''

    r = requests.get('https://www.celestrak.com/satcat/tle.php?CATNR={}'.format(norad_cat_id),
                     verify=verify,
                     timeout=REQUESTS_TIMEOUT)
    r.raise_for_status()

    page = html.fromstring(r.text)

    tle = page.xpath('//pre/text()')[0].split('\n')
    if tle[1].strip() == 'No TLE found':
        raise LookupError

    return tle[1].strip(), tle[2].strip(), tle[3].strip()


def fetch_tles_from_url(url, verify=True):
    '''
    Downloads the TLE set from the given url.
    Returns a dictionary of the form {norad_id1: tle1, norad_id2: tle2} for all TLEs found.
    tleN is returned as list of three strings: [satellite_name, line1, line2].

    Parameters
    ----------
    url : string
        URL of the TLE source
    verify : boolean or string, optional
        Either a boolean, in which case it controls whether we verify
        the server's TLS certificate, or a string, in which case it must be a path
        to a CA bundle to use. Defaults to ``True``. (from python-requests)
    '''

    r = requests.get(url, verify=verify, timeout=REQUESTS_TIMEOUT)
    r.raise_for_status()

    tles = dict()
    lines = r.text.splitlines()

    # Loop over TLEs
    for i in range(len(lines) - 2):
        if (lines[i + 1][0] == "1") & (lines[i + 2][0] == "2"):
            try:
                twoline2rv(lines[i + 1], lines[i + 2], wgs72)
                norad_cat_id = int(lines[i + 1][2:7].encode('ascii'))
                tles[norad_cat_id] = (lines[i].strip(), lines[i + 1], lines[i + 2])
            except ValueError:
                logging.warning('Failed to parse TLE for {}\n({}, {})'.format(
                    lines[i], lines[i + 1], lines[i + 2]))

    return tles
