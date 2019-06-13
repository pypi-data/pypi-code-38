# Copyright (c) Microsoft Corporation
# All rights reserved.
#
# MIT License
#
# Permission is hereby granted, free of charge,
# to any person obtaining a copy of this software and associated
# documentation files (the "Software"), to deal in the Software without restriction,
# including without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and
# to permit persons to whom the Software is furnished to do so, subject to the following conditions:
# The above copyright notice and this permission notice shall be included
# in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED *AS IS*, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING
# BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
# DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

import csv
import os
import psutil
import json
import datetime
import time
from subprocess import call, check_output
import random
import string
from .batch_command import BatchCommand

def run_batch(args):
    # TODO: 接受多个source
    # TODO: 接受对single_run函数自定义参数，以便变成更复杂的形式（比如ffmpeg）
    # '''start a new experiment'''
    # config_file_name = ''.join(random.sample(string.ascii_letters + string.digits, 8))
    # config_path = os.path.abspath(args.config)
    # if not os.path.exists(config_path):
    #     print('Please set correct config path!')
    #     exit(1)
    # else:
    #     print('Start',config_file_name)
    #     exit(0)
    if args.debug != True:
        try:
            bc = BatchCommand(command=args.command,source_dir=args.source_dir,target_dir=args.target_dir)
            print(bc.run())
        except:
            print("BatchCommand error")
            exit(1)
    else:
        bc = BatchCommand(command=args.command,source_dir=args.source_dir,target_dir=args.target_dir)
        print(bc.run())
