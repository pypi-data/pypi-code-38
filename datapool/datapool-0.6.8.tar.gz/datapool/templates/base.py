# encoding: utf-8
from __future__ import print_function, division, absolute_import

from os.path import join, exists

from ..errors import Message
from datapool.instance.landing_zone_structure import relative_path_for_yaml
from ..utils import open_and_create_folders
from .utils import ask_values, template_variables


class Adder:

    template = None
    yaml = None

    def variables(self):
        return template_variables(self.template)

    def dialog(self, landing_zone, presets, input_):
        self.path = None
        for result in ask_values(self.variables(), presets, input_):
            if result is None:
                raise Message("aborted")
            self.check_presets(landing_zone, presets)

    def check_presets(self, landing_zone, presets):
        rel_path = relative_path_for_yaml(self.yaml, presets)
        if rel_path is not None:
            path = join(landing_zone, rel_path)
            if path is not None and self.check_target(path):
                self.path = path

    def check_target(self, path):
        if path is not None and exists(path):
            raise Message("error: {} already exists".format(path))
        return True

    def write(self, data):
        with open_and_create_folders(self.path, "w") as fh:
            fh.write(data)

    def main(self, landing_zone, presets, input_):
        self.dialog(landing_zone, presets, input_)
        data = self.template.format(**presets)
        self.write(data)
        self.extra_tasks()
        return "wrote {}".format(self.path)

    def extra_tasks(self):
        pass
