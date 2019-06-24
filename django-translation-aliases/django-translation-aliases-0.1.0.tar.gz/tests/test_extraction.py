# -*- encoding: utf-8 -*-
from __future__ import unicode_literals

import os
import re
import time
import warnings
from unittest import skipUnless

from django.core import management
from django.core.management.utils import find_command
from django.test import SimpleTestCase
from django.utils import six
from django.utils.encoding import force_text
from django.utils.six import StringIO
from django.utils.translation import TranslatorCommentWarning

from .base import POFileAssertionMixin
from .base import RunInTmpDirMixin

LOCALE = 'de'
has_xgettext = find_command('xgettext')


@skipUnless(has_xgettext, 'xgettext is mandatory for extraction tests')
class ExtractorTests(POFileAssertionMixin, RunInTmpDirMixin, SimpleTestCase):

    work_subdir = 'commands'

    PO_FILE = 'locale/%s/LC_MESSAGES/django.po' % LOCALE

    def _run_makemessages(self, **options):
        os.chdir(self.test_dir)
        out = StringIO()
        management.call_command('makemessages', locale=[LOCALE], verbosity=2, stdout=out, **options)
        output = out.getvalue()
        self.assertTrue(os.path.exists(self.PO_FILE))
        with open(self.PO_FILE, 'r') as fp:
            po_contents = fp.read()
        return output, po_contents

    def assertMsgIdPlural(self, msgid, haystack, use_quotes=True):
        return self._assertPoKeyword('msgid_plural', msgid, haystack, use_quotes=use_quotes)

    def assertMsgStr(self, msgstr, haystack, use_quotes=True):
        return self._assertPoKeyword('msgstr', msgstr, haystack, use_quotes=use_quotes)

    def assertNotMsgId(self, msgid, s, use_quotes=True):
        if use_quotes:
            msgid = '"%s"' % msgid
        msgid = re.escape(msgid)
        return self.assertTrue(not re.search('^msgid %s' % msgid, s, re.MULTILINE))

    def _assertPoLocComment(self, assert_presence, po_filename, line_number, *comment_parts):
        with open(po_filename, 'r') as fp:
            po_contents = force_text(fp.read())
        if os.name == 'nt':
            # #: .\path\to\file.html:123
            cwd_prefix = '%s%s' % (os.curdir, os.sep)
        else:
            # #: path/to/file.html:123
            cwd_prefix = ''

        path = os.path.join(cwd_prefix, *comment_parts)
        parts = [path]

        if isinstance(line_number, six.string_types):
            line_number = self._get_token_line_number(path, line_number)
        if line_number is not None:
            parts.append(':%d' % line_number)

        needle = ''.join(parts)
        pattern = re.compile(r'^\#\:.*' + re.escape(needle), re.MULTILINE)
        if assert_presence:
            return self.assertRegex(po_contents, pattern, '"%s" not found in final .po file.' % needle)
        else:
            return self.assertNotRegex(po_contents, pattern, '"%s" shouldn\'t be in final .po file.' % needle)

    def _get_token_line_number(self, path, token):
        with open(path) as f:
            for line, content in enumerate(f, 1):
                if token in force_text(content):
                    return line
        self.fail("The token '%s' could not be found in %s, please check the test config" % (token, path))

    def assertLocationCommentPresent(self, po_filename, line_number, *comment_parts):
        r"""
        self.assertLocationCommentPresent('django.po', 42, 'dirA', 'dirB', 'foo.py')

        verifies that the django.po file has a gettext-style location comment of the form

        `#: dirA/dirB/foo.py:42`

        (or `#: .\dirA\dirB\foo.py:42` on Windows)

        None can be passed for the line_number argument to skip checking of
        the :42 suffix part.
        A string token can also be passed as line_number, in which case it
        will be searched in the template, and its line number will be used.
        A msgid is a suitable candidate.
        """
        return self._assertPoLocComment(True, po_filename, line_number, *comment_parts)

    def assertLocationCommentNotPresent(self, po_filename, line_number, *comment_parts):
        """Check the opposite of assertLocationComment()"""
        return self._assertPoLocComment(False, po_filename, line_number, *comment_parts)

    def assertRecentlyModified(self, path):
        """
        Assert that file was recently modified (modification time was less than 10 seconds ago).
        """
        delta = time.time() - os.stat(path).st_mtime
        self.assertLess(delta, 10, "%s was recently modified" % path)

    def assertNotRecentlyModified(self, path):
        """
        Assert that file was not recently modified (modification time was more than 10 seconds ago).
        """
        delta = time.time() - os.stat(path).st_mtime
        self.assertGreater(delta, 10, "%s wasn't recently modified" % path)


class BasicExtractorTests(ExtractorTests):
    def test_blocktranslate_trimmed(self):
        management.call_command('makemessages', locale=[LOCALE], verbosity=0)
        self.assertTrue(os.path.exists(self.PO_FILE))
        with open(self.PO_FILE, 'r') as fp:
            po_contents = force_text(fp.read())
            # should not be trimmed
            self.assertNotMsgId('Text with a few line breaks.', po_contents)
            # should be trimmed
            self.assertMsgId("Again some text with a few line breaks, this time should be trimmed.", po_contents)
        # #21406 -- Should adjust for eaten line numbers
        self.assertMsgId("Get my line number", po_contents)
        self.assertLocationCommentPresent(self.PO_FILE, 'Get my line number', 'templates', 'test.html')

    def test_template_message_context_extractor(self):
        """
        Message contexts are correctly extracted for the {% translate %} and
        {% blocktranslate %} template tags (#14806).
        """
        management.call_command('makemessages', locale=[LOCALE], verbosity=0)
        self.assertTrue(os.path.exists(self.PO_FILE))
        with open(self.PO_FILE, 'r') as fp:
            po_contents = force_text(fp.read())
            # {% translate %}
            self.assertIn('msgctxt "Special translate context #1"', po_contents)
            self.assertMsgId("Translatable literal #7a", po_contents)
            self.assertIn('msgctxt "Special translate context #2"', po_contents)
            self.assertMsgId("Translatable literal #7b", po_contents)
            self.assertIn('msgctxt "Special translate context #3"', po_contents)
            self.assertMsgId("Translatable literal #7c", po_contents)

            # {% translate %} with a filter
            for minor_part in 'abcdefgh':  # Iterate from #7.1a to #7.1h template markers
                self.assertIn('msgctxt "context #7.1{}"'.format(minor_part), po_contents)
                self.assertMsgId('Translatable literal #7.1{}'.format(minor_part), po_contents)

            # {% blocktranslate %}
            self.assertIn('msgctxt "Special blocktranslate context #1"', po_contents)
            self.assertMsgId("Translatable literal #8a", po_contents)
            self.assertIn('msgctxt "Special blocktranslate context #2"', po_contents)
            self.assertMsgId("Translatable literal #8b-singular", po_contents)
            self.assertIn("Translatable literal #8b-plural", po_contents)
            self.assertIn('msgctxt "Special blocktranslate context #3"', po_contents)
            self.assertMsgId("Translatable literal #8c-singular", po_contents)
            self.assertIn("Translatable literal #8c-plural", po_contents)
            self.assertIn('msgctxt "Special blocktranslate context #4"', po_contents)
            self.assertMsgId("Translatable literal #8d %(a)s", po_contents)

    def test_context_in_single_quotes(self):
        management.call_command('makemessages', locale=[LOCALE], verbosity=0)
        self.assertTrue(os.path.exists(self.PO_FILE))
        with open(self.PO_FILE, 'r') as fp:
            po_contents = force_text(fp.read())
            # {% translate %}
            self.assertIn('msgctxt "Context wrapped in double quotes"', po_contents)
            self.assertIn('msgctxt "Context wrapped in single quotes"', po_contents)

            # {% blocktranslate %}
            self.assertIn('msgctxt "Special blocktranslate context wrapped in double quotes"', po_contents)
            self.assertIn('msgctxt "Special blocktranslate context wrapped in single quotes"', po_contents)

    def test_template_comments(self):
        """Template comment tags on the same line of other constructs (#19552)"""
        # Test detection/end user reporting of old, incorrect templates
        # translator comments syntax
        with warnings.catch_warnings(record=True) as ws:
            warnings.simplefilter('always')
            management.call_command('makemessages', locale=[LOCALE], extensions=['thtml'], verbosity=0)
            self.assertEqual(len(ws), 3)
            for w in ws:
                self.assertTrue(issubclass(w.category, TranslatorCommentWarning))
            self.assertRegex(
                str(ws[0].message),
                r"The translator-targeted comment 'Translators: ignored i18n "
                r"comment #1' \(file templates[/\\]comments.thtml, line 4\) "
                r"was ignored, because it wasn't the last item on the line\."
            )
            self.assertRegex(
                str(ws[1].message),
                r"The translator-targeted comment 'Translators: ignored i18n "
                r"comment #3' \(file templates[/\\]comments.thtml, line 6\) "
                r"was ignored, because it wasn't the last item on the line\."
            )
            self.assertRegex(
                str(ws[2].message),
                r"The translator-targeted comment 'Translators: ignored i18n "
                r"comment #4' \(file templates[/\\]comments.thtml, line 8\) "
                r"was ignored, because it wasn't the last item on the line\."
            )
        # Now test .po file contents
        self.assertTrue(os.path.exists(self.PO_FILE))
        with open(self.PO_FILE, 'r') as fp:
            po_contents = force_text(fp.read())

            self.assertMsgId('Translatable literal #9a', po_contents)
            self.assertNotIn('ignored comment #1', po_contents)

            self.assertNotIn('Translators: ignored i18n comment #1', po_contents)
            self.assertMsgId("Translatable literal #9b", po_contents)

            self.assertNotIn('ignored i18n comment #2', po_contents)
            self.assertNotIn('ignored comment #2', po_contents)
            self.assertMsgId('Translatable literal #9c', po_contents)

            self.assertNotIn('ignored comment #3', po_contents)
            self.assertNotIn('ignored i18n comment #3', po_contents)
            self.assertMsgId('Translatable literal #9d', po_contents)

            self.assertNotIn('ignored comment #4', po_contents)
            self.assertMsgId('Translatable literal #9e', po_contents)
            self.assertNotIn('ignored comment #5', po_contents)

            self.assertNotIn('ignored i18n comment #4', po_contents)
            self.assertMsgId('Translatable literal #9f', po_contents)
            self.assertIn('#. Translators: valid i18n comment #5', po_contents)

            self.assertMsgId('Translatable literal #9g', po_contents)
            self.assertIn('#. Translators: valid i18n comment #6', po_contents)
            self.assertMsgId('Translatable literal #9h', po_contents)
            self.assertIn('#. Translators: valid i18n comment #7', po_contents)
            self.assertMsgId('Translatable literal #9i', po_contents)

            self.assertRegex(po_contents, r'#\..+Translators: valid i18n comment #8')
            self.assertRegex(po_contents, r'#\..+Translators: valid i18n comment #9')
            self.assertMsgId("Translatable literal #9j", po_contents)
