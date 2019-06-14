import json
import os


class Config(object):
    """
    This class stores configuration information like config file paths, default values, etc.
    """

    class Defaults(object):
        """
        This class stores default values for configuration.
        """

        MONGODB_CONNECTION_STRING = "mongodb://localhost:27017/"
        """The connection string for the MongoDB server."""

        API_PORT = 3620
        """The port the HTTP API exposing the Scraper object's functions operates in."""

    @staticmethod
    def example_secrets_json():
        # type: () -> str
        """
        :return: An example of what the secrets.json configuration file should look like.
        """
        return json.dumps({
            'consumer_key': 'ABCDEFG_I_WOULD_LIKE_YOU_TO_REPLACE_ME',
            'consumer_secret': 'ABCDEFG_I_WOULD_LIKE_YOU_TO_REPLACE_ME',
            'access_token': 'ABCDEFG_I_WOULD_LIKE_YOU_TO_REPLACE_ME',
            'access_token_secret': 'ABCDEFG_I_WOULD_LIKE_YOU_TO_REPLACE_ME',
        }, indent=4, sort_keys=True)

    @staticmethod
    def create_example_secrets():
        """Create an example file that serves as `secrets.json` for the user to populate."""

        if not os.path.exists(Config.CONFIG_FOLDER):
            os.mkdir(Config.CONFIG_FOLDER)

        if not os.path.exists(Config.SECRETS_DATAFILE_EXAMPLE_PATH):
            with open(Config.SECRETS_DATAFILE_EXAMPLE_PATH, 'w') as f:
                f.write(Config.example_secrets_json())

    CONFIG_FOLDER = os.path.abspath(os.path.expanduser("~/.twitterfirescraper"))
    """The folder that configuration files, secrets, etc. get stored in."""

    SECRETS_DATAFILE_PATH = os.path.join(CONFIG_FOLDER, "secrets.json")
    """The file that stores Twitter API keys."""

    SECRETS_DATAFILE_EXAMPLE_PATH = os.path.join(CONFIG_FOLDER, "secrets.example.json")
    """The file that serves as an example of the secrets datafile."""

    CONFIG_FILE = os.path.join(CONFIG_FOLDER, "config.json")
    """The file that stores configuration such as rate limiting, API ports, etc."""


def try_get(object, key):
    """Tries to get the value of a key in an object, and politely notifies you if it cannot find it."""

    if key not in object:
        raise KeyError("Could not find " + key + " inside of " + object + "! Does it exist?")

    return object[key]


class DataConfig:
    """Holds data and filepath configuration information for data files such as state names, hashtags we wish to track,
    terms that indicate fires or disasters, etc."""

    # Folder name that data is stored in.
    DATA_FOLDER_NAME = "data"

    # Path data is stored in.
    DATA_PATH = os.path.join(os.path.dirname(os.path.realpath(__file__)), DATA_FOLDER_NAME)

    # Disaster hashtag datafile location.
    DISASTER_HASHTAGS_DATA_PATH = os.path.join(DATA_PATH, "DisasterHashtags.yml")

    # Fire hashtag datafile location.
    FIRE_HASHTAGS_DATA_PATH = os.path.join(DATA_PATH, "FireHashtags.yml")

    # US major cities datafile location.
    MAJOR_CITIES_DATA_PATH = os.path.join(DATA_PATH, "MajorCities.yml")

    # US states datafile location.
    US_STATES_DATA_PATH = os.path.join(DATA_PATH, "USStates.yml")

    TWITTER_ACCOUNTS_DATA_PATH = os.path.join(DATA_PATH, "TwitterAccounts.yml")
