# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import, division, print_function

from django import get_version
from django.core.management.base import BaseCommand#, CommandError


class Command(BaseCommand):
    help = 'Shows django version in cli environment.'
    
    def handle(self, *args, **options):
        self.stdout.write("Django %s" % get_version())
