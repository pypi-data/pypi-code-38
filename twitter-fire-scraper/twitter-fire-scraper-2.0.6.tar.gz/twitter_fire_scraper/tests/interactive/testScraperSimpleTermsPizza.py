"""
This file demonstrates the Scraper class' ability to scrape small amounts of tweets about a simple term or hashtag, like
'pizza', '#pizza', 'cat', and '#cat'.
"""

import __init__

from pprint import pprint

from twitter_fire_scraper.scraper import Scraper
from twitter_fire_scraper.twitter import GEOBOX_CHICAGO
from twitter_fire_scraper.util import geobox_to_geocode, flatten_status_dict

if __name__ == '__main__':
    scraper = Scraper()

    terms = {"#pizza", "pizza", 'cat', '#cat'}

    results = scraper.scrape_terms(terms=terms, count=3)
    results = flatten_status_dict(results)

    print("{} on all of twitter:".format(", ".join(terms)))
    pprint(results)

    results = scraper.scrape_terms(geocode=geobox_to_geocode(GEOBOX_CHICAGO, "20mi"), terms=terms, count=3)
    results = flatten_status_dict(results)
    print("{} in chicago:".format(", ".join(terms)))
    pprint(results)

    # scraper = Scraper()
    #
    # results = scraper.scrape_accounts(accounts=['MABASIllinois','NWSChicago'])
    #
    # pprint(results)
