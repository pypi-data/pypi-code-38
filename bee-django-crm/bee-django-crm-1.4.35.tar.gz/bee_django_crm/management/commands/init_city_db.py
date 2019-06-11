# coding=utf-8
__author__ = 'zhangyue'
import os, datetime, urllib2, json
from django.core.management.base import BaseCommand, CommandError
from bee_django_crm.utils import loadJson
from bee_django_crm.models import Province, City, District


class Command(BaseCommand):
    def handle(self, *args, **options):
        def init_db():
            json_data = loadJson("city")
            citylist = json_data["citylist"]
            print(len(citylist).__str__() + "个省")
            for data in citylist:
                province = data["p"]
                p = save_province(province)
                city_list = data["c"]
                for city_data in city_list:
                    city = city_data["n"]
                    c = save_city(p, city)
                    # print(city)
                    if city_data.has_key("a"):
                        district_list = city_data["a"]
                        for district_data in district_list:
                            district = district_data["s"]
                            # print district
                            save_district(c, district)
            return

        def save_province(province):
            p = Province()
            p.name = province
            p.save()
            return p

        def save_city(p, city):
            c = City()
            c.province = p
            c.name = city
            c.save()
            return c

        def save_district(c, district):
            d = District()
            d.city = c
            d.name = district
            d.save()
            return

        p_list = Province.objects.all()
        if p_list.count() == 0:
            init_db()