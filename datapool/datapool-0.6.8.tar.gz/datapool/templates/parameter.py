# encoding: utf-8
from __future__ import print_function, division, absolute_import

from os.path import exists

from ..errors import Message
from ..yaml_stuff import load_yaml_and_bunchify
from .base import Adder


class ParameterAdder(Adder):

    template = """
- name: {name}
  unit: {unit}
  description: {description}
    """.strip()

    yaml = "parameters.yaml"

    def check_target(self, path):
        return True

    def main(self, landing_zone, presets, input_):

        self.dialog(landing_zone, presets, input_)

        new = self.template.format(**presets)

        if exists(self.path):
            parameters = load_yaml_and_bunchify(self.path)
            name = presets["name"]
            for parameter in parameters:
                if parameter.name == name:
                    raise Message(
                        "parameter with name '{}' already exists".format(name)
                    )
            existing = open(self.path).read()
            entry = existing.rstrip("\n") + "\n\n" + new
        else:
            entry = new

        self.write(entry)
        return "wrote {}".format(self.path)


p = ParameterAdder()
variables = p.variables
main = p.main
