__author__ = "Altertech Group, https://www.altertech.com/"
__copyright__ = "Copyright (C) 2018 Altertech Group"
__license__ = "Apache License 2.0"
__version__ = "0.0.1"
__doc__ = """
TTS provider for Amazon AWS TTS (Polly)

Key: must contain aws_access_key_id, aws_secret_access_key and region_name

Options:
    voice: tts voice (default: Joanna)
"""
__id__ = 'polly'

import boto3
import numpy as np


class TTSProvider(object):

    def __init__(self):
        self.__id = __id__
        self.default_voice = 'Joanna'

    def generate_audio(self, text, key, **kwargs):
        k = key['aws_access_key_id']
        sec = key['aws_secret_access_key']
        region = key['region_name']
        rate = 16000
        client = boto3.Session(
            aws_access_key_id=k, aws_secret_access_key=sec,
            region_name=region).client('polly')
        r = client.synthesize_speech(
            VoiceId=kwargs.get('voice', self.default_voice),
            OutputFormat='pcm',
            Text=text,
            SampleRate=str(rate))
        raw = r['AudioStream'].read()
        data = np.fromstring(raw, 'Int16')
        return data.astype(np.float64, order='C') / 32768.0, rate
