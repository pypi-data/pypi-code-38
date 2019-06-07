# -*- coding: utf-8 -*-

from .urlbuilder import UrlBuilder

url_correct = 'my-social-network-1.imgix.net'
url_append_slash = 'sherwinski.imgix.net/products'
url_prepend_protocol = 'https://sherwinski.imgix.net'
url_append_dash = 'sherwinski.imgix.net-products'
path = "image.jpg"
url_arr = ['sherwinski.imgix.net', 'sherwinski.imgix.net/products']
url_tuples = ('sherwinski.imgix.net', 'assets.imgix.net')
url_wrong = ['http://assets.imgix.net', 'sherwinski.imgix.net/products']


ub = UrlBuilder(url_wrong)
