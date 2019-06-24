__author__ = "Altertech Group, https://www.altertech.com/"
__copyright__ = "Copyright (C) 2018 Altertech Group"
__license__ = "Apache License 2.0"
__version__ = "0.0.1"

__doc__ = """
TTS provider for IBM Watson TTS

Key: JSON credentials (username/password)

Options:
    voice: tts voice (default: en-US_AllisonVoice)
"""
__id__ = 'watson'

import requests
import soundfile
import io


class TTSProvider(object):

    def __init__(self):
        self.__id = __id__
        self.default_voice = 'en-US_AllisonVoice'

    def generate_audio(self, text, key, **kwargs):
        req_headers = {'Accept': 'audio/wav'}
        req_data = {
            'text': text,
        }
        r = requests.post(
            'https://stream.watsonplatform.net/text-to-speech/api/v1/' + \
                'synthesize?voice=%s' % kwargs.get('voice', self.default_voice),
            json=req_data,
            auth=(key['username'], key['password']),
            headers=req_headers)
        if r.status_code != 200:
            raise Exception(
                'Cloud server error response code %u' % r.status_code)
        data, rate = soundfile.read(io.BytesIO(r.content))
        return data, rate
