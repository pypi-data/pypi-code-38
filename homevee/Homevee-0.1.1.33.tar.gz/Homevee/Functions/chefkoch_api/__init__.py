#!/usr/bin/python
# -*- coding: utf-8 -*-
import json
import urllib.error
import urllib.parse
import urllib.request

from Homevee.Helper import Logger


def get_recipe(id):
    url = "https://api.chefkoch.de/v2/recipes/"+str(id)

    result = urllib.request.urlopen(url).read()

    data = json.loads(result)

    return data

def search_recipes(keyword, limit=None, offset=None, min_rating=None, max_time=None):
    keyword = keyword.replace(" ", "%20")

    url = "https://api.chefkoch.de/v2/recipes?query=" + str(keyword)

    if limit is not None:
        url = url + "&limit=" + str(limit)

    if offset is not None:
        url = url + "&offset=" + str(offset)

    if min_rating is not None:
        url = url + "&minimumRating=" + str(min_rating)

    if max_time is not None:
        url = url + "&maximumTime=" + str(max_time)

    Logger.log(url)

    result = urllib.request.urlopen(url).read()

    result = json.loads(result)

    recipes = result['results']

    return recipes