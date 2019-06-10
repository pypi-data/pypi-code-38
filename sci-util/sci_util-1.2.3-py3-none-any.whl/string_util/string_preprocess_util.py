#!/usr/bin/python
# -*- coding: utf-8 -*-
# Author: violinsolo
# Created on 28/09/2018


FILTER_TOKENS = {
    ' ': '',
    '\n': '',
    '\t': '',
    '\r': '',
    '󾠮': '',
    '🏻': '',
    '🏼': '',
    '𓆟': '',
}


def filter_string(target: str, to_removed_tokens: list=None) -> str:
    """
    element-wise doing filter, do filtering for target string

    :param to_removed_tokens:
        list of str, that need to filtered from :param target,
        default is FILTER_TOKENS
    :param target:
        target string ...
    :return:
        filtered :param target.
    """
    result = target

    if to_removed_tokens is None:
        to_removed_tokens = FILTER_TOKENS

    for key, value in to_removed_tokens.items():
        result = result.replace(key, value)

    return result




if __name__ == '__main__':
    res = filter_string(' \n 222 \t')
    print(f'"{res}"')
