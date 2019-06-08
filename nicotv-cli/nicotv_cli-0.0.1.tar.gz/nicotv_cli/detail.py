#!/usr/bin/python3
# -*- coding: utf-8 -*-

import requests
import scrapy
import re
import json
from requests.models import PreparedRequest
from scrapy import Selector

from scrapy.http import HtmlResponse


def get_video_detail(detail_url):
    video_detail = {}
    try:
        rsp = requests.get(detail_url)
        response = HtmlResponse(body=rsp.content, url=rsp.url)
        video_detail['title'] = response.xpath('//div[@class="media"]//a[@class="ff-text"]/text()').extract_first()
        # video_detail['actors'] = response.xpath('//div[@class="media"]//dt[contains(text(), "主演")]/following-sibling::dd[1]//text()').extract()
        #
        # video_detail['directors'] = response.xpath(
        #     '//div[@class="media"]//dt[contains(text(), "导演")]/following-sibling::dd[1]//text()').extract()
        # video_detail['categories'] = response.xpath(
        #     '//div[@class="media"]//dt[contains(text(), "类型")]/following-sibling::dd[1]//text()').extract()
        # video_detail['area'] = response.xpath(
        #     '//div[@class="media"]//dt[contains(text(), "地区")]/following-sibling::dd[1]//text()').extract_first()
        # video_detail['year'] = response.xpath(
        #     '//div[@class="media"]//dt[contains(text(), "年份")]/following-sibling::dd[1]//text()').extract_first()
        data_active = response.xpath('//ul[contains(@class, "ff-playurl") and contains(@class, "active")]/@data-active').extract_first()
        video_detail['episode'] = response.xpath('//li[@data-id="{data_active}"]//text()'.format(data_active=data_active)).extract_first()
        player_url = response.xpath('//div[@id="cms_player"]/script[1]/@src').extract_first()
        rsp = requests.get(response.urljoin(player_url))
        video_info = json.loads(re.findall(r'var cms_player = (\{[\s\S]+?\});', rsp.text)[0])
        # print(video_info)
        req = PreparedRequest()
        url = video_info['url']
        if video_info['name'] == 'haokan_baidu':
            params = {}
            req.prepare_url(url, params)
        elif video_info['name'] == '360biaofan':
            params = {'time': video_info['time'], 'auth_key': video_info['auth_key']}
            req.prepare_url(url, params)
        rsp = requests.get(req.url)
        script_text = Selector(text=rsp.text).xpath('//script/text()').extract_first()
        # print(script_text)
        video_detail['video_url'] = re.findall(r'url: *\"(\S+?)\"', script_text)[0]
        return video_detail
    except KeyboardInterrupt:
        print('Interrupted')
        exit(0)
    except Exception:
        return video_detail


def get_video_urls(url):
    rsp = requests.get(url)
    response = HtmlResponse(body=rsp.content, url=rsp.url)
    video_urls = response.xpath('//ul[contains(@class, "ff-playurl") and contains(@class, "active")]/li/a/@href').extract()
    for i in range(0, len(video_urls)):
        video_urls[i] = response.urljoin(video_urls[i])
    return video_urls


# urls = get_video_urls('http://www.nicotv.me/video/play/53294-1-1.html')
# for url in urls:
#     print(get_video_detail(url))
