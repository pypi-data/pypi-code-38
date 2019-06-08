#!/usr/bin/python3
# -*- coding: utf-8 -*-

import requests
import scrapy
import re
import json
from requests.models import PreparedRequest
from scrapy import Selector

from scrapy.http import HtmlResponse

SEARCH_URL = 'http://www.nicotv.me/video/search/{keyword}.html'


def search(keyword):
    url = SEARCH_URL.format(keyword=keyword)
    rsp = requests.get(url)
    response = HtmlResponse(body=rsp.content, url=rsp.url)
    search_result = response.xpath('//div[@class="container ff-bg"]/ul[contains(@class, "list-unstyled")]/li')
    videos = []
    for item in search_result:
        status = item.xpath('.//span[@class="continu"]/text()').extract_first()
        videos.append({
            'name': item.xpath('./h2/a/text()').extract_first(),
            'url': response.urljoin(item.xpath('./h2/a/@href').extract_first()),
            'status': status.strip() if status else ''
        })
    return videos


# print(json.dumps(search('darling'), ensure_ascii=False))
