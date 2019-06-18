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
"""Copy solver output to new folder."""
import sys
import time
from pathlib import Path
import shutil
from argparse import ArgumentParser
from galini_io.logging import RootLogger
from galini_io.reader import MessageReader
from galini_io.writer import MessageWriter


def create_output_directory(directory):
    directory = Path(directory)
    if not directory.exists():
        directory.mkdir(exist_ok=True)
    else:
        raise RuntimeError('Directory "%s" already exists.' % directory)


def copy_data_hdf5(directory, output_directory):
    """Copy the data.hdf5 file to `output_directory`."""
    in_data_file = Path(directory) / 'data.hdf5'
    out_data_file = Path(output_directory) / 'data.hdf5'
    shutil.copy(str(in_data_file), str(out_data_file))


def copy_messages(reader, writer, speed=1.0):
    previous_timestamp = None
    for msg in reader:
        if previous_timestamp:
            time_diff = msg.timestamp - previous_timestamp
            time.sleep(time_diff / (1000.0 * speed))

        previous_timestamp = msg.timestamp
        print(msg)
        writer.write(msg)


def main():
    parser = ArgumentParser()
    parser.add_argument('directory')
    parser.add_argument('output_directory')
    parser.add_argument('--speed', type=float, default=1.0)
    args = parser.parse_args()

    in_filename = Path(args.directory) / 'messages.bin'
    out_filename = Path(args.output_directory) / 'messages.bin'
    try:
        create_output_directory(args.output_directory)
        copy_data_hdf5(args.directory, args.output_directory)

        with open(in_filename, 'rb') as in_f:
            with open(out_filename, 'wb') as out_f:
                reader = MessageReader(in_f, stream=False)
                writer = MessageWriter(out_f)
                copy_messages(reader, writer, speed=args.speed)
    except Exception as ex:
        print(ex)
        sys.exit(1)
