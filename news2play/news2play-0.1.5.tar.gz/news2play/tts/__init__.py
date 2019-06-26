import logging
import os
import re
from io import BytesIO

# import pysnooper
import requests
from pydub import AudioSegment

from news2play.ssml import SSML

current_path = os.path.dirname(__file__)
logger = logging.getLogger(__name__)


class TextToSpeech:
    def __init__(self, subscription_key):
        self.cognitive_base_url = 'https://southeastasia.api.cognitive.microsoft.com'
        self.tts_base_url = 'https://southeastasia.tts.speech.microsoft.com'
        self.subscription_key = subscription_key
        self.style = 'cheerful'
        self.voice = 'en-US-GuyNeural'
        self.access_token = None
        self.ssml = SSML()

    def get_token(self):
        """
        The TTS endpoint requires an access token. This method exchanges your
        subscription key for an access token that is valid for 10 minutes.
        :return:
        """
        fetch_token_url = self.cognitive_base_url + "/sts/v1.0/issueToken"
        headers = {
            'Ocp-Apim-Subscription-Key': self.subscription_key
        }
        response = requests.post(fetch_token_url, headers=headers)
        self.access_token = str(response.text)

    # @pysnooper.snoop()
    def tts(self, txt):
        """
        Convert text to speech
        :param txt: text need to convert to speech
        :return: bytes of audio of the speech
        """
        constructed_url = self.tts_base_url + '/cognitiveservices/v1'
        headers = {
            'Authorization': 'Bearer ' + self.access_token,
            'Content-Type': 'application/ssml+xml',
            'X-Microsoft-OutputFormat': 'riff-24khz-16bit-mono-pcm',
            'User-Agent': 'YOUR_RESOURCE_NAME'
        }

        body = self.build_ssml(txt).encode('utf-8')

        logger.debug(f"SSML:\n\n{body}\n")

        response = requests.post(constructed_url, headers=headers, data=body)

        if response.status_code == 200:
            logger.info(f"Status code: {response.status_code}")
            logger.info("Your TTS is ready.")
            return response.content

        else:
            logger.error(f"Status code: {response.status_code}")
            logger.error("Something went wrong. Check your subscription key and headers.")
            return None

    def build_ssml(self, txt):
        ssml_body = self.ssml.dump(txt)

        if self.voice in ['en-US-GuyNeural', 'en-US-JessaNeural']:
            ssml_head = f'''<speak version='1.0' xmlns="https://www.w3.org/2001/10/synthesis" xmlns:mstts="http://www.w3.org/2001/mstts" xml:lang='en-US'>
            <voice name="{self.voice}"><prosody rate="slow">'''
            ssml_body = f'''<mstts:express-as type="{self.style}">''' + ssml_body + '''</mstts:express-as>'''
        else:
            ssml_head = f'''<speak version='1.0' xmlns="https://www.w3.org/2001/10/synthesis" xml:lang='en-US'>
                                    <voice  name="{self.voice}" type="{self.style}">'''

        ssml_tail = '''</prosody></voice></speak>'''

        return ssml_head + ssml_body + ssml_tail

    # @pysnooper.snoop()
    def save_audio(self, f_name, txt, audio_type='mp3'):
        """
        If tts process run successfully, the binary audio will be written
        to file in current working directory or other specify path.
        :param f_name: audio file name, or additional path ahead
        :param txt: text that will be convert to speech
        :param audio_type: the audio type
        :return:
        """
        if f_name is None or f_name.strip() == "":
            raise TypeError('Parameter file_name must not be None')

        if txt is None or txt.strip() == "":
            raise TypeError('Parameter text must not be None')

        self.__save_audio(f_name, txt, audio_type)

    def __save_audio(self, f_name, txt, audio_type):
        p = re.compile(r'\n\n', re.S)
        p_list = p.split(txt)

        audio = AudioSegment.empty()
        for paragraph in p_list:
            audio_bytes_stream = self.tts(paragraph)
            if audio_bytes_stream:
                audio += AudioSegment.from_file(BytesIO(audio_bytes_stream))

        f_name = f'{f_name}.{audio_type}'
        audio.export(f_name, format=audio_type)

        logger.info(f"Your audio of speech is saved in {f_name}.")
