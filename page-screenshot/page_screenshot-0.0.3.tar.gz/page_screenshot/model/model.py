#!/usr/bin/env python
# -*- coding: utf-8 -*-

from page_screenshot.config.setting import *


class PageScreenshotModel:
    @staticmethod
    def build(url, img_save_path=IMG_SAVE_PATH, js_file_name=JS_FILE_NAME, outer_width=OUTER_PC_WIDTH, init_height=INIT_HEIGHT):
        if str(url).strip() == '':
            raise SystemExit('url 不能为空')
        page_screenshot_model = PageScreenshotModel()
        page_screenshot_model.url = url
        page_screenshot_model.img_save_path = img_save_path
        page_screenshot_model.js_file_name = js_file_name
        page_screenshot_model.outer_width = outer_width
        page_screenshot_model.init_height = init_height
        return page_screenshot_model

    timestamp_with_folder = TIMESTAMP_WITH_FOLDER
    url = URL
    img_save_path = IMG_SAVE_PATH

    base_height = BASE_HEIGHT
    scale_window = SCALE_HEIGHT

    time_ms_scroll_fast = TIME_MS_SCROLL_FAST
    time_ms_scroll_slow = TIME_MS_SCROLL_SLOW
    chrome_driver_path = CHROME_DRIVER_PATH

    init_window_position_x = INIT_WINDOW_POSITION_X
    init_window_position_y = INIT_WINDOW_POSITION_Y
    js_file_name = JS_FILE_NAME

    outer_width = OUTER_PC_WIDTH
    init_height = INIT_HEIGHT

    # 中间变量
    count_image = None
    file_name = None  # 无后缀

    def set_outer_width(self, outer_width):
        self.outer_width = outer_width

    def add_to_js_file_name(self, js_file_name):
        self.js_file_name = self.js_file_name + ' + "-%s"' % js_file_name

    def set_js_file_name(self, js_file_name):
        self.js_file_name = js_file_name
