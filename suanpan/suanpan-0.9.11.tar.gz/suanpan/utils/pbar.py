# coding=utf-8
from __future__ import absolute_import, print_function

import functools

import tqdm

from suanpan import utils

DEFAULT_PBAR_FORMAT = "{desc}: {n_fmt}/{total_fmt} |{bar}"
DEFAULT_PBAR_CONFIG = {"bar_format": DEFAULT_PBAR_FORMAT}


def parseConfig(config):
    if config is True:
        return utils.merge(DEFAULT_PBAR_CONFIG, {"desc": "Processing"})
    if isinstance(config, str):
        return utils.merge(DEFAULT_PBAR_CONFIG, {"desc": config})
    if config in (False, None):
        return utils.merge(DEFAULT_PBAR_CONFIG, {"disable": True})
    if isinstance(config, dict):
        return utils.merge(DEFAULT_PBAR_CONFIG, config)
    raise Exception("Invalid pbar config: bool | str | dict. but {}".format(config))


def runner(pbar, quantity=1):
    def _dec(func):
        @functools.wraps(runner)
        def _runner(*args, **kwargs):
            result = func(*args, **kwargs)
            pbar.update(quantity)
            return result

        return _runner

    return _dec


def getIterableLen(iterable=None, config=None, total=None):
    if config and total is None and iterable is not None:
        iterable = list(iterable)
        total = len(iterable)
    return iterable, total


def one(iterable=None, config=True, total=None, **kwargs):
    iterable, total = getIterableLen(iterable, config=config, total=total)
    params = parseConfig(config)
    params.update(total=total)
    params.update(kwargs)
    return tqdm.tqdm(iterable, **params)


def multi(iterables=None, configs=True, totals=None, **kwargs):
    return Group(iterables=iterables, configs=configs, totals=totals, **kwargs)


class Group(object):
    def __init__(self, iterables=None, configs=True, totals=None, **kwargs):
        lengths = [
            len(i) for i in (iterables, configs, totals) if isinstance(i, (tuple, list))
        ]
        length = min(lengths) if lengths else 0
        if not isinstance(iterables, (tuple, list)):
            iterables = [iterables] * length
        if not isinstance(configs, (tuple, list)):
            configs = [configs] * length
        if not isinstance(totals, (tuple, list)):
            totals = [totals] * length
        self.pbars = [
            one(iterable, config=config, total=total, position=i, **kwargs)
            for i, (iterable, config, total) in enumerate(
                zip(iterables, configs, totals)
            )
        ]

    def add(self, iterable=None, config=True, total=None, **kwargs):
        pbar = one(
            iterable=iterable,
            config=config,
            total=total,
            position=len(self.pbars),
            **kwargs
        )
        self.pbars.append(pbar)
        return pbar

    def get(self, idx):
        return self.pbars[idx]
