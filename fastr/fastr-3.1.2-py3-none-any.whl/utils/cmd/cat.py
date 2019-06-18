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
from fastr.helpers.iohelpers import load_gpickle, load_json
from fastr.utils.cmd import add_parser_doc_link
FASTR_LOG_TYPE = 'none'  # Do not get info about fastr


def get_parser():
    parser = argparse.ArgumentParser(
        description="Extract selected information from the extra job info. The path"
                    " is the selection of the data to retrieve. Every parts of the"
                    " path (separated by a /) is seen as the index for the previous"
                    " object. So for example to get the stdout of a job, you could use"
                    " 'fastr cat __fastr_extra_job_info__.json process/stdout'."
    )
    parser.add_argument('infile', metavar='__fastr_extra_job_info__.json', help='result file to cat')
    parser.add_argument('path', help='path of the data to print')
    return parser


def fastr_cat(infile, path):
    import os
    from pprint import pprint

    path = path.strip('/').split('/')

    if os.path.isdir(infile):
        infile = os.path.join(infile, '__fastr_result__.pickle.gz')

        if not os.path.isfile(infile):
            print('ERROR: Input file does not exist!')
            return

    if infile.endswith('.pickle.gz'):
        try:
            job = load_gpickle(infile)
            infile = job.extrainfofile
        except IOError:
            print('ERROR: Could not open {} for reading'.format(infile))

    data = load_json(infile)

    for part in path:
        try:
            data = data[part]
        except KeyError:
            raise KeyError('{} not found in {}'.format(part, list(data.keys())))

    if isinstance(data, str):
        for line in data.split('\n'):
            print(line)
    else:
        pprint(data)


def main():
    """
    Print information from a job file
    """
    # No arguments were parsed yet, parse them now
    parser = add_parser_doc_link(get_parser(), __file__)
    args = parser.parse_args()
    fastr_cat(args.infile, args.path)

if __name__ == '__main__':
    main()
