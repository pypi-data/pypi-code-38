#!/usr/bin/env python3
# -*- coding:utf-8 -*-
import os

import requests
from bs4 import BeautifulSoup

from douban import threadPoolExecutor
from utils import file_utils
from utils.file_utils import get_raw_url


class Celebrity:
    BASE_URL = "https://movie.douban.com/celebrity/{}/photos/"

    def __init__(self, celebrity_id):
        self.url = Celebrity.BASE_URL.format(celebrity_id)

    def photos(self):
        start = 0
        while True:
            next_photos = self.__photos(start)
            step = len(next_photos)
            if 0 == step:
                break
            for photo in next_photos:
                # https://img3.doubanio.com/view/photo/thumb/public/p2156276775.jpg
                # https://img3.doubanio.com/view/photo/raw/public/p2156276775.jpg
                # https://img3.doubanio.com/view/photo/photo/public/p2156276775.webp
                # src https://img3.doubanio.com/view/photo/m/public/p2179264053.webp
                yield photo.a['href'], get_raw_url(photo.img['src'])
            start += step

    def __photos(self, start):
        params = {
            "type": "C",
            "start": start,
            "sortby": "like",
            "size": "a",
            "subtype": "a"
        }
        header = {
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36'
        }
        r = requests.get(self.url, params=params, headers=header)
        soup = BeautifulSoup(r.text, "html.parser")
        return soup.find_all("div", class_="cover")


def get_celebrity(celebrity, path):
    idx = 0
    file_utils.mkdir(path)
    for refer, photo_url in celebrity.photos():
        name = os.path.basename(photo_url)
        full_path = path + '/' + name
        if os.path.exists(full_path):
            print('pic {} exist skip'.format(name))
            continue
        # print("{}: saving {}".format(idx, name))
        headers = {
            "Referer": refer,
            "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.104 Safari/537.36"
        }
        threadPoolExecutor.submit(file_utils.save_from_url, url=photo_url, headers=headers, name=full_path, index=idx)
        # file_utils.save_from_url(photo_url, headers, path + '/' + name)
        idx += 1

    print("Finish parsing celebrity pages, all file will save to {}".format(path))


def get_celebrity_by_id(cid, path):
    c = Celebrity(cid)
    get_celebrity(c, path)


if __name__ == "__main__":
    celebrity_id = "1335340"
    celebrity = Celebrity(celebrity_id)
    path = os.path.expanduser("~") + "/Pictures/celebrity/" + celebrity_id
    get_celebrity(celebrity, path)
