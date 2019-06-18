#!/usr/bin/env python

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

"""
A small tool to wipe all .pyc files from fastr
"""
import os


def dir_list(directory):
    """
    Find all .pyc files

    :param str directory: directory to search
    :return: all .pyc files
    :rtype: list
    """
    output_list = []
    for root, _, files in os.walk(directory):
        for filename in files:
            if filename.endswith('.pyc'):
                output_list.append(os.path.abspath(os.path.join(root, filename)))
    return output_list


def main():
    """
    Main entry poitn
    """
    os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
    print("************* REMOVING .pyc FILES ***********************")
    for filename in dir_list('.'):
        os.remove(filename)
        print('removed {}'.format(filename))
    print("************* ALL .pyc FILES REMOVED ********************")


if __name__ == '__main__':
    main()
