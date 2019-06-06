# encoding: utf-8
from __future__ import print_function, division, absolute_import


from .base import Adder


class SourceTypeAdder(Adder):

    template = """
name: {name}
description: {description}
special_values:
    - categorical_value: NA
      numerical_value: -666.0
      description: not a number
    """.rstrip()

    yaml = "source_type.yaml"

    def main(self, landing_zone, presets, input_):
        super().main(landing_zone, presets, input_)
        return "wrote {}, please edit the special_values dummy section".format(
            self.path
        )


s = SourceTypeAdder()
variables = s.variables
main = s.main
