# encoding: utf-8
from __future__ import print_function, division, absolute_import

from os.path import join, exists
import os
import glob

from ..errors import Message
from datapool.instance.landing_zone_structure import relative_path_for_yaml
from ..yaml_stuff import load_yaml_and_bunchify
from .base import Adder
from .utils import template_variables


def find_source_type(landing_zone, source_type):
    pattern = relative_path_for_yaml("source_type.yaml", dict(name="*"))

    for p in glob.glob(join(landing_zone, pattern)):
        b = load_yaml_and_bunchify(p)
        if b.name == source_type:
            return p

    return None


class SourceAdder(Adder):

    template = """
name: {name}
description: {description}
serial: {serial}
manufacturer: {manufacturer}
manufacturing_date: {manufacturing_date}
""".strip()

    yaml = "source.yaml"

    def variables(self):
        return ["source_type"] + template_variables(self.template)

    def check_presets(self, landing_zone, presets):
        super().check_presets(landing_zone, presets)
        source_type = presets.get("source_type")
        if source_type is not None:
            p = find_source_type(landing_zone, source_type)
            if p is None:
                raise Message("source_type '{}' does not exists".format(source_type))

    def extra_tasks(self):

        raw_data_folder = join(os.path.dirname(self.path), "raw_data")
        if not exists(raw_data_folder):
            os.makedirs(raw_data_folder)

    def main(self, *a):
        super().main(*a)
        return "please check {} and maybe modify the special_values dummy section".format(
            self.path
        )


sa = SourceAdder()
variables = sa.variables
main = sa.main
