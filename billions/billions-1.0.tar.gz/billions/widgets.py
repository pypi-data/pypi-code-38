#!/usr/bin/env python
# -*- coding:utf-8 -*-
import json
from django import forms
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

from .utils import static, JS

DEFAULT_CONFIG = {
    "width": "100%",
    "height": 640,
    "path": static("billions/editormd/lib/"),
    "placeholder": "Enjoy coding!",
    "syncScrolling": True,
    "codeFold": True,
    "htmlDecode": True,
    "imageUpload": True,
    "imageFormats": ["jpg", "jpeg", "gif", "png", "bmp", "webp", "JPG"],
    "imageUploadURL": "./php/upload.php",
}


class BillionsMarkdownEditorWidget(forms.Textarea):
    template_name = 'billions/widgets/mdeditor.html'

    class Media:
        js = (
            'billions/editormd/editormd.js',
            'billions/billions-init.js',
        )

        css = {
            'all': ('billions/editormd/css/editormd.css', 'billions/billions-init.css',),
        }

    def __init__(self, config_name='default', *args, **kwargs):
        super(BillionsMarkdownEditorWidget, self).__init__(*args, **kwargs)
        self.config = DEFAULT_CONFIG.copy()
        configs = getattr(settings, 'BILLIONS_CONFIGS', None)
        if not isinstance(configs, dict):
            raise ImproperlyConfigured("请为mdeditor设置相关配置BILLIONS_CONFIGS")

        config = configs.get(config_name)
        if not config:
            raise ImproperlyConfigured("BILLIONS_CONFIGS中配置项%s不存在" % config_name)
        self.config.update(config)

    def get_context(self, name, value, attrs):
        context = {}
        final_attrs = self.build_attrs(self.attrs, attrs)
        billions_area_id = "%s_billions_area" % final_attrs['id']
        self.config['id'] = billions_area_id

        final_attrs['billions-config'] = json.dumps(self.config)

        context['widget'] = {
            'name': name,
            'is_hidden': self.is_hidden,
            'required': self.is_required,
            'value': self.format_value(value),
            'attrs': final_attrs,
            'billions_area_id': billions_area_id
        }
        return context
