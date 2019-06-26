"""
This file demonstrates the Scraper class' ability to scrape small amounts of tweets from a list of accounts.
"""

import __init__

from pprint import pprint

import yaml

from twitter_fire_scraper.config import DataConfig
from twitter_fire_scraper.scraper import Scraper

if __name__ == '__main__':
    scraper = Scraper()

    with open(DataConfig.TWITTER_ACCOUNTS_DATA_PATH, errors='ignore') as f:
        accountsYml = yaml.load(f)

    # First 5 accounts from Twitter Account list.
    accounts = accountsYml['accounts'][0:5]

    # Amount to get.
    count = 3

    print("Scraping top {} tweets from these accounts:".format(count))
    print(", ".join(["@" + account for account in accounts]))

    results = scraper.scrape_accounts(accounts=accounts, count=count)
    pprint(results)
