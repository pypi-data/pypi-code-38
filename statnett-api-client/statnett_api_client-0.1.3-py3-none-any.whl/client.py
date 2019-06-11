# -*- coding: utf-8 -*-

"""Client for reading data from Statnett REST API
"""

from statnett_api_client.topics import *
from statnett_api_client import config
from statnett_api_client.constants import TopicName


def get_flow(**kwargs):
    topic = Flow(**kwargs)
    return topic.get(config.topics[TopicName.flow.value])


def get_balance(**kwargs):
    topic = Balance(**kwargs)
    return topic.get(config.topics[TopicName.balance.value])


def get_frequency(**kwargs):
    topic = Frequency(**kwargs)
    return topic.get(config.topics[TopicName.frequency.value],
                     date_from=kwargs.get('date_from', None))

