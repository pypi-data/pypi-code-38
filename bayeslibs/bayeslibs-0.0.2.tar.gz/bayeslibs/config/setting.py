# conding=utf-8
"""
@project:edubalibs
@language:Python3
@create:2019/5/30
@author:qianyang<qianyang@aibayes.com>
@description:none
"""
from bayeslibs.config import const
import configparser
from bayeslibs.utils.pattern.code_design import singleton
import os

HEAR = os.path.abspath(os.path.dirname(__file__))
ROOM_MAP = {'电教室': [10.759, -3.156], '财务室': [10.759, -3.156], '出发点': [1.367, -0.361]}
MAX_DISTANCE = 10
APOLLO_PNO = 'Apollo T200'
APOLLO_USER = 'UserInfo'
APOLLO_INI_PATH = os.path.join(HEAR, const.APOLLO_INI)


class IniFileParser:
    def __init__(self):
        self.config = configparser.ConfigParser()

    def write(self, file_path, section, **kwargs):
        if not section or not kwargs:
            print('input in illegal')
            return
        try:
            self.config.add_section(section) if section not in self.config.sections() else None
            for item, value in kwargs.items():
                self.config.set(section, item, value)
            self.config.write(open(file_path, 'w', encoding='utf-8'))
        except Exception as err:
            print('Some unexpected error happen:{}'.format(err))

    def get(self, section, option):
        try:
            value_ = self.config.get(section, option)
            return value_
        except Exception as err:
            print('Some unexpected error happen:{}'.format(err))
            return None

    def set(self, section, option, value=None):
        try:
            self.config.set(section, option, value)
            return True
        except Exception as err:
            print('Some unexpected error happen:{}'.format(err))
            return None

    def close(self):
        self.config.clear()

    def open(self, file_path):
        self.config.read(file_path)


@singleton
class ApolloConfig:

    def __init__(self):
        self.ini_parser = IniFileParser()
        self.ini_parser.open(APOLLO_INI_PATH)
        self.ip = self.ini_parser.get(APOLLO_PNO, const.IP)
        self.port = self.ini_parser.get(APOLLO_PNO, const.PORT)
        self.apollo_url = 'http://{}:{}'.format(self.ip, self.port)
        self.uid = self.ini_parser.get(APOLLO_USER, const.UID)

    def set_apollo_url(self, ip, port):
        self.apollo_url = 'http://{}:{}'.format(ip, port)
        self.ini_parser.write(APOLLO_INI_PATH, APOLLO_PNO, ip=str(ip), port=str(port))

    def get_apollo_url(self):
        return self.apollo_url

    def get_uid(self):
        return self.uid

    def get_motion_rotate_url(self):
        return '{}/bayes/motion/rotate'.format(self.apollo_url)

    def get_motion_move_url(self):
        return '{}/bayes/motion/move'.format(self.apollo_url)

    def get_motion_map_url(self):
        return '{}/bayes/map/save'.format(self.apollo_url)

    def get_motion_nav_url(self):
        return '{}/bayes/navigate'.format(self.apollo_url)

    def get_voice_wts_url(self):
        return '{}/bayes/voice/wts'.format(self.apollo_url)

    def get_voice_tts_url(self):
        return '{}/bayes/voice/tts'.format(self.apollo_url)

    def get_voice_asr_url(self):
        return '{}/bayes/voice/asr'.format(self.apollo_url)

    def get_voice_acr_url(self):
        return '{}/bayes/voice/casr'.format(self.apollo_url)

    def get_voice_chat_url(self):
        return '{}/bayes/voice/chat'.format(self.apollo_url)

    def get_voice_music_url(self):
        return '{}/bayes/voice/music'.format(self.apollo_url)

    def get_vision_object_detect_url(self):
        return '{}/bayes/vision/object_detect'.format(self.apollo_url)

    def get_vision_distance_detect_url(self):
        return '{}/bayes/vision/distance_detect'.format(self.apollo_url)

    def get_vision_color_recog_url(self):
        return '{}/bayes/vision/color_recog'.format(self.apollo_url)

    def get_vision_face_detect_url(self):
        return '{}/bayes/vision/face_detect'.format(self.apollo_url)

    def get_vision_face_recog_url(self):
        return '{}/bayes/vision/face_recog'.format(self.apollo_url)

    def get_vision_age_gender_recog_url(self):
        return '{}/bayes/vision/age_gender_recog'.format(self.apollo_url)

    def get_vision_emotion_recog_url(self):
        return '{}/bayes/vision/emotion_recog'.format(self.apollo_url)

    def get_vision_headpose_recog_url(self):
        return '{}/bayes/vision/headpose_recog'.format(self.apollo_url)

    def get_vision_beauty_recog_url(self):
        return '{}/bayes/vision/beauty_recog'.format(self.apollo_url)

    def get_vision_handpose_recog_url(self):
        return '{}/bayes/vision/handpose_recog'.format(self.apollo_url)

    def get_vision_skeleton_recog_url(self):
        return '{}/bayes/vision/skeleton_recog'.format(self.apollo_url)
