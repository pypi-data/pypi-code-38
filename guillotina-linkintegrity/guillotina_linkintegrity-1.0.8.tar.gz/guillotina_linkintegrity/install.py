# -*- coding: utf-8 -*-
from guillotina import configure
from guillotina.addons import Addon


@configure.addon(
    name="guillotina_linkintegrity",
    title="Link integrity support for guillotina")
class ManageAddon(Addon):

    @classmethod
    def install(cls, container, request):
        registry = request.container_settings  # noqa
        # install logic here...

    @classmethod
    def uninstall(cls, container, request):
        registry = request.container_settings  # noqa
        # uninstall logic here...
