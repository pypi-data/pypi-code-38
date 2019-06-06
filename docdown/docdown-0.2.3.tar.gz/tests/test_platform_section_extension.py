# -*- coding: utf-8 -*-

"""
test_note_blocks_extension
----------------------------------

Tests for `docdown.note_blocks` module.
"""

from __future__ import absolute_import, print_function, unicode_literals

import unittest

import markdown


class PlatformSectionExtensionTest(unittest.TestCase):
    """
    Integration test with markdown for :class:`docdown.platform_section.PlatformSectionExtension`
    """
    MARKDOWN_EXTENSIONS = ['docdown.platform_section']

    def build_config_for_platform_section(self, section):
        return {
            'docdown.platform_section': {
                'platform_section': section,
            }
        }

    def test_section_does_not_match(self):
        text = ('@![asdf]\n'
                'some content\nnot shown\n\n'
                '!@')

        html = markdown.markdown(
            text,
            extension_configs=self.build_config_for_platform_section('Android'),
            extensions=self.MARKDOWN_EXTENSIONS,
            output_format='html5'
        )
        expected_output = ''
        self.assertEqual(expected_output, html)

    def test_section_does_match(self):
        text = ('@![asdf]\n'
                'some content\nshown\n\n'
                '!@ \n')

        html = markdown.markdown(
            text,
            extension_configs=self.build_config_for_platform_section('asdf'),
            extensions=self.MARKDOWN_EXTENSIONS,
            output_format='html5'
        )
        expected_output = '<p>some content\nshown</p>'
        self.assertEqual(expected_output, html)

    def test_section_markdown_case_insensitive(self):
        text = ('@![ASDF]\n'
                'some content\nshown\n\n'
                '!@\n')

        html = markdown.markdown(
            text,
            extension_configs=self.build_config_for_platform_section('asdf'),
            extensions=self.MARKDOWN_EXTENSIONS,
            output_format='html5'
        )
        expected_output = '<p>some content\nshown</p>'
        self.assertEqual(expected_output, html)

    def test_section_config_case_insensitive(self):
        text = ('@![asdf]\n'
                'some content\nshown\n\n'
                '!@ \n')

        html = markdown.markdown(
            text,
            extension_configs=self.build_config_for_platform_section('ASDF'),
            extensions=self.MARKDOWN_EXTENSIONS,
            output_format='html5'
        )
        expected_output = '<p>some content\nshown</p>'
        self.assertEqual(expected_output, html)

    def test_multiple_platforms_section(self):
        text = ('@![asdf,QwErTy]\n'
                'some content\nshown\n\n'
                '!@\n')

        html = markdown.markdown(
            text,
            extension_configs=self.build_config_for_platform_section('qwerty'),
            extensions=self.MARKDOWN_EXTENSIONS,
            output_format='html5'
        )
        expected_output = '<p>some content\nshown</p>'
        self.assertEqual(expected_output, html)

    def test_platform_sections_with_spaces(self):
        text = ('@![asdf, qwerty]\n'
                'some content\nshown\n\n'
                '!@\n')

        html = markdown.markdown(
            text,
            extension_configs=self.build_config_for_platform_section('qwerty'),
            extensions=self.MARKDOWN_EXTENSIONS,
            output_format='html5'
        )
        expected_output = '<p>some content\nshown</p>'
        self.assertEqual(expected_output, html)

    def test_platform_section_with_space(self):
        text = ('@![asdf, qwerty, another platform]\n'
                'some content\nshown\n\n'
                '!@\n'
                '@![another platform]\n'
                'some extra content\nshown\n\n'
                '!@\n')

        html = markdown.markdown(
            text,
            extension_configs=self.build_config_for_platform_section('another platform'),
            extensions=self.MARKDOWN_EXTENSIONS,
            output_format='html5'
        )
        expected_output = '<p>some content\nshown</p>\n<p>some extra content\nshown</p>'
        self.assertEqual(expected_output, html)

    def test_multiple_sections(self):
        text = ('@![asdf,QwErTy]\n'
                'some content\nnot shown\n\n'
                '!@\n'
                '\n'
                '@![zxcv]\n'
                'some content\nshown\n\n'
                '!@\n')

        html = markdown.markdown(
            text,
            extension_configs=self.build_config_for_platform_section('zxcv'),
            extensions=self.MARKDOWN_EXTENSIONS,
            output_format='html5'
        )
        expected_output = '<p>some content\nshown</p>'
        self.assertEqual(expected_output, html)

    def test_section_with_code_snippet(self):
        text = ('@![Android]\n'
                'some Android content shown\n\n'
                '``` java\n'
                'String java = "asdf";\n'
                '```\n'
                '!@\n')

        html = markdown.markdown(
            text,
            extension_configs=self.build_config_for_platform_section('Android'),
            extensions=self.MARKDOWN_EXTENSIONS,
            output_format='html5'
        )
        expected_output = '<p>some Android content shown</p>\n<p><code>java\nString java = "asdf";</code></p>'
        self.assertEqual(expected_output, html)

    def test_multiple_sections_with_code_snippet(self):
        text = ('@![iOS]\n'
                'some iOS content not shown\n\n'
                '!@\n'
                '\n'
                '@![Android]\n'
                'some Android content shown\n\n'
                '``` java\n'
                'String java = "asdf";\n'
                '```\n'
                '!@\n')

        html = markdown.markdown(
            text,
            extension_configs=self.build_config_for_platform_section('Android'),
            extensions=self.MARKDOWN_EXTENSIONS,
            output_format='html5'
        )
        expected_output = '<p>some Android content shown</p>\n<p><code>java\nString java = "asdf";</code></p>'
        self.assertEqual(expected_output, html)

    def test_inline_platform_section(self):
        text = ('### 1. Creating an App Service Manifest\n'
                'The first step to publishing is to create an @![iOS]`SDLAppServiceManifest`!@ @![Android, JavaSE, JavaEE]`AppServiceManifest`!@ object.\n')

        html = markdown.markdown(
            text,
            extension_configs=self.build_config_for_platform_section('Android'),
            extensions=self.MARKDOWN_EXTENSIONS,
            output_format='html5'
        )
        expected_output = '<h3>1. Creating an App Service Manifest</h3>\n<p>The first step to publishing is to create an  <code>AppServiceManifest</code> object.</p>'
        self.assertEqual(expected_output, html)

        html = markdown.markdown(
            text,
            extension_configs=self.build_config_for_platform_section('JavaEE'),
            extensions=self.MARKDOWN_EXTENSIONS,
            output_format='html5'
        )
        expected_output = '<h3>1. Creating an App Service Manifest</h3>\n<p>The first step to publishing is to create an  <code>AppServiceManifest</code> object.</p>'
        self.assertEqual(expected_output, html)

        html = markdown.markdown(
            text,
            extension_configs=self.build_config_for_platform_section('iOS'),
            extensions=self.MARKDOWN_EXTENSIONS,
            output_format='html5'
        )
        expected_output = '<h3>1. Creating an App Service Manifest</h3>\n<p>The first step to publishing is to create an <code>SDLAppServiceManifest</code>  object.</p>'
        self.assertEqual(expected_output, html)
