# -*- coding: utf-8 -*-
from guillotina import configure
from guillotina.addons import Addon


@configure.addon(
    name="guillotina_linkintegrity",
    title="Link integrity support for guillotina")
class ManageAddon(Addon):

    @classmethod
    def install(cls, container, request):
        pass

    @classmethod
    def uninstall(cls, container, request):
        pass
