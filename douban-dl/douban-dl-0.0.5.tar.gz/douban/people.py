#!/usr/bin/env python3
# -*- coding:utf-8 -*-
import re

import requests


class People:
    BASE_URL = 'https://www.douban.com/people/'

    def __init__(self, user_id):
        self.uid = user_id
        self.url = People.BASE_URL + '{}/photos?start='.format(user_id)

    def albums(self):
        start = 0
        while True:
            next_albums = self.__album(start)
            step = len(next_albums)
            if 0 == step:
                break
            for album_id in next_albums:
                yield album_id
            start += step

    def __album(self, start):
        headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.6,en;q=0.4',
            'Connection': 'keep-alive',
            'DNT': '1',
            'HOST': 'www.douban.com',
            'Referer': People.BASE_URL + self.uid,
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36'
        }
        url = self.url + str(start)
        r = requests.get(url, headers=headers)
        album_urls = re.findall(r'https?://www.douban.com/photos/album/(\d+)', r.text)
        return set(album_urls)


if __name__ == '__main__':
    lordbean = People('LordBean')
    for album_id in lordbean.albums():
        print(album_id)
