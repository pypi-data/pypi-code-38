# -*- coding: utf-8 -*-

from eea.facetednavigation.interfaces import IFacetedLayout
from hashlib import md5
from ideabox.policy import utils
from plone.memoize import ram

import time


def faceted_query_handler(obj, event):
    if obj.REQUEST.ACTUAL_URL.endswith("@@faceted_query"):
        try:
            layout = IFacetedLayout(obj).layout
        except TypeError:
            layout = None
        if layout == "faceted-project":
            randomizer = Randomizer(obj.REQUEST)
            event.query["sort_on"] = randomizer.random_sort_key
            event.query["sort_order"] = randomizer.random_sort_order


def _cache_key(function, generator):
    return (generator, time.time() // (12 * 60 * 60))


@ram.cache(_cache_key)
def random_key_generator(generator):
    return md5(generator).hexdigest()


class Randomizer(object):

    _keys = {
        0: "UID",
        1: "project_random_1",
        2: "project_random_2",
        3: "project_random_3",
        4: "project_random_4",
        5: "project_random_5",
        6: "project_random_6",
        7: "project_random_7",
    }
    _sort_order_keys = ("ascending", "descending")

    def __init__(self, request):
        self.request = request
        now = utils.now()
        generator = "{0}-{1}".format(
            self.request.cookies.get(
                "__ac", self.request.cookies.get("beaker.session")
            ),
            now.strftime("%H"),
        )
        self.key = random_key_generator(generator)

    @property
    def random_sort_key(self):
        key = ord(self.key[0])
        return self._keys[key % len(self._keys)]

    @property
    def random_sort_order(self):
        key = ord(self.key[-1])
        return self._sort_order_keys[key % len(self._sort_order_keys)]
