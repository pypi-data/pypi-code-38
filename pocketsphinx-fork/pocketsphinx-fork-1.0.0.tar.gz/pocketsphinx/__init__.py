# Copyright (c) 1999-2016 Carnegie Mellon University. All rights
# reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
#
# 1. Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
#
# 2. Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in
#    the documentation and/or other materials provided with the
#    distribution.
#
# This work was supported in part by funding from the Defense Advanced
# Research Projects Agency and the National Science Foundation of the
# United States of America, and the CMU Sphinx Speech Consortium.
#
# THIS SOFTWARE IS PROVIDED BY CARNEGIE MELLON UNIVERSITY ``AS IS'' AND
# ANY EXPRESSED OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO,
# THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
# PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL CARNEGIE MELLON UNIVERSITY
# NOR ITS EMPLOYEES BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
# THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
import glob
import io
import lzma
import os
import sys
import shutil
import signal
import tarfile
import urllib.request
from contextlib import contextmanager
from sphinxbase import *
from .pocketsphinx import *


DefaultConfig = Decoder.default_config


def get_model_path():
    """ Return path to the model. """
    return os.path.join(os.path.dirname(__file__), 'model')


def get_data_path():
    """ Return path to the data. """
    return os.path.join(os.path.dirname(__file__), 'data')

class PocketsphinxModel():

    def __init__(self, model_path=None):
        if model_path is None:
            self.model_path = os.path.expanduser('~') + '/pocketsphinx_models'
        else:
            self.model_path = model_path

    def install_model(self, url, abbr, replace=False):
        model_dir = f'{self.model_path}/model/{abbr}/'
        if os.path.isdir(model_dir+abbr):
            if replace:
                self.remove_model(abbr)
            else:
                raise ValueError(
                    f'''
                    Model with name {abbr} already installed under {model_dir+abbr}.
                    You can remove it using remove_model("{abbr}") or passing replace=True
                    '''
                )
        with urllib.request.urlopen(url) as response:
            file = tarfile.open(
                fileobj=io.BytesIO(lzma.decompress(response.read()))
            )
        os.makedirs(model_dir+abbr)
        file.extractall()
        model_name = file.members[0].name
        paths = glob.glob(f'{model_name}/model_parameters/**')
        paths.sort()
        param_files = os.listdir(paths[0])
        acoustic_parameters_directory = model_dir+abbr
        for f in param_files:
            shutil.move(paths[0]+'/'+f, acoustic_parameters_directory)
        language_model_file = model_dir+abbr+'.lm.bin'
        shutil.move(glob.glob(f'{model_name}/etc/*.lm.bin')[0], language_model_file)
        phoneme_dictionary_file = model_dir+'default.dic'
        shutil.move(glob.glob(f'{model_name}/etc/*.dic')[0], phoneme_dictionary_file)
        shutil.rmtree(f'{model_name}')

    def remove_model(self, abbr):
        shutil.rmtree(f'{self.model_path}/model/{abbr}/')
        
    def get_model(self, abbr):
        model_dir = f'{self.model_path}/model/{abbr}/'
        if os.path.isdir(model_dir+abbr):
            acoustic_parameters_directory = model_dir+abbr
            language_model_file = glob.glob('{}*.lm.bin'.format(model_dir))[0]
            phoneme_dictionary_file = (glob.glob('{}*.dic'.format(model_dir))+glob.glob('{}*.dict'.format(model_dir)))[0]
            return {
                'hmm': acoustic_parameters_directory,
                'lm': language_model_file,
                'dict': phoneme_dictionary_file
            }
        else:
            raise ValueError(
                f'Model with name {abbr} does not seem to be installed under {model_dir+abbr}.'
            )

class Pocketsphinx(Decoder):

    def __init__(self, **kwargs):
        model_path = get_model_path()

        if kwargs.get('model') is not None:
            model_dict = kwargs.pop('model')
            kwargs['hmm']  = model_dict['hmm']
            kwargs['lm']   = model_dict['lm']
            kwargs['dict'] = model_dict['dict']
        else:
            if kwargs.get('dic') is not None and kwargs.get('dict') is None:
                kwargs['dict'] = kwargs.pop('dic')
            if kwargs.get('hmm') is None:
                kwargs['hmm'] = os.path.join(model_path, 'en-us')
            if kwargs.get('lm') is None:
                kwargs['lm'] = os.path.join(model_path, 'en-us.lm.bin')
            if kwargs.get('dict') is None:
                kwargs['dict'] = os.path.join(model_path, 'cmudict-en-us.dict')

        if kwargs.pop('verbose', False) is False:
            if sys.platform.startswith('win'):
                kwargs['logfn'] = 'nul'
            else:
                kwargs['logfn'] = '/dev/null'

        config = DefaultConfig()

        for key, value in kwargs.items():
            if isinstance(value, bool):
                config.set_boolean('-{}'.format(key), value)
            elif isinstance(value, int):
                config.set_int('-{}'.format(key), value)
            elif isinstance(value, float):
                config.set_float('-{}'.format(key), value)
            elif isinstance(value, str):
                config.set_string('-{}'.format(key), value)

        super(Pocketsphinx, self).__init__(config)

    def __str__(self):
        return self.hypothesis()

    @contextmanager
    def start_utterance(self):
        self.start_utt()
        yield
        self.end_utt()

    @contextmanager
    def end_utterance(self):
        self.end_utt()
        yield
        self.start_utt()

    def decode(self, audio_file, buffer_size=2048,
               no_search=False, full_utt=False):
        buf = bytearray(buffer_size)

        with open(audio_file, 'rb') as f:
            with self.start_utterance():
                while f.readinto(buf):
                    self.process_raw(buf, no_search, full_utt)
        return self

    def segments(self, detailed=False):
        if detailed:
            return [
                (s.word, s.prob, s.start_frame, s.end_frame)
                for s in self.seg()
            ]
        else:
            return [s.word for s in self.seg()]

    def hypothesis(self):
        hyp = self.hyp()
        if hyp:
            return hyp.hypstr
        else:
            return ''

    def probability(self):
        hyp = self.hyp()
        if hyp:
            return hyp.prob

    def score(self):
        hyp = self.hyp()
        if hyp:
            return hyp.best_score

    def best(self, count=10):
        return [
            (h.hypstr, h.score)
            for h, i in zip(self.nbest(), range(count))
        ]

    def confidence(self):
        hyp = self.hyp()
        if hyp:
            return self.get_logmath().exp(hyp.prob)


class AudioFile(Pocketsphinx):

    def __init__(self, **kwargs):
        signal.signal(signal.SIGINT, self.stop)

        self.audio_file = kwargs.pop('audio_file', None)
        self.buffer_size = kwargs.pop('buffer_size', 2048)
        self.no_search = kwargs.pop('no_search', False)
        self.full_utt = kwargs.pop('full_utt', False)

        self.keyphrase = kwargs.get('keyphrase')

        self.in_speech = False
        self.buf = bytearray(self.buffer_size)

        super(AudioFile, self).__init__(**kwargs)

        self.f = open(self.audio_file, 'rb')

    def __iter__(self):
        with self.f:
            with self.start_utterance():
                while self.f.readinto(self.buf):
                    self.process_raw(self.buf, self.no_search, self.full_utt)
                    if self.keyphrase and self.hyp():
                        with self.end_utterance():
                            yield self
                    elif self.in_speech != self.get_in_speech():
                        self.in_speech = self.get_in_speech()
                        if not self.in_speech and self.hyp():
                            with self.end_utterance():
                                yield self

    def stop(self, *args, **kwargs):
        raise StopIteration


class StreamSpeech(Pocketsphinx):

    def __init__(self, **kwargs):
        signal.signal(signal.SIGINT, self.stop)

        self.buffer_size = kwargs.pop('buffer_size', 2048)
        self.no_search = kwargs.pop('no_search', False)
        self.full_utt = kwargs.pop('full_utt', False)

        self.keyphrase = kwargs.get('keyphrase')

        self.in_speech = False
        self.buf = bytearray(self.buffer_size)

        self.callback = kwargs.pop('callback')

        super(StreamSpeech, self).__init__(**kwargs)

    def __iter__(self):
        with self.start_utterance():
            self.buf = self.callback()
            while self.buf:
                self.process_raw(self.buf, self.no_search, self.full_utt)
                if self.keyphrase and self.hyp():
                    with self.end_utterance():
                        yield self
                elif self.in_speech != self.get_in_speech():
                    self.in_speech = self.get_in_speech()
                    if not self.in_speech and self.hyp():
                        with self.end_utterance():
                            yield self
                self.buf = self.callback()

    def stop(self, *args, **kwargs):
        raise StopIteration


class LiveSpeech(Pocketsphinx):

    def __init__(self, **kwargs):
        signal.signal(signal.SIGINT, self.stop)

        self.audio_device = kwargs.pop('audio_device', None)
        self.sampling_rate = kwargs.pop('sampling_rate', 16000)
        self.buffer_size = kwargs.pop('buffer_size', 2048)
        self.no_search = kwargs.pop('no_search', False)
        self.full_utt = kwargs.pop('full_utt', False)

        self.keyphrase = kwargs.get('keyphrase')

        self.in_speech = False
        self.buf = bytearray(self.buffer_size)
        self.ad = Ad(self.audio_device, self.sampling_rate)

        super(LiveSpeech, self).__init__(**kwargs)

    def __iter__(self):
        with self.ad:
            with self.start_utterance():
                while self.ad.readinto(self.buf) >= 0:
                    self.process_raw(self.buf, self.no_search, self.full_utt)
                    if self.keyphrase and self.hyp():
                        with self.end_utterance():
                            yield self
                    elif self.in_speech != self.get_in_speech():
                        self.in_speech = self.get_in_speech()
                        if not self.in_speech and self.hyp():
                            with self.end_utterance():
                                yield self

    def stop(self, *args, **kwargs):
        raise StopIteration
