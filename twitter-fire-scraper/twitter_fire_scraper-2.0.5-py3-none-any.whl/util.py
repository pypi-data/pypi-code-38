from __future__ import print_function
import colorama
import json
from pymongo.database import Database
from pymongo.errors import DuplicateKeyError
from tweepy import Status
from typing import Dict, List

from twitter_fire_scraper.models import Point


def get_status_text(status):
    # type: (Status) -> str
    """Given a Status, return its text.

    This method favors longer text."""

    if hasattr(status, 'full_text'):
        return status.full_text

    if hasattr(status, 'text'):
        return status.text

    raise Exception("Status {} has no text?".format(status))


def dict_from_status(status):
    # type: (Status) -> dict
    """

    :param status: A Status object.
    :return: An object ready to be saved into a MongoDB database.
    """

    obj = status._json  # type: dict

    obj['_id'] = status.id

    return obj


def save_statuses_dict_to_json(status_dict, filepath="tweets.json"):
    """
    Utility function to extract tweets from a dictionary of Statuses and saves them to a csv file

    :param status_dict: A dict of {"category": {Status, Status, Status}, ...} objects
    :param filepath: Path to file where to save all tweets to
    """

    # Open file to write to
    with open(filepath, 'w') as outfile:
        json.dump(status_dict, outfile, indent=4)

    return


def save_statuses_dict_to_mongodb(status_dict, mongodb, print_on_duplicates=False):
    # type: (Dict[str, List[Status]], Database, bool) -> None
    """
    This is a utility function that saves a Dict[str, List[Status]] to a MongoDB database.

    It saves each Status to a collection of the same name as the dictionary key

    :param status_dict: A dict of {"category": {Status, Status, Status}, ...} objects.
    :param mongodb: A MongoDB Database object.
    :param print_on_duplicates Whether to log if we found a duplicate Status or not.
    """

    for category, statuses in status_dict.items():
        for status in statuses:  # type: Status

            # Create a dict from the status
            obj = dict_from_status(status)

            try:
                # Attempt to insert a status.
                mongodb[category].insert_one(obj)
            # If the status already exists,
            except DuplicateKeyError as e:
                # Error silently and continue (or print and continue)
                if print_on_duplicates:
                    print("Duplicate tweet ID {} was NOT inserted to {} collection. ".format(obj['_id'], category))
                pass


def save_single_status_to_mongodb(status, mongodb):
    # type: (Status) -> None

    # Create a dict from the status
    obj = dict_from_status(status)

    try:
        # Attempt to insert a status.
        mongodb.insert_one(obj)
    # If the status already exists,
    except DuplicateKeyError as e:
        # Error silently and continue (or print and continue)
        # if print_on_duplicates:
        print("Duplicate tweet ID {} was NOT inserted to {} collection. ".format(obj['_id'], category))
        pass


def merge_status_dict(d1, d2):
    # type: (Dict[str, List[Status]], Dict[str, List[Status]]) -> Dict[str, List[Status]]
    """
    Given two status dictionaries, merge them into one status dictionary.
    Does not modify either dictionary, and rather makes a new one.
    """
    results = dict()

    for term, statuses in d1.items():
        if term not in results:
            results[term] = list()

        for status in statuses:
            results[term].append(status)

    for term, statuses in d2.items():
        if term not in results:
            results[term] = list()

        for status in statuses:
            results[term].append(status)

    return results


def status_to_url(status):
    # type: (Status) -> str
    """Given a Status, return that status' url."""
    return "https://www.twitter.com/statuses/{id}".format(id=status.id)


def pretty_print_statuses(statuses):
    # type: (List[Status]) -> None
    for status in statuses:
        print("<{}>".format(status_to_url(status)))
        print(get_status_text(status))
        print()


def jsonify_status_dict(status_dict):
    # type: (Dict[str, List[Status]]) -> Dict[str, List[str]]
    """Take a Dict[str, List[Status]] and flatten its statuses into JSON objects.

    Example:

        flatten_status_dict({
            "icecream": [Status, Status],
            "cake": [Status]
            })

            ->

            {
                "icecream": [{"author": "@IceCreamLuvr", ...}, {"author": "@IceCreamHater", ...}],
                "cake": [{"author": "@CakeIsGod123", ...}]
            }
    """
    for term, statuses in status_dict.items():  # Only get the json of the tweet
        status_dict[term] = list([status._json for status in statuses])

    return status_dict


def flatten_status_dict(status_dict):
    # type: (Dict[str, List[Status]]) -> Dict[str, List[str]]
    """Take a Dict[str, List[Status]] and flatten its statuses into the text of the statuses.

    Example:

        flatten_status_dict({
            "icecream": [Status, Status],
            "cake": [Status]
            })

            ->

            {"icecream": ["mm icecream", "icecream sucks :("],
            "cake": ["CAKE!!!!"]}

    """
    for term, statuses in status_dict.items():  # Only print the text of the tweet
        status_dict[term] = list([get_status_text(status) for status in statuses])

    return status_dict


def geobox_from_points(points):
    # type: (List[Point]) -> List[float]
    """Given a list of points, flatten them starting from y and going to x.

    This function exists because for some reason Tweepy/Twitter API likes to
    have a bounding box with flipped lat/long coordinates.

    Example:
        `flatten_points([Point(x=1,y=2), Point(x=2,y=3)])`
        -->
        `[2, 1, 3, 2]`"""
    numbers = []

    for point in points:
        numbers.append(point.y)
        numbers.append(point.x)

    return numbers


def flatten_points(points):
    # type: (List[Point]) -> List[float]
    """Given a list of points, flatten them starting from x and going to y.

    Example:
        `flatten_points([Point(x=1,y=2), Point(x=2,y=3)])`
        -->
        `[1, 2, 2, 3]`"""

    numbers = []

    for point in points:
        numbers.append(point.x)
        numbers.append(point.y)

    return numbers


def geobox_to_geocode(geobox, radius):
    # type: (List[Point, Point], str) -> str
    """Given a geobox and a radius, return a valid Twitter geocode consisting of a point and radius."""
    midpoint = geobox[0].midpoint(geobox[1])

    return "{lat},{lon},{radius}".format(
        lat=midpoint.x,
        lon=midpoint.y,
        radius=radius,
    )


def is_retweet(status):
    # type: (Status) -> bool
    """Tells you if this Status is a retweet."""
    return "RT @" in get_status_text(status)


def strtobool(v):
    # type: (str) -> bool
    return v.lower() in ["yes", "true", "t", "1"]


def colorama_reset():
    # type: () -> None
    print(colorama.Fore.WHITE, end='')
    print(colorama.Back.BLACK, end='')


def colorama_highlight_red(text, keyword=None):
    # type: (str, str) -> str
    """
    Highlights text red for a terminal.
    :param text: Text.
    :param keyword: Keyword to highlight.
    :return: Highlighted text.
    """

    if keyword is None:
        keyword = text

    return text.replace(keyword, (colorama.Fore.WHITE + colorama.Back.RED +
                                  keyword +
                                  colorama.Fore.WHITE + colorama.Back.BLACK))
