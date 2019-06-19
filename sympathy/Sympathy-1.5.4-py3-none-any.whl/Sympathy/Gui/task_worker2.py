# This file is part of Sympathy for Data.
# Copyright (c) 2016 Combine Control Systems AB
#
# Sympathy for Data is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Sympathy for Data is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Sympathy for Data.  If not, see <http://www.gnu.org/licenses/>.
from __future__ import absolute_import, unicode_literals, print_function
import logging
import os
import collections
import signal
import json
import base64
import threading
import psutil
import time
import six


core_logger = logging.getLogger('core')
(NEW_TASK, NEW_QUIT_TASK, UPDATE_TASK, QUIT_TASK, ABORT_TASK,
 DONE_TASK, SET_WORKERS_TASK) = range(7)


def readlines_fd(fd, bufl):
    return datalines(os.read(fd, 2048), bufl)


IOBundle = collections.namedtuple(
    'IOBundle', ['port', 'input_func', 'output_func', 'result_func'])


def killer(ppid):
    while True:
        if not psutil.pid_exists(ppid):
            os.kill(os.getpid(), signal.SIGTERM)
        time.sleep(0.2)


def worker_twisted(function, port, ppid):
    ipipebuf = []
    taskid = -1
    signal.signal(signal.SIGINT, signal.SIG_IGN)

    def get_msgs():
        lines = readlines_fd(0, ipipebuf)
        return [decode_json(line) for line in lines]

    def output_result(msg):
        return encode_json([taskid, DONE_TASK, msg.to_dict()]) + b'\n'

    def output_update(msg):
        return encode_json([taskid, UPDATE_TASK, msg.to_dict()]) + b'\n'

    def input_update(line):
        return decode_json(line)[2]

    killer_thread = threading.Thread(target=killer, args=(ppid,))
    killer_thread.daemon = True
    killer_thread.start()

    args = (0,)
    kwargs = {'mode': 'rb'}
    if six.PY2:
        args = (0, 'rb')
        kwargs = {}

    with os.fdopen(*args, **kwargs) as msg_in:

        while True:
            msg = decode_json(msg_in.readline().rstrip())
            taskid_new, cmd, data = msg
            if cmd in [NEW_TASK, NEW_QUIT_TASK]:
                taskid = taskid_new
                io_bundle = IOBundle(
                    port, input_update, output_update, output_result)
                function(io_bundle, *data)
            else:
                assert False


def datalines(data, bufl):
    i = data.rfind(b'\n')
    if i >= 0:
        bufl.append(data[:i])
        sdata = b''.join(bufl)
        bufl[:] = [data[i + 1:]]
        lines = sdata.split(b'\n')
        return [line.strip() for line in lines]
    else:
        bufl.append(data)
    return []


def get_msgs(lines):
    return [decode_json(line) for line in lines]


def decode_json(str_):
    return json.loads(base64.b64decode(str_).decode('ascii'))


def encode_json(dict_):
    return base64.b64encode(json.dumps(dict_).encode('ascii'))


def main():
    import argparse
    from Gui import task_worker_subprocess
    from Gui import log
    task_worker_subprocess.set_high_dpi_unaware()

    parser = argparse.ArgumentParser()
    parser.add_argument('port', type=int)
    parser.add_argument('parent_pid', type=int)
    parser.add_argument('loglevel', type=int)
    parser.add_argument('node_loglevel', type=int)
    (parsed, _) = parser.parse_known_args()
    log.setup_loglevel(parsed.loglevel, parsed.node_loglevel)

    worker_twisted(
        task_worker_subprocess.worker, parsed.port, parsed.parent_pid)


if __name__ == '__main__':
    main()
