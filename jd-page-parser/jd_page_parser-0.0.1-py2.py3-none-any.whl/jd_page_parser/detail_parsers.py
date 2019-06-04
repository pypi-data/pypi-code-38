# -*- coding: utf-8 -*-

# Copyright © 2019 by IBPort. All rights reserved.
# @Author: Neal Wong
# @Email: ibprnd@gmail.com

from parsel import Selector


class BookDetailParser(object):
    def __init__(self, text, type='html', namespaces=None, root=None, base_url=None):
        self.selector = Selector(
            text, type=type, namespaces=namespaces, root=root, base_url=base_url)

    def parse(self):
        name_elem = self.selector.xpath(
            '//div[@id="product-intro"]//div[@id="itemInfo"]/div[@id="name"]')
        raw_title = name_elem.xpath('./div[@class="sku-name"]/text()').get()
        raw_authors = name_elem.xpath('./div[@id="p-author"]/a/text()').getall()

        title = raw_title.strip().encode('utf-8').decode('utf-8') if raw_title else ''
        if raw_authors:
            author = ','.join(
                [raw_author.strip().encode('utf-8').decode('utf-8') for raw_author in raw_authors])
        else:
            author = ''

        images = []
        image_elems = self.selector.xpath(
            '//div[@id="spec-list"]/div[@class="spec-items"]/ul/li/img')
        for image_elem in image_elems:
            image_url = 'https:' + image_elem.xpath('./@src').get()
            images.append(image_url.replace('n5/jfs', 'n1/jfs'))

        detail = dict()
        detail_item_elems = self.selector.xpath('//ul[@id="parameter2"]/li')
        for detail_item_elem in detail_item_elems:
            if detail_item_elem.xpath('./a').getall():
                k = detail_item_elem.xpath('./text()').get().strip().split(u'：').pop(0)
                v = detail_item_elem.xpath('./@title').get().strip()
            else:
                detail_item_str = detail_item_elem.xpath('./text()').get()
                k, v = detail_item_str.split(u'：')
            detail[k.encode('utf-8').decode('utf-8')] = v.encode('utf-8').decode('utf-8')

        return {
            'title': title,
            'author': author,
            'images': images,
            'detail': detail
        }
