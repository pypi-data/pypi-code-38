#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os

import requests
from bs4 import BeautifulSoup

from douban import threadPoolExecutor
from utils import file_utils
from utils.file_utils import get_raw_url, mkdir


class Movie:
    BASE_URL = 'https://movie.douban.com/subject/{}/photos'

    def __init__(self, movie_id):
        self.url = Movie.BASE_URL.format(movie_id)

    def photos(self):
        start = 0
        while True:
            next_photos = self.__photos(start)
            step = len(next_photos)
            if 0 == step:
                break
            for photo in next_photos:
                yield photo.a['href'], get_raw_url(photo.img['src'])
            start += step

    def __photos(self, start):
        url = self.url
        params = {
            'type': 'S',
            'start': start,
            'sortby': 'like',
            'size': 'a',
            'subtype': 'a'
        }
        headers = {
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36'
        }
        r = requests.get(url, params=params, headers=headers)
        soup = BeautifulSoup(r.text, "html.parser")
        return soup.find_all("div", class_="cover")


def get_movie_by_id(mid, path):
    idx = 0
    mkdir(path)
    m = Movie(mid)
    for refer, photo_url in m.photos():
        name = os.path.basename(photo_url)
        full_path = path + '/' + name
        if os.path.exists(full_path):
            print('pic {} exist skip'.format(name))
            continue
        # print('{}: saving {}'.format(idx, name))
        headers = {
            'Referer': refer,
            "User-Agent": 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36'
        }
        # file_utils.save_from_url(photo_url, headers, full_path)
        threadPoolExecutor.submit(file_utils.save_from_url, url=photo_url, headers=headers, name=full_path, index=idx)
        idx += 1
    print('saving movie photos to {}'.format(path))


if __name__ == '__main__':
    get_movie_by_id('4191644', '/home/mi/Pictures/419')
