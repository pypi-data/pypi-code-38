"""
This is a utility to provide a large amount of tweets to unit tests WITHOUT repeatedly incurring API hits.

This is cached in MEMORY, not to disk.

The idea here is this file gets run once and its data used repeatedly, instead of scraping the same terms again and again.

This is not strictly necessary, but will decrease API calls significantly if you don't care about reusing tweets.
"""
from typing import Dict, List

from tweepy import Status
from twitter_fire_scraper.util import geobox_to_geocode

from twitter_fire_scraper.twitter import GEOBOX_CHICAGO
from twitter_fire_scraper.scraper import TwitterAuthentication, Scraper

from functools import lru_cache


class CachedTweets:
    scraper = Scraper(twitter_authentication=TwitterAuthentication.autodetect_twitter_auth())

    @staticmethod
    @lru_cache(maxsize=None)
    def tweets_small():
        # type: () -> Dict[str, List[Status]]
        """Return a static list of 9 tweets that is generated once and re-used throughout the module's lifetime."""
        return CachedTweets.scraper.scrape_terms({"flood", "fire", "house fire"}, count=3)

    @staticmethod
    @lru_cache(maxsize=None)
    def tweets_small_no_retweets():
        # type: () -> Dict[str, List[Status]]
        """Return a static list of 9 non-retweet tweets that is generated once and re-used throughout the module's lifetime."""
        return CachedTweets.scraper.scrape_terms({"flood", "fire", "house fire"}, count=3, include_retweets=False)

    @staticmethod
    @lru_cache(maxsize=None)
    def tweets_small_geo():
        # type: () -> Dict[str, List[Status]]
        """
        Return a static list of 9 tweets geotagged 20 miles from Chicago's center that is generated once and re-used
        throughout the module's lifetime.
        """
        return CachedTweets.scraper.scrape_terms({"flood", "fire", "house fire"}, count=3,
                                                 geocode=geobox_to_geocode(GEOBOX_CHICAGO, "20mi"))

    @staticmethod
    @lru_cache(maxsize=None)
    def tweets_medium():
        # type: () -> Dict[str, List[Status]]
        """Return a static list of 60 tweets that is generated once and re-used throughout the module's lifetime."""
        return CachedTweets.scraper.scrape_terms({"flood", "fire", "house fire"}, count=20)

    @staticmethod
    @lru_cache(maxsize=None)
    def tweets_medium_no_retweets():
        # type: () -> Dict[str, List[Status]]
        """Return a static list of 60 non-retweet tweets that is generated once and re-used throughout the module's lifetime."""
        return CachedTweets.scraper.scrape_terms({"flood", "fire", "house fire"}, count=20, include_retweets=False)

    @staticmethod
    @lru_cache(maxsize=None)
    def tweets_medium_geo():
        # type: () -> Dict[str, List[Status]]
        """
        Return a static list of 60 tweets geotagged 20 miles from Chicago's center that is generated once and re-used
        throughout the module's lifetime.
        """
        return CachedTweets.scraper.scrape_terms({"flood", "fire", "house fire"}, count=20,
                                                 geocode=geobox_to_geocode(GEOBOX_CHICAGO, "20mi"))

    @staticmethod
    @lru_cache(maxsize=None)
    def tweets_large():
        # type: () -> Dict[str, List[Status]]
        """Return a static list of 300 tweets that is generated once and re-used throughout the module's lifetime."""
        return CachedTweets.scraper.scrape_terms({"flood", "fire", "house fire"}, count=100)

    @staticmethod
    @lru_cache(maxsize=None)
    def tweets_large_geo():
        # type: () -> Dict[str, List[Status]]
        """Return a static list of 300 tweets geotagged 20 miles from Chicago's center that is generated once and
        re-used throughout the module's lifetime."""
        return CachedTweets.scraper.scrape_terms({"flood", "fire", "house fire"}, count=100,
                                                 geocode=geobox_to_geocode(GEOBOX_CHICAGO, "20mi"))
