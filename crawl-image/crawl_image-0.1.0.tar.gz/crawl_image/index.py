#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@project: crawl img tag source
@author: xiaohong
@time: 2019-01-01
@feature: crawl image for every site/multi thread to download/filter img type
@重构：20190612，使用class封装
"""

import time
import os
import threading
import chardet
import datetime
from urllib.parse import urlparse, urljoin
from urllib import request
from bs4 import BeautifulSoup

from crawl_image.model.model import *


def make_unique_folder(path, timestamp_with_folder=TIMESTAMP_WITH_FOLDER):
    """
    创建时间戳文件夹

    :param path: 文件路径
    :param timestamp_with_folder: 文件夹随机码
    :return: 文件夹路径
    """
    t = ''
    if timestamp_with_folder:
        t = '/' + str(int(time.time()))
    folder = path + t
    if not os.path.isdir(folder):
        os.makedirs(folder)
    return folder


def get_html(url):
    """
    获取网页源代码

    :param url: HTML网址
    :return: HTML内容
    """
    response = request.urlopen(url)
    html = response.read()
    return html.decode(chardet.detect(html)['encoding'])


def get_host(url):
    """
    获取域名+端口

    :param url: url
    :return: 域名端口
    """
    host = urlparse(url)
    return host.scheme + '://' + host.netloc


def get_img_url(host, src):
    """
    获取绝对路径

    :param host: 域名
    :param src: 资源相对地址
    :return: 资源绝对地址
    """
    return urljoin(host, src)


def get_img(html):
    """
    获取图片标签

    :param html: HTML内容
    :return: 页面所有img标签对象
    """
    soup = BeautifulSoup(html, 'html.parser')
    return soup.find_all('img')


def blank(s):
    """
    是否为空

    :param s: string
    :return: true is empty string, else false.
    """
    return s is None or s is ''


def img_suffix(src, default_img_suffix_):
    """
    img suffix

    :param src: 图片url
    :param default_img_suffix_: 默认图片后缀
    :return: 返回默认图片后缀，如果图片url没有带图片后缀的话
    """
    url_path = urlparse(str(src)).path
    i = url_path.rfind('.')
    return ('.' + default_img_suffix_) if -1 == i else url_path[i:]


def run_by_url(img_file_path, img_url):
    """
    download image from url

    :param img_file_path: 本地图片文件路径
    :param img_url: 图片url
    :return: void
    """
    # noinspection PyBroadException
    try:
        logging.info('下载 %s' % img_url)
        f = open(img_file_path, 'wb')
        f.write(request.urlopen(img_url).read())
        f.close()
    except Exception as e:
        logging.error('%s ，图片下载失败 : %s' % (str(e), img_url))


def thread_for_run_multi_by_url(url_list, img_save_path, file_name, do_last_url_file_name=False):
    for index, url in enumerate(url_list):
        if do_last_url_file_name:
            # if url is None or '/' not in url or url.rindex('/') == -1 or url.rindex('/') == len(url) - 1:
            if url is None or 0 == len(url):
                continue
            save_path = (img_save_path + '%s.' + DEFAULT_IMG_SUFFIX) % url[url.rindex('/'):]
            if not os.path.exists(save_path):
                run_by_url(save_path, url)
        else:
            run_by_url((img_save_path + '/%s.' + DEFAULT_IMG_SUFFIX) % (str(file_name) + '-' + str(index)), url)


def run_multi_by_url(url_list, img_save_path=IMG_SAVE_PATH, count_thread=10, do_last_url_file_name=False):
    """
    多线程抓取

    :param url_list:
    :param img_save_path:
    :param count_thread:
    :param do_last_url_file_name:
    :return:
    """
    if url_list is None or 0 == len(url_list):
        logging.info('url_list is empty')
    if len(url_list) < count_thread:
        count_thread = len(url_list)
    count_url_per_thread = len(url_list) / count_thread
    folder = make_unique_folder(img_save_path, not do_last_url_file_name)
    threads = []
    count_url_per_thread = int(count_url_per_thread)
    last = count_thread - 1

    for i in range(count_thread):
        start = i * count_url_per_thread
        if i == last:
            threads.append(threading.Thread(target=thread_for_run_multi_by_url, args=(url_list[start:], folder, start, do_last_url_file_name)))
        else:
            threads.append(threading.Thread(target=thread_for_run_multi_by_url,
                                            args=(url_list[start: start + count_url_per_thread], folder, start, do_last_url_file_name)))

    for th in threads:
        th.start()
    for th in threads:
        th.join()


def run(folder, img_name, host, img, default_img_suffix_):
    """
    download image

    :param folder: 本地存储文件夹
    :param img_name: 图片文件名称，不带后缀
    :param host: 域名
    :param img: img tag对象
    :param default_img_suffix_: 默认图片存储文件的后缀
    :return: void
    """
    path = folder + '/%s' + default_img_suffix_
    run_by_url(path % img_name, get_img_url(host, img.get('src')))


class ImgCrawl:
    def __init__(self, img_crawl_model_: ImgCrawlModel):
        """
        初始化
        :param img_crawl_model_: ImgCrawlModel
        """
        self.img_crawl_model_ = img_crawl_model_

    def run_multi(self, folder, host, img_list):
        """
        多线程抓取

        :param folder: 本地存储文件夹
        :param host: 域名
        :param img_list: img标签对象数组
        :return: void
        """
        threads = []
        for index, img in enumerate(img_list):
            threads.append(
                threading.Thread(target=run, args=(folder, index, host, img, img_suffix(img.get('src'), self.img_crawl_model_.default_img_suffix))))

        for th in threads:
            th.start()
        for th in threads:
            th.join()

    def save(self, img_list, host):
        """
        save image

        :param img_list: img tag对象数组
        :param host: 域名
        :return: void
        """
        folder = make_unique_folder(self.img_crawl_model_.img_save_path, TIMESTAMP_WITH_FOLDER)
        if self.img_crawl_model_.do_multi:
            self.run_multi(folder, host, img_list)
        else:
            for index, img in enumerate(img_list):
                run(folder, index, host, img, img_suffix(img.get('src'), self.img_crawl_model_.default_img_suffix))
        logging.info('下载完毕')

    def crawl_start(self):
        """
        start

        :return: void
        """
        start = datetime.datetime.now()
        host = get_host(self.img_crawl_model_.url)
        img_list = get_img(get_html(self.img_crawl_model_.url))
        img_list = self.img_list_filter(img_list)
        self.save(img_list, host)
        logging.warning('crawl 耗时 : ' + str(datetime.datetime.now() - start))

    def suffix_filter(self, src):
        """
        suffix filter

        :param src: 图片url
        :return: true is legal
        """
        if blank(src):
            return False
        suffix = img_suffix(src, self.img_crawl_model_.default_img_suffix)
        for e in self.img_crawl_model_.img_include_suffix:
            if suffix.endswith(e):
                return True
        for e in self.img_crawl_model_.img_exclude_suffix:
            if suffix.endswith(e):
                return False
        return True

    def img_list_filter(self, img_list):
        """
        img list filter

        :param img_list: img tag对象数组
        :return: 合法的img tag对象数组
        """
        img_list_result = []
        for img in img_list:
            if self.suffix_filter(img.get('src')):
                img_list_result.append(img)
        return img_list_result

    def print_img_list(self):
        """
        show image tag

        :return: void
        """
        img_list = get_img(get_html(self.img_crawl_model_.url))
        logging.info(dir(img_list[0]))

        img_list = self.img_list_filter(img_list)
        for img in img_list:
            logging.info('[' + str(img.get('src')) + '] : True')
