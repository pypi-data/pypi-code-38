# -*- coding: utf-8 -*-

# Copyright © 2019 by IBPort. All rights reserved.
# @Author: Neal Wong
# @Email: ibprnd@gmail.com

from parsel import Selector


class BookCategoryParser(object):
    def __init__(self, text, type='html', namespaces=None, root=None, base_url=None):
        self.selector = Selector(
            text, type=type, namespaces=namespaces, root=root, base_url=base_url)

    def parse(self):
        categories = []

        category_list_elem = self.selector.xpath('//div[@id="booksort"]/div[@class="mc"]/dl')
        for top_category_elem in category_list_elem.xpath('./dt'):
            top_category = {'children': []}

            top_category['name'] = top_category_elem.xpath(
                './a/text()').get().encode('utf-8').decode('utf-8')
            top_category['url'] = 'https:' + top_category_elem.xpath('./a/@href').get()

            for subcategory_elem in top_category_elem.xpath('./following-sibling::dd[1]/em'):
                name = subcategory_elem.xpath('./a/text()').get()
                if name:
                    top_category['children'].append({
                        'name': name.encode('utf-8').decode('utf-8'),
                        'url': 'https:' + subcategory_elem.xpath('./a/@href').get()
                    })

            categories.append(top_category)

        return categories
