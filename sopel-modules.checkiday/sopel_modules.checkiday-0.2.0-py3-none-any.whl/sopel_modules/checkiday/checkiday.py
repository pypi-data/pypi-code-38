# coding=utf-8

from __future__ import (unicode_literals, absolute_import,
                        division, print_function)
import itertools
import random
import textwrap

import sopel.module
import sopel.formatting
import requests


def configure(config):
    pass


def setup(bot):
    pass


def request_api():
    """ Fetch json from checkiday api """
    r = requests.get('https://www.checkiday.com/api/3/?d')

    rj = r.json()

    if rj['error'] != 'none':
        raise ValueError('Api call returned error: {}'.format(rj['error']))

    return rj


def get_days_from_json(j):
    """ Return just the day names from the json response """
    return [i['name'] for i in j['holidays']]


def apply_colours(days, colours):
    """ Apply given colours to list of day names """
    cdays = [sopel.formatting.color(i, j)
             for i, j in zip(days, itertools.cycle(colours))]

    return cdays


def split_msg(days):
    msg = ', '.join(i.replace(' ', '\x1f') for i in days)
    lines = [i.replace('\x1f', ' ') for i in textwrap.wrap(msg, 400)]

    return lines


@sopel.module.commands('days')
def days(bot, trigger):
    rj = request_api()
    days = get_days_from_json(rj)
    colours = random.sample(['01', '02', '03', '04', '06', '08', '11'], 7)
    cdays = apply_colours(days, colours)

    for msg in split_msg(cdays):
        bot.say('{}'.format(msg))
