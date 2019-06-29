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


def get_names(j):
    """ Get names from json response """
    return [i['text'].split(',')[0] for i in j['data']['Births']]


def apply_colours(days, colours):
    """ Apply given colours to list of names """
    cdays = [sopel.formatting.color(i, j)
             for i, j in zip(days, itertools.cycle(colours))]

    return cdays


def split_msg(days):
    msg = ', '.join(i.replace(' ', '\x1f') for i in days)
    lines = [i.replace('\x1f', ' ') for i in textwrap.wrap(msg, 400)]

    return lines


@sopel.module.commands('bdays')
def bdays(bot, trigger):
    r = requests.get('https://history.muffinlabs.com/date')
    rj = r.json()

    names = get_names(rj)
    colours = random.sample(['01', '02', '03', '04', '06', '08', '11'], 7)
    cnames = apply_colours(names, colours)

    for msg in split_msg(cnames):
        bot.say('{}'.format(msg))
