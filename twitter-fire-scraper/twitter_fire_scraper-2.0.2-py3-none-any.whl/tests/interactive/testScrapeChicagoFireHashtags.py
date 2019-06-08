"""
Demonstrates the ability to scrape tweets regarding chicago fires, and store them in a MongoDB database.

This does NOT use the Scraper object.
"""
# noinspection PyUnresolvedReferences
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError

import __init__

import argparse
import os

import tweepy
from tweepy import Status

import yaml
from twitter_fire_scraper.config import DataConfig, Config
from twitter_fire_scraper.twitter import TwitterAuthentication, GEOBOX_CHICAGO
from twitter_fire_scraper.util import geobox_to_geocode, status_to_url, get_status_text


def get_fire_search_terms():
    # Read hashtags from datafile.
    with open(DataConfig.FIRE_HASHTAGS_DATA_PATH) as f:
        fire_hashtags_data = yaml.load(f)
        return fire_hashtags_data['hashtags']


if __name__ == "__main__":

    # Prepare for command-line input.
    parser = argparse.ArgumentParser()
    parser.add_argument("-t", "--maxtweets", help="Max tweets to get.", required=False, default=10, type=int)

    # Parse arguments.
    args = parser.parse_args()

    # Maximum tweets to search for.
    MAX_TWEETS = args.maxtweets if args.maxtweets else \
        10

    # Radius to search for tweets in.
    TWEET_RADIUS = "50mi"

    # Set up twitter auth.
    twauth = TwitterAuthentication.autodetect_twitter_auth()

    api = tweepy.API(twauth.oauth_handler, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)

    # Get Twitter geocode from Chicago's geobox.
    geocode = geobox_to_geocode(GEOBOX_CHICAGO, TWEET_RADIUS)

    # List of search terms to search for.
    search_terms = get_fire_search_terms()

    print(
        "Scraping the top {n} tweets that reference search terms from our '{path}' datafile inside {geocode}".format(
            n=MAX_TWEETS, path=os.path.basename(DataConfig.FIRE_HASHTAGS_DATA_PATH), geocode=geocode))

    # All tweets, sorted by search term
    all_tweets = {}

    # For all search terms,
    for search_term in search_terms:  # type: str

        # Conduct a search.
        cursor = tweepy.Cursor(api.search, q=search_term, geocode=geocode)

        # Retrieve however many tweets we want, and store that in our dictionary.
        all_tweets[search_term] = [status for status in cursor.items(MAX_TWEETS)]

        print("{n} hits for {ht}:".format(n=len(all_tweets[search_term]), ht=search_term))

        # For all statuses that we retrieved,
        for status in all_tweets[search_term][0:5]:  # type: Status
            print(" " * 4),  # Prefix with four spaces to show hierarchy.
            print("<{}> :".format(status_to_url(status)))  # URL of tweet.

            print(" " * 4),  # Status belonging to URL.
            print(get_status_text(status).encode("UTF-8"))  # Status text.
            print

    print("Final results of scraping {n} tweets each from these search terms:".format(
        n=MAX_TWEETS))

    print(", ".join(search_terms))

    # Determine unique statuses found from all keywords

    # Unique statuses. Sets can contain no duplicate elements.
    unique_status_ids = set()  # type: set[long]
    total_statuses = 0  # Total amount of statuses found.
    for keyword, statuses in all_tweets.items():

        for status in statuses:
            unique_status_ids.add(status.id)  # Add the ID as it can be enumerated in a set and is unique.
            total_statuses += 1  # 1 more status!

    # Print out (by keyword) how many hits we get
    for keyword, statuses in all_tweets.items():
        print("{keyword:20s}: {n} hits".format(keyword=keyword, n=len(statuses)))

    # Print out how many unique statuses we get
    print("{uq} unique statuses out of {tot} total statuses with {dup} duplicates.".format(
        uq=len(unique_status_ids), tot=total_statuses, dup=total_statuses - len(unique_status_ids)))

    print("Saving to MongoDB database.")

    try:
        mongoclient = MongoClient(Config.DEFAULT_MONGODB_CONNECTION_STRING)

        # Save to a table that's the same name as the file because this is a test.
        mongodb = mongoclient[os.path.splitext(os.path.basename(__file__))[0]]
    except Exception as e:
        print("Failed to save tweets to MongoDB database.")
        print(e)
        exit(1)

    saved_tweets = 0
    for keyword, statuses in all_tweets.items():
        for status in statuses:  # type: Status

            obj = status._json

            # Create unique ID that is the ID of the tweet itself.
            obj['_id'] = status.id

            try:
                mongodb[keyword].insert_one(obj)
                saved_tweets += 1
            except DuplicateKeyError as e:  # Tweet already exists.
                pass

    print("Successfully saved all tweets. Saved {} new tweets.".format(saved_tweets))
