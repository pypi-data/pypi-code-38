#!/usr/bin/env python
# -*- coding: utf-8 -*-

import io
import logging
from crawl_image.model.model import ImgCrawlModel, URL, IMG_SAVE_PATH
from crawl_image.index import ImgCrawl, run_multi_by_url


def run(url=URL, img_save_path=IMG_SAVE_PATH):
    img_crawl_model = ImgCrawlModel.build(url, img_save_path)
    img_crawl = ImgCrawl(img_crawl_model)
    img_crawl.print_img_list()
    img_crawl.crawl_start()


def run_for_url_list(file_path, img_save_path=IMG_SAVE_PATH, count_thread=10, do_last_url_file_name=False):
    url_list = remove_repeat(file_path)
    logging.info('去重之后的url条数 %s' % len(url_list))
    run_multi_by_url(url_list, img_save_path, count_thread, do_last_url_file_name)


def remove_repeat(file_path):
    with io.open(file_path, encoding='utf-8') as f:
        url_list = f.read()
    url_list = url_list.split('\n')
    if len(url_list) == 0:
        logging.info('file have not a url')
    return list(set(url_list))
