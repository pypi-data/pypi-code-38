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

import argparse
import json


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Subtract one number from another')
    parser.add_argument('--in1', metavar='IN1', dest='in1', type=float, nargs='+', required=True, help='First number')
    parser.add_argument('--in2', metavar='IN2', dest='in2', type=float, nargs='+', required=True, help='Second number')

    args = parser.parse_args()

    if len(args.in1) != len(args.in2):
        raise ValueError("Number of value in each argument should match!")

    result = [x - y for x, y in zip(args.in1, args.in2)]

    print('RESULT={}'.format(json.dumps(result)))
