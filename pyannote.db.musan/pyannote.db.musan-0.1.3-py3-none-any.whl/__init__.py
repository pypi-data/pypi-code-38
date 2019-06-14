#!/usr/bin/env python
# encoding: utf-8

# The MIT License (MIT)

# Copyright (c) 2018 CNRS

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

# AUTHORS
# Hervé BREDIN - http://herve.niderb.fr


from ._version import get_versions
__version__ = get_versions()['version']
del get_versions


from pathlib import Path
from pyannote.database import Database
from pyannote.database.protocol import CollectionProtocol


class BackgroundNoise(CollectionProtocol):

    def files_iter(self):
        data_dir = Path(__file__).resolve().parent / 'data'
        with open(data_dir / 'background_noise.txt', mode='r') as fp:
            for line in fp:
                uri = line.strip()
                yield {'database': 'MUSAN', 'uri': uri}

class Noise(CollectionProtocol):

    def files_iter(self):
        data_dir = Path(__file__).resolve().parent / 'data'
        with open(data_dir / 'noise.txt', mode='r') as fp:
            for line in fp:
                uri = line.strip()
                yield {'database': 'MUSAN', 'uri': uri}

class Music(CollectionProtocol):

    def files_iter(self):
        data_dir = Path(__file__).resolve().parent / 'data'
        with open(data_dir / 'music.txt', mode='r') as fp:
            for line in fp:
                uri = line.strip()
                yield {'database': 'MUSAN', 'uri': uri}

class Speech(CollectionProtocol):

    def files_iter(self):
        data_dir = Path(__file__).resolve().parent / 'data'
        with open(data_dir / 'speech.txt', mode='r') as fp:
            for line in fp:
                uri = line.strip()
                yield {'database': 'MUSAN', 'uri': uri}

class MUSAN(Database):
    """MUSAN database"""

    def __init__(self, preprocessors={}, **kwargs):
        super(MUSAN, self).__init__(preprocessors=preprocessors, **kwargs)

        self.register_protocol(
            'Collection', 'BackgroundNoise', BackgroundNoise)

        self.register_protocol(
            'Collection', 'Noise', Noise)

        self.register_protocol(
            'Collection', 'Music', Music)

        self.register_protocol(
            'Collection', 'Speech', Speech)
