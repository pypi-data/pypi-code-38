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
from fastr.data import url as urltools
from fastr.utils.cmd import add_parser_doc_link


def get_parser():
    parser = argparse.ArgumentParser(description="executes an ioplugin",
                                     formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('-i', '--input', nargs='+', type=str, required=True,
                        help="The url to process (can also be a list)")
    parser.add_argument('-o', '--output', nargs='+', type=str, metavar='OUTPUT', required=True,
                        help="The output urls in vfs scheme (can also be a"
                             " list and should be the same size as --inurl)")
    parser.add_argument('-d', '--datatype', nargs='+', default=None, type=str,
                        help="The datatype of the source/sink data to handle")
    return parser


def sink():
    # No arguments were parsed yet, parse them now
    parser = add_parser_doc_link(get_parser(), __file__)
    args = parser.parse_args()

    fastr.log.info('Using Python version {} loaded from {}'.format(sys.version, sys.executable))
    fastr.log.info(('Arguments:\ninput: {}\noutput: {}\ndatatype: {}').format(
        args.input,
        args.output,
        args.datatype
    ))

    inputs = args.input
    outputs = args.output
    datatypes = args.datatype

    if len(datatypes) == 1:
        datatypes *= len(inputs)

    for input_, output, datatype in zip(inputs, outputs, datatypes):
        fastr.log.info('Processing {} --> {} [{}]'.format(input_, output, datatype))

        if datatype is not None:
            datatype = fastr.types[datatype]

        fastr.log.debug("datatype to use: {}".format(datatype))

        if urltools.isurl(input_):
            message = 'For Sink behaviour the sink should be a path, not a URL! (found {})'.format(input_)
            fastr.log.critical(message)
            raise exceptions.FastrValueError(message)

        parsed_output = up.urlparse(output)
        try:
            plugin = resources.ioplugins[parsed_output.scheme]
        except KeyError:
            message = "No valid scheme is supplied in: {} (Found {}). The following schemes are supported: {}".format(output, parsed_output.scheme, ' '.join(fastr.ioplugins.keys()))
            fastr.log.error(message)
            raise exceptions.FastrUnknownURLSchemeError(message)

        plugin.push_sink_data(input_, output, datatype)

    # Cleanup all plugins
    resources.ioplugins.cleanup()


def main():
    """
    Command line access to the IOPlugin sink
    """
    try:
        sink()
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
