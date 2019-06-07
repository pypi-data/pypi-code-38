from __future__ import annotations

import logging
import os
import sys

import requests
from dotenv import load_dotenv

from discountr.models import Brand, Category, Product, Price

load_dotenv()

logger = logging.getLogger('APIClient')


class API:
    _url = os.getenv('API_URL', 'https://api.discountr.info/')
    _token = "Token " + os.getenv('API_TOKEN', '')

    def __init__(self, app_name: str = None):
        super().__init__()

        self._app_name = app_name

    def create_brand(self, brand: Brand):
        self.__create('brands', brand)

    def create_category(self, category: Category):
        self.__create('categories', category)

    def create_product(self, product: Product):
        self.__create('products', product)

    def create_price(self, price: Price):
        self.__create('prices', price)

    def get_all_brands(self):
        return self.__get_all('brands')

    def get_all_categories(self):
        return self.__get_all('categories')

    def get_all_products(self):
        return self.__get_all('products')

    def __get_all(self, endpoint):
        temp = []
        link = '%s%s/%s/' % (self._url, self._app_name, endpoint)
        while True:
            response = requests.get(link)
            data = response.json()
            if data['next'] is not None:
                link = data['next']
                temp.extend(data['results'])
            else:
                break
        return temp

    def __create(self, endpoint, data):
        response = requests.post('%s%s/%s/' % (self._url, self._app_name, endpoint),
                                 data=data.to_json(), headers={
                'Authorization': self._token,
                'Content-Type': 'application/json'
            })

        if response.status_code >= 500:
            logger.critical(
                '%s Server Error: %s for url: %s\n\tREQUEST DATA => %s\n\tRESPONSE MSG => %s' % (
                    response.status_code, response.reason, response.url, data.to_json(), response.content))
        elif response.status_code >= 400:
            logger.warning('%s Client Error: %s for url: %s\n\tREQUEST DATA => %s\n\tRESPONSE MSG => %s' % (
                response.status_code, response.reason, response.url, data.to_json(), response.content))
