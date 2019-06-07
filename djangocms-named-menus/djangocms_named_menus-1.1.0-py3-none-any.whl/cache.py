# -*- coding: utf-8 -*-
'''
Created on May 21, 2016

@author: jakob
'''

from django.conf import settings
from django.core.cache import cache

from cms_named_menus.models import CMSNamedMenu
from cms_named_menus.settings import CACHE_DURATION


def contains_page(menu, page_id):
    for page in menu.pages:
        if page['id'] == page_id:
            return True
        for child in page.get('children', []):
            if child['id'] == page_id:
                return True


def _key(menu_slug):
    return 'cms_named_menu_{}'.format(menu_slug)


def get(menu_slug):
    key = _key(menu_slug)
    return cache.get(key, None)


def set(menu_slug, nodes):  # @ReservedAssignment
    key = _key(menu_slug)
    cache.set(key, nodes, CACHE_DURATION)


def delete(menu_slug=None):
    delete_many([menu_slug])


def delete_many(menu_slugs=None):
    for menu_slug in menu_slugs:
        key = _key(menu_slug)
        cache.delete(key)


def delete_by_page_id(page_id=None):
    menu_slugs = []
    filter_string='"id":{}'.format(page_id)
    for menu in CMSNamedMenu.objects.filter(pages__contains=filter_string).all():
        if contains_page(menu, page_id):
            menu_slugs.append(menu.name)

    delete_many(menu_slugs)
