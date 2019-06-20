# -*- coding: utf-8 -*-
from appconf import AppConf
from django.conf import settings as dj_settings

settings = dj_settings

class ZipCodeConf(AppConf):
    PAGINATION_CLASS = 'zip_code_api.pagination.HeaderPagination'
    PAGE_SIZE = 10

    class Meta:
        prefix = 'ZIP_CODE'
