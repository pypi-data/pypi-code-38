# -*- coding: utf-8 -*-

""" KojiTag Module """

import wrapt

from koji_wrapper.wrapper import KojiWrapper


class BuildSet(KojiWrapper):
    def __init__(self, tag=None,
                 nvr_blacklist=None, blacklist=None,
                 client=None):
        self.nvr_blacklist = nvr_blacklist
        self.blacklist = blacklist
        self.__builds = None

class TaggedBuildSet(BuildSet):
    
    def __init__(self, tag=None, **kwargs):
        self.__tag = tag
        self.__latest = None
        super().__init__(**kwargs)


