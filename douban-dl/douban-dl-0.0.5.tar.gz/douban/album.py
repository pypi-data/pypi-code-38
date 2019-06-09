#!/usr/bin/env python3
# -*- coding:utf-8 -*-
import os

import requests
from bs4 import BeautifulSoup

from douban import threadPoolExecutor
from utils import file_utils
from utils.file_utils import get_album_raw


class Album:
    BASE_URL = "https://www.douban.com/photos/album/"

    def __init__(self, album_id):
        self.url = Album.BASE_URL + album_id + "/?m_start="

    def photos(self):
        start = 0
        while True:
            next_photos = self.__photos(start)
            step = len(next_photos)
            if 0 == step:
                break
            for photo in next_photos:
                yield get_album_raw(photo.img["src"])
            start += step

    def __photos(self, start):
        url = self.url + str(start)
        r = requests.get(url)
        soup = BeautifulSoup(r.text, "html.parser")
        return soup.find_all("div", class_="photo_wrap")


headers = {
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
    "accept-encoding": "gzip, deflate, br",
    "accept-language": "zh-CN,zh;q=0.8,en-US;q=0.6,en;q=0.4",
    "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.104 Safari/537.36",
    "cache-control": "max-age=0"
}


def get_album(album, path):
    idx = 0
    file_utils.mkdir(path)
    for photo_url in album.photos():
        name = os.path.basename(photo_url)
        full_path = path + '/' + name
        if os.path.exists(full_path):
            print('pic {} exist skip'.format(name))
            continue
        # print("{}: submit {}".format(idx, name))
        threadPoolExecutor.submit(file_utils.save_from_url, url=photo_url, headers=headers, name=full_path, index=idx)
        # file_utils.save_from_url(photo_url, headers, path + '/' + name)
        idx += 1
    print("saving album to {}, total {} images".format(path, idx))


def get_album_by_id(album_id, path):
    print("saving album {} to {}".format(album_id, path))
    album = Album(album_id)
    get_album(album, path)
