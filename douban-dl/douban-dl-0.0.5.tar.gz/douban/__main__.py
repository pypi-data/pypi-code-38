#!/usr/bin/env python
# -*- coding: utf-8 -*-
import argparse
import os
import re

from douban.album import get_album_by_id
from douban.celebrity import get_celebrity_by_id
from douban.movie import get_movie_by_id
from douban.people import People


def get_args():
    """
    argparse 选项的默认语法是基于 Unix 约定， `-` 来表示命令行开关
    :return:
    """
    parser = argparse.ArgumentParser(prog='Douban downloader',
                                     description="""
                                         A tiny tool to download douban resources
                                        """)
    parser.add_argument("url", help="start url of album or celebrity page")
    parser.add_argument('path', default='./douban', nargs='?', help='the path to store all resources defaul is ./douban')  # 可选
    # parser.add_argument('-a', '--album', help='album id', action='store')
    # parser.add_argument('-c', '--celebrity', help='celebrity id', action='store')
    return parser.parse_args()


def parse_url(url, path):
    """
    https://www.douban.com/photos/album/<album_id>
    https://movie.douban.com/celebrity/<celebrity_id>
    https://www.douban.com/people/<douban_id>/photos
    :param url:
    :param path: 下载路径
    :return:
    """
    match = re.match(r'https?://www.douban.com/photos/album/(\d+)', url)
    if match:
        album_id = match.group(1)
        get_album_by_id(album_id, path)
        return
    match = re.match(r'https?://movie.douban.com/celebrity/(\d+)', url)
    if match:
        celebrity_id = match.group(1)
        get_celebrity_by_id(celebrity_id, path)
        return
    match = re.match(r'https?://www.douban.com/people/(\w+)(/|/photos)', url)
    if match:
        people_id = match.group(1)
        people = People(people_id)
        for album_id in people.albums():
            get_album_by_id(album_id, os.path.join(path, album_id))
        return
    match = re.match(r'https?://movie.douban.com/subject/(\d+)', url)
    if match:
        movie_id = match.group(1)
        get_movie_by_id(movie_id, path)
        return
    print("Not support this url yet")


def main():
    """Main entry point"""
    args = get_args()
    if args.url is not None:
        parse_url(args.url, args.path)


if __name__ == '__main__':
    main()
