"""
Demonstrates the ability to listen in a geo-location for the keyword 'fire'.
"""
# noinspection PyUnresolvedReferences
import __init__

import time

import tweepy

from twitter_fire_scraper.twitter import SimpleFireStreamListener, TwitterAuthentication, GEOBOX_CHICAGO
from twitter_fire_scraper.util import geobox_from_points

if __name__ == "__main__":

    # Set up twitter auth.
    twauth = TwitterAuthentication.autodetect_twitter_auth()
    api = tweepy.API(twauth.oauth_handler)

    print("Using our simple 'fire' stream listener, let's see what Chicago geotagged tweets have 'fire' in them.")

    simpleFireStreamListener = SimpleFireStreamListener()
    simpleFireStream = tweepy.Stream(auth=api.auth, listener=simpleFireStreamListener)

    print("Streaming for 60 seconds.")
    simpleFireStream.filter(locations=geobox_from_points(GEOBOX_CHICAGO), is_async=True)
    try:
        time.sleep(60)
    except KeyboardInterrupt:
        simpleFireStream.disconnect()
    finally:
        simpleFireStream.disconnect()
