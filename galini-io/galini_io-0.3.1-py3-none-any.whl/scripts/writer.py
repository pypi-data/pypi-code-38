# Copyright 2018 Francesco Ceccon
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
"""Writes message to the specified file."""
from argparse import ArgumentParser
import datetime
import time
from galini_io.writer import MessageWriter
from galini_io.message import text_message


def main():
    parser = ArgumentParser()
    parser.add_argument('filename')
    args = parser.parse_args()

    with open(args.filename, 'wb') as f:
        writer = MessageWriter(f)

        while True:
            msg = text_message('test_writer', '0', 'NOW = {}'.format(datetime.datetime.utcnow()))
            writer.write(msg)
            time.sleep(1)
