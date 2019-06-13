#!/usr/bin/env python
# -*- coding: utf-8 -*-

from crawl_image.config.setting import *


class ImgCrawlModel:
    @staticmethod
    def build(url, img_save_path=IMG_SAVE_PATH):
        if str(url).strip() == '':
            raise SystemExit('url 不能为空')
        img_crawl_model = ImgCrawlModel()
        img_crawl_model.url = url
        img_crawl_model.img_save_path = img_save_path
        return img_crawl_model

    url = URL
    img_save_path = IMG_SAVE_PATH
    do_multi = DO_MULTI
    default_img_suffix = DEFAULT_IMG_SUFFIX
    img_include_suffix = IMG_INCLUDE_SUFFIX
    img_exclude_suffix = IMG_EXCLUDE_SUFFIX
