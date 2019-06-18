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
import os
import fastr
from fastr.helpers.report import print_job_result
from fastr.utils.cmd import add_parser_doc_link
FASTR_LOG_TYPE = 'none'  # Do not get info about fastr


def get_parser():
    parser = argparse.ArgumentParser(
        description="Print a report of a job result file."
    )
    parser.add_argument('job', metavar='JOBFILE', nargs='?', type=str,
                        help='File of the job to execute (default ./__fastr_command__.pickle.gz)')
    return parser


def main():
    """
    Print report of a job result (__fastr_result__.pickle.gz) file
    """
    # No arguments were parsed yet, parse them now
    parser = add_parser_doc_link(get_parser(), __file__)
    args = parser.parse_args()

    job = args.job

    if job is None:
        curdir_contents = os.listdir('.')

        if '__fastr_result__.pickle.gz' in curdir_contents:
            job = '__fastr_result__.pickle.gz'
        else:
            fastr.log.critical('No job given and cannot find __fastr_result__.pickle.gz in current directory!')
            exit()

    print_job_result(job)


if __name__ == '__main__':
    main()
