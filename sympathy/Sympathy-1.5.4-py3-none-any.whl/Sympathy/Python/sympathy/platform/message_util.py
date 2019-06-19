# Copyright (c) 2016, Combine Control Systems AB
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#     * Redistributions of source code must retain the above copyright
#       notice, this list of conditions and the following disclaimer.
#     * Redistributions in binary form must reproduce the above copyright
#       notice, this list of conditions and the following disclaimer in the
#       documentation and/or other materials provided with the distribution.
#     * Neither the name of the Combine Control Systems AB nor the
#       names of its contributors may be used to endorse or promote products
#       derived from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED.
# IN NO EVENT SHALL COMBINE CONTROL SYSTEMS AB BE LIABLE FOR ANY
# DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
from __future__ import (print_function, division, unicode_literals,
                        absolute_import)
import base64
import json
from PySide import QtCore
from . import message


class QtMessageReader(QtCore.QObject):
    received = QtCore.Signal(list)

    def __init__(self, qiodev, parent=None):
        super(QtMessageReader, self).__init__(parent=parent)
        self._buf = [b'']
        self._qiodev = qiodev
        qiodev.readyRead.connect(self._read)

    def _read(self):
        msgs = self.read()
        if msgs:
            self.received.emit(msgs)

    def read(self):
        data = self._qiodev.readAll().data()
        lines = datalines(data, self._buf)
        elems = [decode_json(line) for line in lines]
        msgs = [message.from_dict(elem[2]) for elem in elems]
        return msgs

    def wait(self, time):
        self._qiodev.waitForReadyRead(time)

    def set_block(self, state):
        self._block = self._qiodev.blockSignals(state)


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
