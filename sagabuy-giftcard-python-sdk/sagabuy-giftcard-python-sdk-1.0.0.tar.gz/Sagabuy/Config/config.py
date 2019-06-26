#!/usr/bin/python
# -*- coding: utf-8 -*-

class Config:

    __app_id = None
    __app_secret = None
    __request_url = 'https://giftcard.sagabuy.com/api/open/'

    def __init__(self, app_id, app_secret):
        if (app_id == None or app_secret == None):
            raise Exception('app_id and app_secret cannot be empty')
        self.__app_id = app_id
        self.__app_secret = app_secret

    def get_app_id(self):
        return self.__app_id

    def get_app_secret(self):
        return self.__app_secret

    def get_request_url(self):
        return self.__request_url