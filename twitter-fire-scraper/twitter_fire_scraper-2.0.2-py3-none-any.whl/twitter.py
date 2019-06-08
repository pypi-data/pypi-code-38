import json
import os

import tweepy
from pymongo import MongoClient
from tweepy import OAuthHandler, Status

from twitter_fire_scraper.config import Config
from twitter_fire_scraper.models import Point
from twitter_fire_scraper.util import get_status_text

GEOBOX_WORLD = [Point(-180, -90), Point(180, 90)]

# From http://boundingbox.klokantech.com/
GEOBOX_CHICAGO = [Point(41.573604, -87.965887, ), Point(42.085967, -87.367663, )]


class TwitterAuthentication(object):
    """Twitter authentication object.

    This is basically just a wrapper for Twitter API keys to prevent a bunch of variables being scattered everywhere.
    """

    @staticmethod
    def autodetect_twitter_auth(auth_filepath=Config.SECRETS_DATAFILE_PATH):
        # type: (str) -> TwitterAuthentication
        """
        Attempts to autodetect Twitter API keys from a file called 'secrets.json'.

        Using this method is inadvisable and only exists to aid our test cases.
        """
        print("WARNING: API key autodetection is inadvisable.")

        if not os.path.isfile(auth_filepath):
            print("Searched for {} but it did not exist.".format(auth_filepath))

            print("Either initialize a {} object with API keys, or make the file located at the above path.".format(
                TwitterAuthentication.__name__))

            Config.create_example_secrets()

            print("See {} for an example of a valid configuration file:".format(
                Config.SECRETS_DATAFILE_EXAMPLE_PATH))

            raise ValueError("No API keys in {} initializer".format(TwitterAuthentication.__name__))
        else:  # Path to auth file exists.
            return TwitterAuthentication.from_json(auth_filepath)

    @staticmethod
    def from_json(filepath):
        """
        Creates a TwitterAuthentication object from a JSON file.
        :param filepath: The path to the JSON file.
        :return: A TwitterAuthentication object.

        Uses the following keys:
            - consumer_key
            - consumer_secret
            - access_token
            - access_token_secret

        """
        file = open(filepath, 'r')
        json_object = json.load(file)
        file.close()

        return TwitterAuthentication(
            consumer_key=json_object['consumer_key'],
            consumer_secret=json_object['consumer_secret'],
            access_token=json_object['access_token'],
            access_token_secret=json_object['access_token_secret'],
        )

    def __init__(self, consumer_key, consumer_secret, access_token, access_token_secret):

        self.consumer_key = consumer_key
        self.consumer_secret = consumer_secret
        self.access_token = access_token
        self.access_token_secret = access_token_secret

        self.oauth_handler = OAuthHandler(self.consumer_key, self.consumer_secret)
        self.oauth_handler.set_access_token(self.access_token, self.access_token_secret)


# override tweepy.StreamListener to add logic to on_status
class SimpleFireStreamListener(tweepy.StreamListener):
    """A naive twitter stream listener that only watches for the phrase "fire".
    This is a simple demo and is best used on the command-line."""

    @staticmethod
    def is_relevant(status, verbose=False):
        # type: (Status, bool) -> bool
        """
        Tells you if a Status is relevant.
        :param status: The status.
        :param verbose: Should we print irrelevant statuses?
        :return: Whether or not the status is relevant.
        """

        text = get_status_text(status)

        if 'fire' in text:
            print("Relevant:")
            return True

        if verbose:
            # Show snapshot of irrelevant tweet
            print("Not relevant: {}".format(text))

        return False

    def on_status(self, status):
        # type: (SimpleFireStreamListener, Status) -> None

        if SimpleFireStreamListener.is_relevant(status, verbose=True):
            text = get_status_text(status)

            print("Relevant: " + text.encode("UTF-8"))


class MongoDBStreamListener(tweepy.StreamListener):
    """A twitter stream listener that logs flagged tweets to a MongoDB database."""

    @staticmethod
    def is_relevant(status, verbose=False):
        # type: (Status, bool) -> bool
        """
        Tells you if a Status is relevant.
        :param status: The status.
        :param verbose: Should we print irrelevant statuses?
        :return: Whether or not the status is relevant.
        """

        if 'fire' in get_status_text(status):
            return True

        return False

    def __init__(self, database_name="MongoDBStreamListener",
                 database_connection_string=Config.Defaults.MONGODB_CONNECTION_STRING):
        super(MongoDBStreamListener, self).__init__()

        # MongoDB client.
        self.mongoclient = MongoClient(database_connection_string)

        # MongoDB database name.
        self.mongodatabase = self.mongoclient[database_name]

        # Table to which tweets are saved.
        self.TWEETS_TABLE = database_name

    # noinspection PyUnresolvedReferences
    def on_status(self, status):
        # type: (MongoDBStreamListener, Status) -> None

        # Make text safe to print in console.
        safe_text = get_status_text(status).encode('UTF-8')

        # If the status is relevant,
        if MongoDBStreamListener.is_relevant(status):
            # Insert it into our database.
            self.mongodatabase[self.TWEETS_TABLE].insert_one(status._json)
            print("Hit: " + safe_text)
        else:
            print("Ign: " + safe_text)
