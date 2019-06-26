#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@project: page screenshot
@author: xiaohong
@time: 2019-06-07
@feature: a complete capture from a web page
"""

import io
import os
import time
import shutil
import logging
import threading
from page_screenshot.model.model import PageScreenshotModel, OUTER_PC_WIDTH, OUTER_PHONE_WIDTH, TIMESTAMP_WITH_FOLDER
from page_screenshot.index import PageScreenshot
import random


def make_unique_folder(path, timestamp_with_folder=TIMESTAMP_WITH_FOLDER):
    """
    创建时间戳文件夹

    :param path: 文件路径
    :param timestamp_with_folder: 文件夹随机码
    :return: 文件夹路径
    """
    t = ''
    if timestamp_with_folder:
        t = '/' + str(int(time.time())) + str(random.randint(0, 1000000))
    folder = path + t
    if not os.path.isdir(folder):
        os.makedirs(folder)
    return folder


def run_thread(url_list=None, responsive_height=None):
    if url_list is None or 0 == len(url_list):
        return
    page_screenshot = PageScreenshot()

    # 建立唯一的目录
    url = url_list[0]
    page_screenshot_model = screenshot_for_pc(url=url, responsive_height=responsive_height)
    page_screenshot_model.img_save_path = make_unique_folder(page_screenshot_model.default_img_save_path)

    # js file name
    default_js_file_name = page_screenshot_model.js_file_name
    for url in url_list:
        # 修改默认目录，重复利用model对象
        # pc
        page_screenshot_model = screenshot_for_pc(url=url, page_screenshot_model=page_screenshot_model, responsive_height=responsive_height)
        page_screenshot.capture(page_screenshot_model)

        time.sleep(1)

        # phone
        page_screenshot_model = screenshot_for_phone(url=url, page_screenshot_model=page_screenshot_model, responsive_height=responsive_height)
        page_screenshot.capture(page_screenshot_model)

        # revert
        page_screenshot_model.js_file_name = default_js_file_name
    # close
    page_screenshot.close()

    logging.info('move file ...')
    # move file to default path
    for f in os.listdir(page_screenshot_model.img_save_path):
        shutil.move(page_screenshot_model.img_save_path + '/' + f, page_screenshot_model.default_img_save_path + '/' + f)

    # remove folder
    # noinspection PyBroadException
    try:
        shutil.rmtree(page_screenshot_model.img_save_path)
    except Exception as e:
        logging.info('remove folder error %s' % e)


def run_for_url_list(file_path, responsive_height=None, count_thread=10):
    with io.open(file_path, encoding='utf-8') as f:
        url_list = f.read()
    url_list = url_list.split('\n')
    if len(url_list) == 0:
        logging.info('file have not a url')

    if count_thread <= 0:
        count_thread = 10
    if len(url_list) < count_thread:
        count_thread = len(url_list)
    count_url_per_thread = len(url_list) / count_thread
    threads = []
    count_url_per_thread = int(count_url_per_thread)
    last = count_thread - 1

    for i in range(count_thread):
        start = i * count_url_per_thread
        if i == last:
            threads.append(threading.Thread(target=run_thread, args=(url_list[start:], responsive_height)))
        else:
            threads.append(threading.Thread(target=run_thread, args=(url_list[start: start + count_url_per_thread], responsive_height)))

    for th in threads:
        th.start()
    for th in threads:
        th.join()


def run(url, responsive_height=None):
    """
    run

    :param responsive_height: responsive_height
    :param url: url
    :return: void
    """
    page_screenshot = PageScreenshot()
    screenshot_for_pc_and_phone(url, page_screenshot, responsive_height)
    page_screenshot.close()


def screenshot_for_pc_and_phone(url, page_screenshot, responsive_height=None):
    """
    pc and phone

    :param responsive_height: responsive_height
    :param url: url
    :param page_screenshot: page_screenshot
    :return: void
    """
    page_screenshot_model = screenshot_for_pc(url=url, responsive_height=responsive_height)
    page_screenshot.capture(page_screenshot_model)

    page_screenshot_model = screenshot_for_phone(page_screenshot_model=page_screenshot_model, responsive_height=responsive_height)
    page_screenshot.capture(page_screenshot_model)


def screenshot_for_pc(url=None, page_screenshot_model=None, responsive_height=None):
    """
    pc

    :param responsive_height: responsive_height
    :param url: url
    :param page_screenshot_model: model
    :return: page_screenshot_model
    """
    if page_screenshot_model is None:
        page_screenshot_model = PageScreenshotModel.build(url)
    if url is not None:
        page_screenshot_model.url = url
    if responsive_height is not None:
        page_screenshot_model.init_height = responsive_height
    page_screenshot_model.set_outer_width(OUTER_PC_WIDTH)
    return page_screenshot_model


def screenshot_for_phone(url=None, page_screenshot_model=None, responsive_height=None):
    """
    phone

    :param responsive_height: responsive_height
    :param url: url
    :param page_screenshot_model: model
    :return: page_screenshot_model
    """
    if page_screenshot_model is None:
        page_screenshot_model = PageScreenshotModel.build(url)
    if url is not None:
        page_screenshot_model.url = url
    if responsive_height is not None:
        page_screenshot_model.init_height = responsive_height
    page_screenshot_model.set_outer_width(OUTER_PHONE_WIDTH)
    page_screenshot_model.add_to_js_file_name('phone')
    return page_screenshot_model
