# encoding: utf-8
from __future__ import print_function, division, absolute_import

import os

from .base import Adder


class SiteAdder(Adder):

    template = """
name: {name}
description: {description}
street: {street}
postcode: {postcode}
city: {city}
coordinates:
    x: {x}
    y: {y}
    z: {z}

pictures:
    -
       path: images/DELETE_ME.png
       description: description
       # timestamp is optional:
       timestamp: 2018/01/31 12:34:56

    """.strip()

    yaml = "site.yaml"

    def extra_tasks(self):
        site_folder = os.path.dirname(self.path)
        picture_folder = os.path.join(site_folder, "images")
        os.makedirs(picture_folder)
        open(os.path.join(picture_folder, "DELETE_ME.png"), "w").close()


a = SiteAdder()
variables = a.variables
main = a.main
