__author__ = "Altertech Group, https://www.altertech.com/"
__copyright__ = "Copyright (C) 2018 Altertech Group"
__license__ = "Apache License 2.0"
__version__ = "0.0.1"
__doc__ = """
TTS provider for Google Cloud TTS

Key: JSON service account key

Options:
    pitch: pitch (default: 0)
    rate: speaking rate (default: 1.0)
    lang: language (default: en-US)
    voice: tts voice (default: en-US-Wavenet-A)
"""
__id__ = 'gcloud'

import requests
import base64
import soundfile
import io
import time
import oauth2client.service_account as oa2s


class TTSProvider(object):

    def __init__(self):
        self.__id = __id__
        self.default_voice = 'en-US-Wavenet-A'
        self.default_lang = 'en-US'
        self.access_token = None
        self.access_token_expires = 0

    def generate_audio(self, text, key, **kwargs):
        if not self.access_token or self.access_token_expires < time.time():
            # obtain new access token
            scope = 'https://www.googleapis.com/auth/cloud-platform'
            c = oa2s.ServiceAccountCredentials.from_json_keyfile_dict(
                key, scope)
            token = c.get_access_token()
            self.access_token = token.access_token
            # set cached token expiration, substract 10 seconds to keep it safe
            self.access_token_expires = time.time() + token.expires_in - 10
        req_headers = {"Authorization": "Bearer %s" % self.access_token}
        req_data = {
            'audioConfig': {
                'audioEncoding': 'LINEAR16',
                'pitch': str(kwargs.get('pitch', 0.0)),
                'speakingRate': str(kwargs.get('rate', 1.0))
            },
            'input': {
                'text': text
            },
            'voice': {
                'languageCode': kwargs.get('lang', self.default_lang),
                'name': kwargs.get('voice', self.default_voice)
            }
        }
        r = requests.post(
            'https://texttospeech.googleapis.com/v1beta1/text:synthesize',
            json=req_data,
            headers=req_headers)
        if r.status_code != 200:
            raise Exception(
                'Cloud server error response code %u' % r.status_code)
        raw = base64.b64decode(r.json()['audioContent'])
        data, rate = soundfile.read(io.BytesIO(raw))
        return data, rate
