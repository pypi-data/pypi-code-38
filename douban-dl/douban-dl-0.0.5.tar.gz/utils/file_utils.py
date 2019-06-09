#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import threading
import time

import requests


def mkdir(path):
    if not os.path.exists(path):
        os.makedirs(path)


def save_from_url(url, headers, name, index):
    r = requests.get(url, headers=headers, stream=True)
    print("%s [%s] saving url %s, to %s" % (threading.current_thread().getName(), index, url, name))
    with open(name, 'wb') as f:
        f.write(r.content)
    time.sleep(0.5)  # slow down speed


def get_album_raw(thumb_url):
    if 'photo/m/public' in thumb_url:
        return thumb_url.replace("photo/m", "photo/l")


def get_raw_url(thumb_url):
    if 'm/public' in thumb_url:
        thumb_url = thumb_url.replace("photo/m", "photo/raw")
    if 'photo/thumb' in thumb_url:
        thumb_url = thumb_url.replace("photo/thumb", "photo/raw")
    if 'webp' in thumb_url:
        thumb_url = thumb_url.replace("webp", "jpg")
    if 'photo/lthumb' in thumb_url:
        thumb_url = thumb_url.replace("photo/lthumb", "photo/large")
    return thumb_url
