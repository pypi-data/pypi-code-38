#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@project: page screenshot
@author: xiaohong
@time: 2019-06-07
@feature: a complete capture from a web page
"""

from page_screenshot.model.model import PageScreenshotModel, OUTER_PC_WIDTH, OUTER_PHONE_WIDTH
from page_screenshot.index import PageScreenshot


def run(url, responsive_height=None):
    """
    run

    :param responsive_height: responsive_height
    :param url: url
    :return: void
    """
    screenshot_for_pc_and_phone(url, responsive_height)


def screenshot_for_pc_and_phone(url, responsive_height=None):
    """
    pc and phone

    :param responsive_height: responsive_height
    :param url: url
    :return: void
    """
    page_screenshot_model = PageScreenshotModel.build(url)
    if responsive_height is not None:
        page_screenshot_model.init_height = responsive_height
    screenshot_for_pc(page_screenshot_model=page_screenshot_model)
    screenshot_for_phone(page_screenshot_model=page_screenshot_model)


def screenshot_for_pc(url=None, page_screenshot_model=None, responsive_height=None):
    """
    pc

    :param responsive_height: responsive_height
    :param url: url
    :param page_screenshot_model: model
    :return: void
    """
    if page_screenshot_model is None:
        page_screenshot_model = PageScreenshotModel.build(url)
    if responsive_height is not None:
        page_screenshot_model.init_height = responsive_height
    page_screenshot_model.set_outer_width(OUTER_PC_WIDTH)
    PageScreenshot(page_screenshot_model).capture()


def screenshot_for_phone(url=None, page_screenshot_model=None, responsive_height=None):
    """
    phone

    :param responsive_height: responsive_height
    :param url: url
    :param page_screenshot_model: model
    :return: void
    """
    if page_screenshot_model is None:
        page_screenshot_model = PageScreenshotModel.build(url)
    if responsive_height is not None:
        page_screenshot_model.init_height = responsive_height
    page_screenshot_model.set_outer_width(OUTER_PHONE_WIDTH)
    page_screenshot_model.add_to_js_file_name('phone')
    PageScreenshot(page_screenshot_model).capture()
