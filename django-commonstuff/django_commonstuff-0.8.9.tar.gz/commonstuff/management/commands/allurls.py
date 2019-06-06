# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import, division, print_function

from django import get_version
from django.core.management.base import BaseCommand
from django.core.urlresolvers import get_resolver


class Command(BaseCommand):
    help = 'Shows all project urls (routes) alphabetically in cli environment.'
    
    def handle(self, *args, **options):
        urls = sorted(set(v[1] for k,v in get_resolver(None).reverse_dict.items()))
        for url in urls:
            self.stdout.write(url)
