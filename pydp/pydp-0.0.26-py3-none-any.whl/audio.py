#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
File: audio.py
Desc: 音频播放类
Author:yanjingang(yanjingang@mail.com)
Date: 2019/2/21 23:34
"""
import subprocess
import tempfile
import threading
import os
import wave
import logging
from ctypes import CFUNCTYPE, c_char_p, c_int, cdll
from contextlib import contextmanager
from pydub import AudioSegment

CUR_PATH = os.path.dirname(os.path.abspath(__file__))


def play(filename='', callback=None, media='', delete=False, volume=1):
    """播放声音（默认声音为报警音）"""
    if filename == '' and media == '':
        filename = CUR_PATH + '/data/media/warning.wav'
    elif media != '':
        filename = CUR_PATH + '/data/media/' + media
    #logging.info("play: "+filename)
    player = Player()
    player.play(filename, delete=delete, onCompleted=callback, volume=volume)


def get_pcm_from_wav(wav_path):
    """ 
    从 wav 文件中读取 pcm

    :param wav_path: wav 文件路径
    :returns: pcm 数据
    """
    wav = wave.open(wav_path, 'rb')
    return wav.readframes(wav.getnframes())


def convert_wav_to_mp3(wav_path):
    """ 
    将 wav 文件转成 mp3

    :param wav_path: wav 文件路径
    :returns: mp3 文件路径
    """
    if not os.path.exists(wav_path):
        logging.critical("文件错误 {}".format(wav_path))
        return None
    mp3_path = wav_path.replace('.wav', '.mp3')
    AudioSegment.from_wav(wav_path).export(mp3_path, format="mp3")
    return mp3_path


def convert_mp3_to_wav(mp3_path):
    """ 
    将 mp3 文件转成 wav

    :param mp3_path: mp3 文件路径
    :returns: wav 文件路径
    """
    target = mp3_path.replace(".mp3", ".wav")
    if not os.path.exists(mp3_path):
        logging.critical("文件错误 {}".format(mp3_path))
        return None
    AudioSegment.from_mp3(mp3_path).export(target, format="wav")
    return target


class Player(threading.Thread):
    """异步线程播放音频"""

    def __init__(self, **kwargs):
        super(Player, self).__init__(**kwargs)
        self.playing = False
        self.pipe = None
        self.delete = False
        self.volume = 1

    def run(self):
        cmd = ['play', '-v', str(self.volume), str(self.src)]
        logging.debug('Executing %s', ' '.join(cmd))

        with tempfile.TemporaryFile() as f:
            self.pipe = subprocess.Popen(cmd, stdout=f, stderr=f)
            self.playing = True
            self.pipe.wait()
            self.playing = False
            f.seek(0)
            output = f.read()
            if output:
                logging.debug("play Output was: '%s'", output)
        if self.delete and os.path.exists(self.src):
            os.remove(self.src)
        if self.onCompleted:
            self.onCompleted()

    def play(self, src, delete=False, onCompleted=None, volume=1):
        self.src = src
        self.delete = delete
        self.onCompleted = onCompleted
        self.volume = volume
        self.start()

    def play_block(self):
        self.run()

    def stop(self):
        if self.pipe:
            self.onCompleted = None
            self.pipe.kill()
            if self.delete:
                os.remove(self.src)

    def is_playing(self):
        return self.playing


if __name__ == '__main__':
    """test play wav"""
    filename = CUR_PATH + '/data/media/on.wav'

    # 播放声音
    play(filename, delete=False, callback=None)
    #play('/Users/yanjingang/project/pigrobot/data/tmp/output1559210063.wav', delete=True, callback=None)

    # 提取pcm
    pcm = get_pcm_from_wav(filename)
    # print(pcm)

    # 转换音频格式
    # convert_wav_to_mp3(filename)
