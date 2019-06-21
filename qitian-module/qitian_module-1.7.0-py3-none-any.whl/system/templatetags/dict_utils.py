from django import template

register = template.Library()


@register.filter(name='get_item')
def get_item(item, key):
    return item.get(key, '')


@register.filter(name='to_int')
def to_int(item):
    return int(item)


@register.filter(name='to_str')
def to_str(item):
    return str(item)


@register.filter(name='add_str')
def add_str(org_str, plus_str):
    return str(org_str) + str(plus_str)
