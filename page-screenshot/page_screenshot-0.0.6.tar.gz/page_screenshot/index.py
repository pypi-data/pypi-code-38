#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@project: page screenshot
@author: xiaohong
@time: 2019-06-07
@feature: a complete capture from a web page
"""

import time
import os
from PIL import Image
from selenium import webdriver

from page_screenshot.model.model import *


def make_unique_folder(path):
    """
    创建时间戳文件夹

    :param path: 文件路径
    :return: 文件夹路径
    """
    t = ''
    # if TIMESTAMP_WITH_FOLDER:
    #     t = '/' + str(int(time.time()))
    folder = path + t
    if not os.path.isdir(folder):
        os.makedirs(folder)
    return folder


class PageScreenshot:
    def __init__(self):
        """
        init
        """
        self.model = None
        self.driver = self.take_driver()

    def print_w_h(self):
        """
        print

        :return: void
        """
        width = self.driver.execute_script(JS_MAX_WIDTH)
        height = self.driver.execute_script(JS_MAX_HEIGHT)
        driver_width = self.driver.get_window_size()['width']
        driver_height = self.driver.get_window_size()['height']
        window_height = self.driver.execute_script(JS_WINDOW_HEIGHT)

        logging.info('外宽(set_window_size) %s, %s; 外宽截图 %s, %s; 内宽(JS_MAX_WIDTH/HEIGHT) %s %s; 内宽截图 %s, %s'
                     % (driver_width, driver_height,
                        driver_width * self.model.scale_window, driver_height * self.model.scale_window,
                        width, height,
                        width * self.model.scale_window, window_height))

    def calc_right_step_scroll(self):
        """
        计算滚动大小

        :return: 滚动次数，滚动高度
        """
        times_shot = 1
        inner_height = height = float(self.driver.execute_script(JS_MAX_HEIGHT))

        # # 没有超出基本高度
        # if inner_height <= self.model.base_height:
        #     return times_shot, window_height

        # 计算不超出基本高度的截图高度
        while True:
            if inner_height <= self.model.base_height:
                break
            times_shot = times_shot + 1
            inner_height = height / times_shot
        # 保持宽度不变，修改高度为内高的变率倍
        driver_height = self.driver.get_window_size()['height']
        window_height = self.driver.execute_script(JS_WINDOW_HEIGHT)
        if 0 == window_height:
            window_height = 1
        self.driver.set_window_size(self.driver.get_window_size()['width'], inner_height * driver_height / window_height)

        # 获取截图高度
        logging.info('times_shot : %s' % times_shot)
        self.print_w_h()
        return times_shot, self.driver.execute_script(JS_WINDOW_HEIGHT)

    def scroll_to_capture(self):
        """
        滚动并截图

        :return: 截图次数
        """
        self.model.img_save_path = make_unique_folder(self.model.img_save_path)
        times_shot, step_scroll = self.calc_right_step_scroll()

        # 快速滚动一遍
        for i in range(times_shot):
            self.driver.execute_script(JS_SCROLL % (i * step_scroll, self.model.time_ms_scroll_fast))
            time.sleep(self.model.time_ms_scroll_fast * 0.002)

            # 滚动到顶部
            self.driver.execute_script(JS_SCROLL % (0, self.model.time_ms_scroll_fast))
        times_shot, step_scroll = self.calc_right_step_scroll()

        # 滚动两遍，确保已经加载完毕
        for i in range(times_shot):
            self.driver.execute_script(JS_SCROLL % (i * step_scroll, self.model.time_ms_scroll_slow))
            time.sleep(self.model.time_ms_scroll_slow * 0.002)

            self.driver.save_screenshot(self.model.img_save_path + '/' + str(i) + DEFAULT_IMG_SUFFIX)
        time.sleep(3)
        return times_shot

    @staticmethod
    def take_driver():
        """
        生成driver

        :return: WebDriver
        """
        options = webdriver.ChromeOptions()
        # options.binary_location = 'C:/Users/xh/AppData/Roaming/360se6/Application/360se.exe'  # 修改成360浏览器
        # options.add_argument('--headless')  # 无法加载异步请求的图片，即滚动事件不会进行图片加载
        options.add_argument('--dns-prefetch-disable')
        options.add_argument('--no-referrers')
        options.add_argument('--disable-gpu')
        options.add_argument('--disable-audio')
        options.add_argument('--no-sandbox')
        options.add_argument('--ignore-certificate-errors')
        options.add_argument('--allow-insecure-localhost')
        # options.add_argument('--switcher-file=C:/Users/xh/Documents/PyCharmProjects/page_screenshot/switch_360_chrome.txt')  # 修改成360浏览器
        options.add_argument('disable-infobars')

        driver = webdriver.Chrome(options=options, executable_path=CHROME_DRIVER_PATH)
        return driver

    def take_url(self):
        self.driver.get(url=self.model.url)
        time.sleep(.5)
        self.driver.set_window_position(self.model.init_window_position_x, self.model.init_window_position_y)

        # self.driver.execute_script("document.body.style.zoom='125%'")  # 修改成360浏览器
        self.driver.execute_script('document.body.parentNode.style.overflowX = "hidden";')  # 隐藏滚动条
        self.driver.execute_script('document.body.parentNode.style.overflowY = "hidden";')  # 隐藏滚动条

        self.driver.set_window_size(self.model.outer_width / self.model.scale_window, self.model.init_height)

    def check(self):
        template_file_name = self.model.default_img_save_path + '/%s' + DEFAULT_IMG_SUFFIX
        return os.path.exists(template_file_name % self.model.file_name)

    def capture(self, page_screenshot_model: PageScreenshotModel):
        """
        生成网页截图文件

        :param page_screenshot_model: PageScreenshotModel
        :return: void
        """
        self.model = page_screenshot_model
        self.take_url()

        # noinspection PyBroadException
        try:
            # 执行指定的js脚本，建立文件名
            self.model.file_name = self.driver.execute_script(self.model.js_file_name)
        except Exception:
            # noinspection PyBroadException
            try:
                # 使用url的md5值作为文件名
                self.model.file_name = self.driver.execute_script(JS_MD5_URL)
            except Exception:
                # 使用时间戳作为文件名
                self.model.file_name = str(int(time.time()))

        # 过滤不合符文件名字符
        self.model.file_name = self.filter_file_name(self.model.file_name)

        # 检查文件是否存在
        if self.check():
            logging.info('图片已存在 %s' % self.model.file_name)
            return

        # capture now
        logging.info('开始捕获截图的url %s' % page_screenshot_model.url)
        self.model.count_image = self.scroll_to_capture()
        logging.info('merge image ...')
        self.merge()
        logging.info('remove_temp_file ...')
        self.remove_temp_file()

    def close(self):
        """
        close

        :return: void
        """
        self.driver.quit()

    def remove_temp_file(self):
        """
        删除每次滚动截图文件

        :return: void
        """
        template_file_name = self.model.img_save_path + '/%s' + DEFAULT_IMG_SUFFIX
        for i in range(self.model.count_image):
            # noinspection PyBroadException
            try:
                os.remove(template_file_name % i)
            except Exception:
                print('no image file, go on')

    @staticmethod
    def filter_file_name(file_name: str):
        """
        过滤非法文件名称的字符
        :param file_name: 文件名
        :return: 正确的文件名
        """
        illegal_char = ['\\', '/', ':', '*', '?', '"', '<', '>', '|']
        for i in illegal_char:
            file_name = file_name.replace(i, '')
        return file_name

    def merge(self):
        """
        拼接滚动截图文件

        :return: void
        """
        template_file_name = self.model.img_save_path + '/%s' + DEFAULT_IMG_SUFFIX

        f = Image.open(template_file_name % 0)
        w, h = f.size
        merge_image = Image.new('RGBA', (w, h * self.model.count_image))
        for i in range(self.model.count_image):
            merge_image.paste(Image.open(template_file_name % i), (0, i * h))

        # save to one image file
        # noinspection PyBroadException
        try:
            merge_image.save(template_file_name % self.model.file_name)
        except Exception:
            merge_image.save(template_file_name % str(int(time.time())))
            logging.info('文件名称不合符 %s' % self.model.url)
        time.sleep(1)
