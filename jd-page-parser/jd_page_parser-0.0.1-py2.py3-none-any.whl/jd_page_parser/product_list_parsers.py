# -*- coding: utf-8 -*-

# Copyright © 2019 by IBPort. All rights reserved.
# @Author: Neal Wong
# @Email: ibprnd@gmail.com

from parsel import Selector


class BookListParser(object):
    def __init__(self, text, type='html', namespaces=None, root=None, base_url=None):
        self.selector = Selector(
            text, type=type, namespaces=namespaces, root=root, base_url=base_url)

    def parse(self):
        result = {'links': []}

        book_links_xpath = '//div[@id="plist"]/ul/li[@class="gl-item"]//' + \
            'div[contains(@class, "j-sku-item")]/div[@class="p-name"]/a'
        for book_link_elem in self.selector.xpath(book_links_xpath):
            title = book_link_elem.xpath(
                './em/text()').get().strip().encode('utf-8').decode('utf-8')
            result['links'].append({
                'url': 'https:' + book_link_elem.xpath('./@href').get(),
                'title': title
            })

        next_page_elem = self.selector.xpath(
            '//div[@id="J_bottomPage"]/span[@class="p-num"]/a[@class="pn-next"]')
        if next_page_elem:
            try:
                result['next_page_uri'] = next_page_elem.xpath('./@href').get()
            except:
                result['next_page_uri'] = None
        else:
            result['next_page_uri'] = None

        return result
