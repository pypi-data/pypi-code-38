import requests
import logging

from sgp4.earth_gravity import wgs72
from sgp4.io import twoline2rv

from . import get_tle_sources, fetch_tles_from_url, fetch_tle_from_celestrak


def fetch_tles(requested_norad_ids, verify=True):
    '''
    Returns the most recent TLEs found for the requested satellites
    available via Celestrak, CalPoly and AMSAT.
    '''

    # List of 2-tuples of the form (source, tle)
    # source is a human-readable string
    # tle is a 3-tuple of strings
    tles = dict()

    def update_tles(source, tle):
        if norad_id not in requested_norad_ids:
            # Satellite not requested,
            # skip.
            return

        if norad_id not in tles.keys():
            # Satellite requested and first occurence in the downloaded data,
            # store new TLE.
            tles[norad_id] = source, tle
            return

        # There are multiple TLEs for this satellite available.
        # Parse and compare epoch of both TLEs and choose the most recent one.
        current_sat = twoline2rv(tles[norad_id][1][1], tles[norad_id][1][2], wgs72)
        new_sat = twoline2rv(tle[1], tle[2], wgs72)
        if new_sat.epoch > current_sat.epoch:
            # Found a more recent TLE than the current one,
            # store the new TLE.
            logging.debug('Updated {}, epoch '
                          '{:%Y-%m-%d %H:%M:%S} > {:%Y-%m-%d %H:%M:%S}'.format(
                              norad_id,
                              new_sat.epoch,
                              current_sat.epoch))
            tles[norad_id] = source, tle

    # Fetch TLE sets from well-known TLE sources
    sources = get_tle_sources()

    for source, url in sources:
        logging.info('Fetch from {}'.format(url))
        try:
            new_tles = fetch_tles_from_url(url=url, verify=verify)
            logging.debug('Found TLEs for {}'.format(list(new_tles.keys())))
        except (requests.HTTPError, requests.Timeout):
            logging.warning('Failed to download from {}.'.format(source))
            continue
        except ValueError:
            logging.warning('Failed to parse catalog from {}.'.format(source))
            continue

        for norad_id, tle in new_tles.items():
            update_tles(source, tle)

    # Try fetching missing sats from another Celestrak endoint
    missing_norad_ids = set(requested_norad_ids) - set(tles.keys())

    for norad_id in missing_norad_ids:
        try:
            logging.info('Fetch {} from Celestrak (satcat)'.format(norad_id))
            tle = fetch_tle_from_celestrak(norad_id, verify=verify)
            update_tles('Celestrak (satcat)', tle)
        except (LookupError, requests.HTTPError, requests.Timeout):
            logging.warning('Fetch {} from Celestrak (satcat) failed!'.format(norad_id))
            continue

    return tles
