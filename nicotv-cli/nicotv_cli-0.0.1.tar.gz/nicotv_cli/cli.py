#!/usr/bin/python3
# -*- coding: utf-8 -*-

from . import search
from . import detail
import json


def main():
    keyword = input("请输入动漫名称：")
    print('正在搜索...')
    videos = search.search(keyword)
    if len(videos) == 0:
        print('没有搜到结果!')
    else:
        for index in range(0, len(videos)):
            print('{}. {}-{}'.format(index + 1, videos[index]['name'], videos[index]['status']))
        while True:
            try:
                down_index = input("请选择要下载的序号：")
                index = int(down_index) - 1
                if 0 <= index < len(videos):
                    print('正在解析...')
                    urls = detail.get_video_urls(videos[index]['url'])
                    for url in urls:
                        print(json.dumps(detail.get_video_detail(url), ensure_ascii=False))
                    break
                else:
                    raise ValueError()
            except ValueError as e:
                print(e)
                print('你的输入有误！请重新输入')
                pass


if __name__ == '__main__':
    main()
