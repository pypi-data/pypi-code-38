# -*- coding: utf-8 -*-

"""
test_sequence_diagram_extension
----------------------------------

Tests for `docdown.sequence` module.
"""

from __future__ import absolute_import, unicode_literals, print_function

import markdown
import unittest

from docdown.sequence import SequenceDiagramBlockPreprocessor


class SequenceDiagramExtensionTest(unittest.TestCase):
    """
    Primarily integration tests for the SequenceDiagramExtension
    """

    EXTENSION_CONFIGS = {
        'docdown.sequence': {
            'media_url': 'http://example.com/',
            'prefix': ('<div class="visual-link-wrapper"><a href="#" data-src="{image_url}" class="visual-link">'
                       '<div class="visual-link__body"><div class="t-h6 visual-link__title">{title}</div>'
                       '<p class="t-default">'),
            'postfix': ('</p></div><div class="visual-link__link fx-wrapper fx-s-between fx-a-center">'
                        '<span class="fc-theme">View Diagram</span>'
                        '<span class="icon">{{% svg "standard/icon-visual" %}}</span></div></a></div>\n'
                        '<img class="visual-print-image" src="{image_url}">'),
        }
    }

    MARKDOWN_EXTENSIONS = ['docdown.sequence']

    def test_sequence_diagram_render_stringformatadapter_with_media_url_and_relative_image_path(self):
        """
        Test a single sequence diagram renders correctly.

        Render a single sequence diagram using the default template_adapter, which is
        :class:`docdown.template_adapters.StringFormatAdapter` with a media_url specified and a relative
        path given for the image.
        """
        text = ("# Sequence Diagrams\n"
                "|||\n"
                "Activate App\n"
                "![Activate App Sequence Diagram](./assets/ActivateAppSuccessfulResume.png)\n"
                "|||")

        html = markdown.markdown(
            text,
            extensions=self.MARKDOWN_EXTENSIONS,
            extension_configs=self.EXTENSION_CONFIGS,
            output_format='html5'
        )

        expected_output = (
            '<h1>Sequence Diagrams</h1>\n'
            '<div class="visual-link-wrapper">'
            '<a href="#" data-src="http://example.com/assets/ActivateAppSuccessfulResume.png" class="visual-link">'
            '<div class="visual-link__body"><div class="t-h6 visual-link__title">Activate App Sequence Diagram</div>'
            '<p class="t-default">\n\n'
            '<p>Activate App</p>\n'
            '</p></div><div class="visual-link__link fx-wrapper fx-s-between fx-a-center">'
            '<span class="fc-theme">View Diagram</span><span class="icon">{% svg "standard/icon-visual" %}</span>'
            '</div></a></div>\n'
            '<img class="visual-print-image" src="http://example.com/assets/ActivateAppSuccessfulResume.png">')

        self.assertEqual(html, expected_output)

    def test_sequence_diagram_default_media_url(self):
        """
        Test that the URL gets the default `.` prepended, making it a relative path
        """
        config = {
            'docdown.sequence': {
                'prefix': ('<div class="visual-link-wrapper"><a href="#" data-src="{image_url}" class="visual-link">'
                           '<div class="visual-link__body"><div class="t-h6 visual-link__title">{title}</div>'
                           '<p class="t-default">'),
                'postfix': ('</p></div><div class="visual-link__link fx-wrapper fx-s-between fx-a-center">'
                            '<span class="fc-theme">View Diagram</span>'
                            '<span class="icon">{{% svg "standard/icon-visual" %}}</span></div></a></div>\n'
                            '<img class="visual-print-image" src="{image_url}">'),
            }
        }
        text = ("# Sequence Diagrams\n"
                "|||\n"
                "Activate App\n"
                "![Activate App Sequence Diagram](/assets/ActivateAppSuccessfulResume.png)\n"
                "|||")

        html = markdown.markdown(
            text,
            extensions=self.MARKDOWN_EXTENSIONS,
            extension_configs=config,
            output_format='html5'
        )

        expected_output = (
            '<h1>Sequence Diagrams</h1>\n'
            '<div class="visual-link-wrapper">'
            '<a href="#" data-src="./assets/ActivateAppSuccessfulResume.png" class="visual-link">'
            '<div class="visual-link__body"><div class="t-h6 visual-link__title">Activate App Sequence Diagram</div>'
            '<p class="t-default">\n\n'
            '<p>Activate App</p>\n'
            '</p></div><div class="visual-link__link fx-wrapper fx-s-between fx-a-center">'
            '<span class="fc-theme">View Diagram</span><span class="icon">{% svg "standard/icon-visual" %}</span>'
            '</div></a></div>\n'
            '<img class="visual-print-image" src="./assets/ActivateAppSuccessfulResume.png">')

        self.assertEqual(html, expected_output)

    def test_multiple_sequence_diagrams(self):
        """
        Test that multiple sequence diagrams in a row render correctly
        """
        text = ('# Sequence Diagrams\n'
               '|||\n'
               'Activate App 1\n'
               '![Activate App Sequence Diagram 1](./assets/ActivateAppSuccessfulResume.png)\n'
               '|||\n\n'
               '|||\n'
               'Activate App 2\n'
               '![Activate App Sequence Diagram 2](./assets/ActivateAppSuccessfulResume.png)\n'
               '|||')

        html = markdown.markdown(
            text,
            extensions=self.MARKDOWN_EXTENSIONS,
            extension_configs=self.EXTENSION_CONFIGS,
            output_format='html5'
        )

        expected_output = (
            '<h1>Sequence Diagrams</h1>\n'
            '<div class="visual-link-wrapper">'
            '<a href="#" data-src="http://example.com/assets/ActivateAppSuccessfulResume.png" class="visual-link">'
            '<div class="visual-link__body"><div class="t-h6 visual-link__title">Activate App Sequence Diagram 1</div>'
            '<p class="t-default">\n\n<p>Activate App 1</p>\n</p></div>'
            '<div class="visual-link__link fx-wrapper fx-s-between fx-a-center">'
            '<span class="fc-theme">View Diagram</span><span class="icon">{% svg "standard/icon-visual" %}</span></div>'
            '</a></div>\n'
            '<img class="visual-print-image" src="http://example.com/assets/ActivateAppSuccessfulResume.png">\n\n'
            '<div class="visual-link-wrapper">'
            '<a href="#" data-src="http://example.com/assets/ActivateAppSuccessfulResume.png" class="visual-link">'
            '<div class="visual-link__body">'
            '<div class="t-h6 visual-link__title">Activate App Sequence Diagram 2</div><p class="t-default">\n\n'
            '<p>Activate App 2</p>\n</p></div>'
            '<div class="visual-link__link fx-wrapper fx-s-between fx-a-center">'
            '<span class="fc-theme">View Diagram</span>'
            '<span class="icon">{% svg "standard/icon-visual" %}</span></div></a></div>\n'
            '<img class="visual-print-image" src="http://example.com/assets/ActivateAppSuccessfulResume.png">')

        self.assertEqual(html, expected_output)

    def test_sequence_diagram_with_protocol_relative_path(self):
        """
        Test a single sequence diagram renders correctly.

        Render a single sequence diagram using the default template_adapter, which is
        :class:`docdown.template_adapters.StringFormatAdapter` with a media_url specified and a relative
        path given for the image.
        """
        text = ("# Sequence Diagrams\n"
                "|||\n"
                "Activate App\n"
                "![Activate App Sequence Diagram](//example.org/assets/ActivateAppSuccessfulResume.png)\n"
                "|||")

        html = markdown.markdown(
            text,
            extensions=self.MARKDOWN_EXTENSIONS,
            extension_configs=self.EXTENSION_CONFIGS,
            output_format='html5'
        )

        expected_output = (
            '<h1>Sequence Diagrams</h1>\n'
            '<div class="visual-link-wrapper">'
            '<a href="#" data-src="//example.org/assets/ActivateAppSuccessfulResume.png" class="visual-link">'
            '<div class="visual-link__body"><div class="t-h6 visual-link__title">Activate App Sequence Diagram</div>'
            '<p class="t-default">\n\n'
            '<p>Activate App</p>\n'
            '</p></div><div class="visual-link__link fx-wrapper fx-s-between fx-a-center">'
            '<span class="fc-theme">View Diagram</span><span class="icon">{% svg "standard/icon-visual" %}</span>'
            '</div></a></div>\n'
            '<img class="visual-print-image" src="//example.org/assets/ActivateAppSuccessfulResume.png">')

        self.assertEqual(html, expected_output)

    def test_sequence_diagram_without_title_has_default(self):
        """
        Test that if there is no title for the sequence diagram that it defaults to the title `Sequence Diagram`
        """
        text = ("# Sequence Diagrams\n"
                "|||\n"
                "Activate App\n"
                "![](./assets/ActivateAppSuccessfulResume.png)\n"
                "|||")

        html = markdown.markdown(
            text,
            extensions=self.MARKDOWN_EXTENSIONS,
            extension_configs=self.EXTENSION_CONFIGS,
            output_format='html5'
        )

        expected_output = (
            '<h1>Sequence Diagrams</h1>\n'
            '<div class="visual-link-wrapper">'
            '<a href="#" data-src="http://example.com/assets/ActivateAppSuccessfulResume.png" class="visual-link">'
            '<div class="visual-link__body"><div class="t-h6 visual-link__title">Sequence Diagram</div>'
            '<p class="t-default">\n\n'
            '<p>Activate App</p>\n'
            '</p></div><div class="visual-link__link fx-wrapper fx-s-between fx-a-center">'
            '<span class="fc-theme">View Diagram</span><span class="icon">{% svg "standard/icon-visual" %}</span>'
            '</div></a></div>\n'
            '<img class="visual-print-image" src="http://example.com/assets/ActivateAppSuccessfulResume.png">')

        self.assertEqual(html, expected_output)


class SequenceDiagramBlockPreprocessorTest(unittest.TestCase):
    """
    Specifically test the preprocessor used by SequenceDiagramExtension.
    """

    PREFIX_TEMPLATE = ('<div class="visual-link-wrapper"><a href="#" data-src="{image_url}" class="visual-link">'
                       '<div class="visual-link__body"><div class="t-h6 visual-link__title">{title}</div>'
                       '<p class="t-default">')

    POSTFIX_TEMPLATE = ('</p></div><div class="visual-link__link fx-wrapper fx-s-between fx-a-center">'
                        '<span class="fc-theme">View Diagram</span>'
                        '<span class="icon">{{% svg "standard/icon-visual" %}}</span></div></a></div>\n'
                        '<img class="visual-print-image" src="{image_url}">')
    TEMPLATE_ADAPTER = 'docdown.template_adapters.StringFormatAdapter'

    def test_run_method_with_media_url_prefix_and_postfix_set(self):
        """
        When media_url is passed in, urls should be replaced with the media_url url.
        Placeholders should get properly replaced.  Each line in list of text should be treated as new line.
        """
        processor = SequenceDiagramBlockPreprocessor(
            media_url='http://example.com/',
            prefix=self.PREFIX_TEMPLATE,
            postfix=self.POSTFIX_TEMPLATE,
            template_adapter=self.TEMPLATE_ADAPTER,
            markdown_instance=markdown.Markdown())

        text = ("# Sequence Diagrams",
                "|||",
                "Activate App",
                "![Activate App Sequence Diagram](./assets/ActivateAppSuccessfulResume.png)",
                "|||",)
        processed = processor.run(text)

        # placeholder pipes are replaced with a code
        # each element in the list is treated as a line and so a newline is inserted
        # adding an extra empty line between each element
        expected = ['# Sequence Diagrams', '',
                '\x02wzxhzdk:0\x03',
                '',
                'Activate App', '',
                '\x02wzxhzdk:1\x03',
                ''
                ]

        self.assertEqual(processed, expected)

    def test_run_method_with_default_settings(self):
        """
        If no media_url and a relative file path is given, the leading ./ should be stripped from
        the path to the sequence diagram image.
        Placeholders should get properly replaced.  Each line in list of text should be treated as new line.
        """
        processor = SequenceDiagramBlockPreprocessor(markdown_instance=markdown.Markdown())
        text = ("# Sequence Diagrams",
                "|||",
                "Activate App",
                "![Activate App Sequence Diagram](./assets/ActivateAppSuccessfulResume.png)",
                "|||",)
        processed = processor.run(text)

        # placeholder pipes are replaced with a code
        # each element in the list is treated as a line and so a newline is inserted
        # adding an extra empty line between each element
        expected = ['# Sequence Diagrams', '',
                '\x02wzxhzdk:0\x03',
                '',
                'Activate App', '',
                '\x02wzxhzdk:1\x03',
                ''
                ]
        self.assertEqual(processed, expected)
