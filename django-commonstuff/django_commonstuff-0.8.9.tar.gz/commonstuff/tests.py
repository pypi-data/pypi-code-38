# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import, division, print_function

from django.test import TestCase


class CommonstuffTests(TestCase):
    def test_autocorrect_email_sub(self):
        from commonstuff.str_utils import autocorrect_email
        self.assertEqual(autocorrect_email('user@@mail.ru'), 'user@mail.ru')
        self.assertEqual(autocorrect_email('user@mail.ruuser@mail.ru'), 'user@mail.ru')
        self.assertEqual(autocorrect_email('с-user@mail.ru'), 'c-user@mail.ru')
        self.assertEqual(autocorrect_email('user.@.mail.ru'), 'user@mail.ru')
        self.assertEqual(autocorrect_email('user@mail.ry'), 'user@mail.ru')
        self.assertEqual(autocorrect_email('user@mail ru'), 'user@mail.ru')
        self.assertEqual(autocorrect_email('user@mail,ru'), 'user@mail.ru')
        self.assertEqual(autocorrect_email('user@meil'), 'user@mail.ru')
        self.assertEqual(autocorrect_email('user@gmail'), 'user@gmail.com')
        self.assertEqual(autocorrect_email('user@inboks'), 'user@inbox.ru')
        self.assertEqual(autocorrect_email('user@ramblerru'), 'user@rambler.ru')
        self.assertEqual(autocorrect_email('usermail.ru'), 'user@mail.ru')
        self.assertEqual(autocorrect_email('    user@MAIL.ru   '), 'user@mail.ru')
    
    def test_decode_htmlentities_template_string_filter(self):
        from commonstuff.templatetags.str_tools import decode_htmlentities
        self.assertEqual(decode_htmlentities('&pound;'), '£')
    
