__author__ = 'hachterberg'

import re

import fastr
from fastr.plugins import FastrInterface


class StdoutCollector(FastrInterface.collector_plugin_type):
    """
    The StdoutCollector can collect data from the stdout stream of a program.
    It filters the ``stdout`` line by line matching a predefined regular expression.

    The general working is as follows:

    1. The location field is taken from the output
    2. The substitutions are performed on the location field (see below)
    3. The updated location field will be used as a :ref:`regular expression <python:re-syntax>` filter
    4. The ``stdout`` is scanned line by line and the :ref:`regular expression <python:re-syntax>` filter is applied

    The special substitutions performed on the location use the
    Format Specification Mini-Language :ref:`python:formatspec`.
    The predefined fields that can be used are:

    * ``inputs``, an objet with the input values (use like ``{inputs.image[0]}``)
    * ``outputs``, an object with the output values (use like ``{outputs.result[0]}``)
    * ``special`` which has two subfields:

      * ``special.cardinality``, the index of the current cardinality
      * ``special.extension``, is the extension for the output DataType

    .. note:: because the plugin scans line by line, it is impossible to catch
              multi-line output into a single value
    """
    def __init__(self):
        super(StdoutCollector, self).__init__()
        self.id = 'stdout'

    def _collect_results(self, interface, output, result):
        output_data = []
        result.result_data[output.id] = output_data
        location = output.location
        stdout = result.target_result.stdout
        cardinality = 0
        fastr.log.debug('Searching for {}'.format(location))
        specials, inputs, outputs = interface.get_specials(result.payload,
                                                           output,
                                                           cardinality)
        loc = location.format(input=inputs,
                              output=outputs,
                              special=specials,
                              input_parts=inputs,
                              output_parts=outputs)
        for line in stdout.splitlines():
            match = re.search(loc, line)
            if match is not None:
                value = '{regexp[0]}'.format(input=inputs,
                                             output=outputs,
                                             special=specials,
                                             input_parts=inputs,
                                             output_parts=outputs,
                                             regexp=match.groups())

                if output.separator is not None:
                    value = value.split(output.separator)
                else:
                    value = [value]

                for val in value:
                    fastr.log.info('Found value: {}'.format(val))
                    output_data.append(val)
                    cardinality += 1

                specials, inputs, outputs = interface.get_specials(result.payload,
                                                                   output,
                                                                   cardinality)
                loc = location.format(input=inputs,
                                      output=outputs,
                                      special=specials,
                                      input_parts=inputs,
                                      output_parts=outputs)
