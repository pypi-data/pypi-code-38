#!/usr/bin/env python2
# -*- coding: utf-8 -*-

# SAT: a jabber client
# Copyright (C) 2009-2019 Jérôme Poisson (goffi@goffi.org)

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.

# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

""" Plugin text syntaxes tests """

from sat.test import helpers
from sat.plugins import plugin_misc_text_syntaxes
from twisted.trial.unittest import SkipTest
import re


class SanitisationTest(helpers.SatTestCase):

    EVIL_HTML1 = """
   <html>
    <head>
      <script type="text/javascript" src="evil-site"></script>
      <link rel="alternate" type="text/rss" src="evil-rss">
      <style>
        body {background-image: url(javascript:do_evil)};
        div {color: expression(evil)};
      </style>
    </head>
    <body onload="evil_function()">
      <!-- I am interpreted for EVIL! -->
      <a href="javascript:evil_function()">a link</a>
      <a href="#" onclick="evil_function()">another link</a>
      <p onclick="evil_function()">a paragraph</p>
      <div style="display: none">secret EVIL!</div>
      <object> of EVIL! </object>
      <iframe src="evil-site"></iframe>
      <form action="evil-site">
        Password: <input type="password" name="password">
      </form>
      <blink>annoying EVIL!</blink>
      <a href="evil-site">spam spam SPAM!</a>
      <image src="evil!">
    </body>
   </html>"""  # example from lxml: /usr/share/doc/python-lxml-doc/html/lxmlhtml.html#cleaning-up-html

    EVIL_HTML2 = """<p style='display: None; test: blah; background: url(: alert()); color: blue;'>test <strong>retest</strong><br><span style="background-color: (alert('bouh')); titi; color: #cf2828; font-size: 3px; direction: !important; color: red; color: red !important; font-size: 100px       !important; font-size: 100px  ! important; font-size: 100%; font-size: 100ox; font-size: 100px; font-size: 100;;;; font-size: 100 %; color: 100 px 1.7em; color: rgba(0, 0, 0, 0.1); color: rgb(35,79,255); background-color: no-repeat; background-color: :alert(1); color: (alert('XSS')); color: (window.location='http://example.org/'); color: url(:window.location='http://example.org/'); "> toto </span></p>"""

    def setUp(self):
        self.host = helpers.FakeSAT()
        reload(plugin_misc_text_syntaxes)  # reload the plugin to avoid conflict error
        self.text_syntaxes = plugin_misc_text_syntaxes.TextSyntaxes(self.host)

    def test_xhtml_sanitise(self):
        expected = u"""<div>
      <style>/* deleted */</style>
    <body>
      <a href="">a link</a>
      <a href="#">another link</a>
      <p>a paragraph</p>
      <div style="">secret EVIL!</div>
       of EVIL!
        Password:
      annoying EVIL!
      <a href="evil-site">spam spam SPAM!</a>
      <img src="evil!">
    </img></body>
   </div>"""

        d = self.text_syntaxes.cleanXHTML(self.EVIL_HTML1)
        d.addCallback(self.assertEqualXML, expected, ignore_blank=True)
        return d

    def test_styles_sanitise(self):
        expected = u"""<p style="color: blue">test <strong>retest</strong><br/><span style="color: #cf2828; font-size: 3px; color: red; color: red !important; font-size: 100px       !important; font-size: 100%; font-size: 100px; font-size: 100; font-size: 100 %; color: rgba(0, 0, 0, 0.1); color: rgb(35,79,255); background-color: no-repeat"> toto </span></p>"""

        d = self.text_syntaxes.cleanXHTML(self.EVIL_HTML2)
        d.addCallback(self.assertEqualXML, expected)
        return d

    def test_html2text(self):
        """Check that html2text is not inserting \n in the middle of that link.
        By default lines are truncated after the 79th characters."""
        source = '<img src="http://sat.goffi.org/static/images/screenshots/libervia/libervia_discussions.png" alt="sat"/>'
        expected = "![sat](http://sat.goffi.org/static/images/screenshots/libervia/libervia_discussions.png)"
        try:
            d = self.text_syntaxes.convert(
                source,
                self.text_syntaxes.SYNTAX_XHTML,
                self.text_syntaxes.SYNTAX_MARKDOWN,
            )
        except plugin_misc_text_syntaxes.UnknownSyntax:
            raise SkipTest("Markdown syntax is not available.")
        d.addCallback(self.assertEqual, expected)
        return d

    def test_removeXHTMLMarkups(self):
        expected = u""" a link another link a paragraph secret EVIL! of EVIL! Password: annoying EVIL! spam spam SPAM! """
        result = self.text_syntaxes._removeMarkups(self.EVIL_HTML1)
        self.assertEqual(re.sub(r"\s+", " ", result).rstrip(), expected.rstrip())

        expected = u"""test retest toto"""
        result = self.text_syntaxes._removeMarkups(self.EVIL_HTML2)
        self.assertEqual(re.sub(r"\s+", " ", result).rstrip(), expected.rstrip())
