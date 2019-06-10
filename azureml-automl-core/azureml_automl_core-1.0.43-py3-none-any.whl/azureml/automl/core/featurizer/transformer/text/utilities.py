# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Utilities for text featurization."""
max_ngram_len = 3


def get_ngram_len(lens_series):
    """
    Get N-grams length required for text transforms.

    :param lens_series: Series of lengths for a string.
    :return: The ngram to use.
    """
    lens_series = lens_series.apply(lambda x: min(x, max_ngram_len))
    return lens_series.mode()[0]
