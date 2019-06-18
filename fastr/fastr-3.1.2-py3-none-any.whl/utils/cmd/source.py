# Copyright 2011-2014 Biomedical Imaging Group Rotterdam, Departments of
# Medical Informatics and Radiology, Erasmus MC, Rotterdam, The Netherlands
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import argparse
import json
import sys
import urllib.parse as up

import fastr
from fastr import exceptions, resources
from fastr.core.ioplugin import IOPlugin
from fastr.data import url as urltools
from fastr.utils.cmd import add_parser_doc_link


def get_parser():
    parser = argparse.ArgumentParser(description="Executes an source command",
                                     formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('-i', '--input', nargs='+', type=str, required=True,
                        help="The url to process (can also be a list)")
    parser.add_argument('-o', '--output', type=str, metavar='OUTPUT', required=True,
                        help="The output url in vfs scheme")
    parser.add_argument('-d', '--datatype', default=None, type=str,
                        help="The datatype of the source/sink data to handle")
    parser.add_argument('-s', '--sample_id', default=None, type=str,
                        help="The sample_id of the source/sink data to handle")
    return parser


def source():
    # No arguments were parsed yet, parse them now
    parser = add_parser_doc_link(get_parser(), __file__)
    args = parser.parse_args()

    fastr.log.info('Using Python version {} loaded from {}'.format(sys.version, sys.executable))
    fastr.log.info(('Arguments:\ninput: {}\noutput: {}\n'
                    'datatype: {}\nsample_id: {}').format(args.input,
                                                          args.output,
                                                          args.datatype,
                                                          args.sample_id))

    inputs = args.input
    output = args.output
    sample_id = args.sample_id
    datatype = args.datatype

    if datatype is not None:
        datatype = fastr.types[datatype]
    fastr.log.debug("datatype to use: {}".format(datatype))

    if sample_id is None:
        message = 'For Source behaviour the sample id needs to be defined!'
        fastr.log.critical(message)
        raise exceptions.FastrValueError(message)

    if urltools.isurl(output):
        message = 'For Source behaviour the output should be a directory, not a URL! (found {})'.format(output)
        fastr.log.critical(message)
        raise exceptions.FastrValueError(message)

    results = []
    for input_ in inputs:
        if urltools.isurl(input_):
            parsed_input = up.urlparse(input_)
            try:
                plugin = resources.ioplugins[parsed_input.scheme]
            except KeyError:
                message = "No valid scheme is supplied in: {} (Found {}). The following schemes are supported: {}".format(
                    input_,
                    parsed_input.scheme,
                    ' '.join(resources.ioplugins.keys())
                )
                fastr.log.error(message)
                raise exceptions.FastrUnknownURLSchemeError(message)

            results.append(plugin.pull_source_data(input_, output, sample_id, datatype))
        else:
            results.append(input_)

    if len(results) == 1:
        # If we have only one result, there is no need to merge
        result = results[0]
    else:
        # Merge multiple cardinality into a single result
        samples = set()
        for part in results:
            # Check if we got value or if the value was a simple value
            if isinstance(part, dict):
                samples.update(part.keys())

        # For each sample collect all found values
        result = {}
        for sample_id in samples:
            result[sample_id] = temp = []

            for part in results:
                if isinstance(part, dict):
                    # We have a dictionary with {sampleid: (value1, value2)} format
                    temp.extend(part.get(sample_id, []))
                else:
                    # We have a value (not URL) that was given, we assume this to be used for ALL samples (broadcasting)
                    temp.append(part)

    IOPlugin.print_result(result)

    # Cleanup all plugins
    resources.ioplugins.cleanup()


def main():
    """
    Command line access to the IOPlugin source
    """
    try:
        source()
    except Exception as exception:
        # Pass error on to main process and raise error again
        exception = (
            type(exception).__name__,
            str(exception),
            exception.filename if hasattr(exception, 'filename') else None,
            exception.linenumber if hasattr(exception, 'linenumber') else None,
        )

        print('__FASTR_ERRORS__ = {}'.format(
            json.dumps(
                [exception]
            )
        ))
        raise

if __name__ == '__main__':
    main()
