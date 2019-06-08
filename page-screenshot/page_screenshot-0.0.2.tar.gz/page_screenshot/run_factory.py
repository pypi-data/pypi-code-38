#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@project: page screenshot
@author: xiaohong
@time: 2019-06-07
@feature: a complete capture from a web page
"""

import io
import logging
from page_screenshot.model.model import PageScreenshotModel, OUTER_PC_WIDTH, OUTER_PHONE_WIDTH
from page_screenshot.index import PageScreenshot


def run_for_url_list(file_path, responsive_height=None):
    with io.open(file_path, encoding='utf-8') as f:
        url_list = f.read()
    url_list = url_list.split('\n')
    if len(url_list) == 0:
        logging.info('file have not a url')
    page_screenshot = screenshot_for_pc_and_phone(url_list[0], responsive_height)
    url_list.remove(url_list[0])
    for url in url_list:
        page_screenshot = screenshot_for_pc_and_phone(url, responsive_height, page_screenshot)
    page_screenshot.close()


def run(url, responsive_height=None):
    """
    run

    :param responsive_height: responsive_height
    :param url: url
    :return: void
    """
    page_screenshot = screenshot_for_pc_and_phone(url, responsive_height)
    page_screenshot.close()


def screenshot_for_pc_and_phone(url, responsive_height=None, page_screenshot=None):
    """
    pc and phone

    :param responsive_height: responsive_height
    :param url: url
    :param page_screenshot: page_screenshot
    :return: void
    """
    page_screenshot_model = screenshot_for_pc(url=url, responsive_height=responsive_height)
    if page_screenshot is None:
        page_screenshot = PageScreenshot(page_screenshot_model)
    else:
        page_screenshot.url_change(url)
    screenshot(page_screenshot_model, page_screenshot)

    page_screenshot_model = screenshot_for_phone(page_screenshot_model=page_screenshot_model, responsive_height=responsive_height)
    screenshot(page_screenshot_model, page_screenshot)

    return page_screenshot


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
    if responsive_height is not None:
        page_screenshot_model.init_height = responsive_height
    page_screenshot_model.set_outer_width(OUTER_PHONE_WIDTH)
    page_screenshot_model.add_to_js_file_name('phone')
    return page_screenshot_model


def screenshot(page_screenshot_model=None, page_screenshot=None):
    """
    screenshot now

    :param page_screenshot_model: model
    :param page_screenshot: page_screenshot
    :return:
    """
    if page_screenshot is None:
        PageScreenshot(page_screenshot_model).capture()
    else:
        page_screenshot.use_driver(page_screenshot_model).capture()
