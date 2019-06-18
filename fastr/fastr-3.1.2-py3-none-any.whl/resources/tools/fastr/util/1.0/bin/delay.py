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

import sys
import time
import shutil
import random


try:
    if len(sys.argv) == 1:
        sys.argv.append('-h')

    if sys.argv[1] == '-h' or len(sys.argv) < 3:
        print('delays the execution for a random time (somewhere between 2 and 5 seconds)')
        print('usage:')
        print('    ' + sys.argv[0] + ' --in inputfile --out outputfile')
        sys.exit()

    in_index = sys.argv.index('--in') + 1
    out_index = sys.argv.index('--out') + 1

    infile = sys.argv[in_index]
    outfile = sys.argv[out_index]

    rnd = random.randint(2, 5)
    print("delay for {} seconds".format(rnd))
    time.sleep(rnd)

    shutil.copy(infile, outfile)

except KeyboardInterrupt:
    print('   ')
    print('ctrl-c detected, now exiting ... ')