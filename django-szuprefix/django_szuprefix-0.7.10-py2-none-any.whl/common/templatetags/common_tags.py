# -*- coding:utf-8 -*- 
__author__ = 'denishuang'
from django.template import Library
register = Library()


@register.filter()
def dump_images_json(images,thumb="100x100"):
    import json
    from sorl.thumbnail import get_thumbnail
    data = [{"url":r.file.url, "thumb_url":get_thumbnail(r.file,thumb).url, "id":r.id} for r in images]
    return json.dumps(data)

@register.filter()
def dump_attachments_json(attachments):
    import json
    data = [{"url":r.file.url, "name": r.name, "id":r.id} for r in attachments]
    return json.dumps(data)

