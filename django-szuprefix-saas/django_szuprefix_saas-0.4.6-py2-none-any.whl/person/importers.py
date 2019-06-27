# -*- coding:utf-8 -*-
from __future__ import unicode_literals
from ..saas.importers import BaseImporter
from .validators import field_gender, field_mobile, field_weixinid, field_qq, field_idcard, field_ethnic

class PersonImporter(BaseImporter):
    fields = [
        field_gender,
        field_mobile,
        field_weixinid,
        field_qq,
        field_idcard,
        field_ethnic
    ]
    min_fields_count = 2
