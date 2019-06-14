#!/usr/bin/python
# -*- coding: utf-8 -*-
from Homevee.Item import APIKey, Item
from Homevee.Item.APIKey import APIKey
from Homevee.Item.Status import *
from Homevee.Utils.Database import Database

class APIKeyManager():
    def get_all_api_key_data(self, user, db: Database = None):
        if db is None:
            db = Database()
        if not user.has_permission("admin"):
            return Status(type=STATUS_NO_ADMIN).get_dict()

        services = [
            {'servicename': 'Open Weather Map',
             'description': 'Open Weather Map stellt Wetterdaten und -vorhersagen bereit.', 'registerkeyurl': '',
             'servicelogourl': 'https://openweathermap.org/themes/openweathermap/assets/vendor/owm/img/logo_OpenWeatherMap_orange.svg'},
            {'servicename': 'IMDB', 'description': 'IMDB ist eine internationale Filmdatenbank', 'registerkeyurl': '',
             'servicelogourl': 'http://ia.media-imdb.com/images/G/01/imdb/images/mobile/imdb-logo-responsive@2-868559777._CB514893749_.png'}
        ]

        output = []

        for service in services:
            api_key = self.get_api_key(service['servicename'], db)

            if api_key is not None:
                service['key'] = api_key['key']
                output.append(service)

        return output

    def get_api_key(self, service_name, db: Database = None):
        if db is None:
            db = Database()
        api_key = APIKey.find_by_name(service_name, db)

        if api_key is not None:
            return api_key.get_dict()
        else:
            return None

    def set_api_key(self, user, id, service, api_key, db: Database = None):
        if not user.has_permission("admin"):
            return Status(type=STATUS_NO_ADMIN).get_dict()

        if db is None:
            db = Database()

        api_key = Item.load_from_db(APIKey, id, db)

        if api_key is None:
            api_key = APIKey(service, api_key)

        return api_key.api_save(db)