# Version of the slacktory package
__version__ = "1.0.4"
"""

  _______   __                  __      __
 |   _   | |  | .---.-. .----. |  |--. |  |_  .-----. .----. .--.--.
 |   1___| |  | |  _  | |  __| |    <  |   _| |  _  | |   _| |  |  |
 |____   | |__| |___._| |____| |__|__| |____| |_____| |__|   |___  |
 |:  1   |                                                   |_____|
 |::.. . |
 `-------'



For this decorator to work, you must first create a local_settings.py file in your project's root directory with the following content:

---------------------------------------------------
name = '<your slack channel name>'
channel = '<your slack channel id>'
token = '<your slack API token>'
webhook = '<your slack channel webhook>'
---------------------------------------------------

All of this information can be obtained when setting up a Slack App here: https://api.slack.com/apps

"""
try:
    from local_settings import *
except ModuleNotFoundError:
    raise ModuleNotFoundError(
        "No local_settings.py file was found in your project root directory. See README.md for details"
    )
import requests
import functools
import collections
from time import sleep

SlackChannel = collections.namedtuple('SlackChannel', 'name channel token webhook')

chan = SlackChannel(
    name=name,
    channel=channel,
    token=token,
    webhook=webhook)

history_url = 'https://slack.com/api/channels.history'
data = {'token': chan.token, 'channel': chan.channel}
headers = {'content-type': 'application/x-www-form-urlencoded'}


def watch(text_list):
    """
    A decorator that watches a Slack channel for specific text posts
    :param text_list: List of strings to watch for
    :return:

    """

    def decorator_slack_check(func):
        @functools.wraps(func)
        def wrapper_slack_check(*args, **kwargs):

            def last_message():
                # get the last message post in the slack channel
                return requests.post(history_url, data=data, headers=headers).json()['messages'][0]

            try:
                # get time stamp from most recent message post in the slack channel
                baseline = last_message()
                baseline_ts = baseline['ts']

            except requests.ConnectionError:
                sleep(1)
                wrapper_slack_check(*args, **kwargs)

            def check_for_new_post():
                try:
                    nonlocal baseline
                    nonlocal baseline_ts
                    # get most recent message post in the slack channel
                    slack_post2 = last_message()
                except requests.ConnectionError:
                    slack_post2 = baseline
                    check_for_new_post()

                # if the time stamp differs between the two message posts, then there has been a new post in the channel.
                # If the post contains text from text_list then execute the decorated function
                if slack_post2['ts'] != baseline_ts and slack_post2['text'] in text_list:
                    baseline = slack_post2
                    baseline_ts = slack_post2['ts']
                    func(*args, **kwargs)

            while True:
                check_for_new_post()
                sleep(1)

        return wrapper_slack_check

    return decorator_slack_check
