# -*- coding: utf-8 -*-

"""
test_include_extension
----------------------------------

Tests for `docdown.include` module.
"""

from __future__ import absolute_import, unicode_literals, print_function

import markdown
import unittest

import os

from docdown.include import IncludePreprocessor

class IncludeExtensionTest(unittest.TestCase):
    """
    Test the IncludeExtension.

    Primarily runs as an integration test by using it with markdown.  This test includes the `fenced_code`
    extension because the current output from the preprocessor assumes the `fenced_code` extension will
    be in use.
    """
    # TODO: This test appears to be relying on behavior from another extension
    # due to the expected output vs what is really being output... nl2br and fenced_code
    # The extension should probably check for them, or at least document that they are needed,
    # if they are expected to always be there.
    # ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
    # CURRENT_DIR = os.path.join(ROOT_DIR, 'test_files')
    ASSET_DIR = 'assets'

    TESTS_DIR = os.path.dirname(os.path.abspath(__file__))
    ROOT_DIR = os.path.join(TESTS_DIR, 'test_files')
    CURRENT_DIR = os.path.join(ROOT_DIR, 'deep_assets')

    MARKDOWN_EXTENSIONS = [
        'markdown.extensions.fenced_code',
        'docdown.include']

    EXTENSION_CONFIGS = {
        'docdown.include': {
            'asset_directory': ASSET_DIR,
            'current_directory': CURRENT_DIR,
            'root_directory': ROOT_DIR,
            'extension_map': {
                '.m': '.c',
            }
        }
    }

    def test_missing_file(self):
        """
        Test where the specified file does not exist.
        """
        text = ('Test File:\n' '+++ not_here.md')

        html = markdown.markdown(
            text,
            extensions=self.MARKDOWN_EXTENSIONS,
            extension_configs=self.EXTENSION_CONFIGS,
            output_format='html5'
        )

        expected_output = '<p>Test File:</p>'
        self.assertEqual(html, expected_output)

    def test_json(self):
        text = ('Test JSON:\n'
                '+++ test.json')

        html = markdown.markdown(
            text,
            extensions=self.MARKDOWN_EXTENSIONS,
            extension_configs=self.EXTENSION_CONFIGS,
            output_format='html5'
        )

        expected_output = ('<p>Test JSON:</p>\n'
                           '<pre><code class="json">{&quot;test&quot;: &quot;Deep content&quot;}\n'
                           '</code></pre>')
        self.assertEqual(html, expected_output)

    def test_nested_json(self):
        """
        Test JSON where filename is lower in path within the assets dir.
        """
        text = ('Test JSON:\n'
                '+++ subdir/test.json')

        html = markdown.markdown(
            text,
            extensions=self.MARKDOWN_EXTENSIONS,
            extension_configs=self.EXTENSION_CONFIGS,
            output_format='html5'
        )

        expected_output = ('<p>Test JSON:</p>\n'
                           '<pre><code class="json">{&quot;test&quot;: &quot;subdir content&quot;}\n'
                           '</code></pre>')
        self.assertEqual(html, expected_output)

    def test_json_directory_rollup(self):
        """
        Test JSON where we have rolled up one level in the dir tree looking in `ROOT_DIR/test_files/assets/` after not
        finding the file in `ROOT_DIR/test_files/deep_assets/assets/`
        """
        EXTENSION_CONFIGS = {
            'docdown.include': {
                'asset_directory': self.ASSET_DIR,
                'current_directory': os.path.join(self.ROOT_DIR, 'test_files', 'deep_assets'),
                'root_directory': self.ROOT_DIR,
                'extension_map': {
                    '.m': '.c',
                }
            }
        }

        text = ('Test JSON:\n'
                '+++ subdir/test.json')

        html = markdown.markdown(
            text,
            extensions=self.MARKDOWN_EXTENSIONS,
            extension_configs=self.EXTENSION_CONFIGS,
            output_format='html5'
        )

        expected_output = ('<p>Test JSON:</p>\n'
                           '<pre><code class="json">{&quot;test&quot;: &quot;subdir content&quot;}\n'
                           '</code></pre>')
        self.assertEqual(html, expected_output)

    def test_html(self):
        text = ('Test HTML:\n'
                '+++ test.html')

        html = markdown.markdown(
            text,
            extensions=self.MARKDOWN_EXTENSIONS,
            extension_configs=self.EXTENSION_CONFIGS,
            output_format='html5'
        )

        expected_output = (
            '<p>Test HTML:</p>\n'
            '<pre><code class="html">&lt;html&gt;&lt;head&gt;&lt;/head&gt;&lt;'
            'body&gt;&lt;h1&gt;Test&lt;/h1&gt;&lt;/body&gt;&lt;/html&gt;\n'
            '</code></pre>')

        self.assertEqual(html, expected_output)

    def test_js(self):
        text = ('Test JS:\n'
                '+++ test.js')

        html = markdown.markdown(
            text,
            extensions=self.MARKDOWN_EXTENSIONS,
            extension_configs=self.EXTENSION_CONFIGS,
            output_format='html5'
        )

        expected_output = (
            '<p>Test JS:</p>\n'
            '''<pre><code class="js">alert('test');\n'''
            '</code></pre>')
        self.assertEqual(html, expected_output)

    def test_css(self):
        text = ('Test CSS:\n'
                '+++ test.css')

        html = markdown.markdown(
            text,
            extensions=self.MARKDOWN_EXTENSIONS,
            extension_configs=self.EXTENSION_CONFIGS,
            output_format='html5'
        )

        expected_output = ('<p>Test CSS:</p>\n'
                           '<pre><code class="css">.lime{\n'
                           '  color: #75D366;\n'
                           '}\n'
                           '</code></pre>')

        self.assertEqual(html, expected_output)

    def test_obj_c_with_mapped_extension(self):
        text = ('Test Objective C:\n'
                '+++ test.m')

        html = markdown.markdown(
            text,
            extensions=self.MARKDOWN_EXTENSIONS,
            extension_configs=self.EXTENSION_CONFIGS,
            output_format='html5'
        )

        expected_output = (
            '<p>Test Objective C:</p>\n'
            '<pre><code class="c">#import &lt;Foundation/Foundation.h&gt;'
            '\n\nint main (int argc, const char * argv[])\n{\n'
            '        NSAutoreleasePool *pool = [[NSAutoreleasePool alloc] init];\n'
            '        NSLog (@&quot;Test&quot;);\n'
            '        [pool drain];\n'
            '        return 0;\n}\n'
            '</code></pre>')

        self.assertEqual(html, expected_output)

    def test_swift(self):
        text = ('Test Swift:\n'
                '+++ test.swift')

        html = markdown.markdown(
            text,
            extensions=self.MARKDOWN_EXTENSIONS,
            extension_configs=self.EXTENSION_CONFIGS,
            output_format='html5'
        )

        expected_output = (
            '<p>Test Swift:</p>\n'
            '<pre><code class="swift">print(&quot;Test&quot;)\n'
            '</code></pre>')

        self.assertEqual(html, expected_output)

    def test_java(self):
        text = ('Test JAVA:\n'
                '+++ test.java')

        html = markdown.markdown(
            text,
            extensions=self.MARKDOWN_EXTENSIONS,
            extension_configs=self.EXTENSION_CONFIGS,
            output_format='html5'
        )

        expected_output = (
            '<p>Test JAVA:</p>\n'
            '<pre><code class="java">public class TestJava{\n\n'
            '    public static void main(String[] args) {\n'
            '        System.out.println(&quot;Test&quot;);\n'
            '    }\n\n'
            '}\n'
            '</code></pre>')

        self.assertEqual(html, expected_output)

    def test_cpp(self):
        text = ('Test C++:\n'
                '+++ test.cpp')

        html = markdown.markdown(
            text,
            extensions=self.MARKDOWN_EXTENSIONS,
            extension_configs=self.EXTENSION_CONFIGS,
            output_format='html5'
        )

        expected_output = (
            '<p>Test C++:</p>\n'
            '<pre><code class="cpp">#include &lt;iostream&gt;\n\n'
            'using namespace std;\n\n'
            'int main()\n'
            '{\n'
            '\tcout &lt;&lt; &quot;Test&quot; &lt;&lt; endl;\n'
            '\treturn 0;\n'
            '}\n'
            '</code></pre>')
        self.assertEqual(html, expected_output)

    def test_csv(self):
        text = ('Test CSV:\n'
                '+++ test.csv')

        html = markdown.markdown(
            text,
            extensions=self.MARKDOWN_EXTENSIONS,
            extension_configs=self.EXTENSION_CONFIGS,
            output_format='html5'
        )

        expected_output = (
            '<p>Test CSV:\n'
            '<table><tr><th>Test 1</th><th>Test 2</th><th>Test 3</th></tr>'
            '<tr><td>a</td><td>b</td><td>c</td></tr></table></p>')

        self.assertEqual(html, expected_output)


class IncludePreprocessorTest(unittest.TestCase):
    """
    Test the IncludePreprocessor
    """
    TESTS_DIR = os.path.dirname(os.path.abspath(__file__))
    ROOT_DIR = os.path.join(TESTS_DIR, 'test_files')
    CURRENT_DIR = os.path.join(ROOT_DIR, 'deep_assets')
    ASSET_DIR = 'assets'

    def setUp(self):
        md = markdown.Markdown()
        self.preprocessor = IncludePreprocessor(root_directory=self.ROOT_DIR,
                                                current_directory=self.CURRENT_DIR,
                                                asset_directory=self.ASSET_DIR,
                                                extension_map={},
                                                markdown_instance=md)

    def test_find_file_path_with_rollup(self):
        """
        Test that if file is not found in current_dir that we roll up a directory and find there, if it exists.
        """
        self.assertEqual(
            os.path.join(self.TESTS_DIR, 'test_files', 'assets', 'test.cpp'),
            self.preprocessor.find_file_path('test.cpp')
        )

    def test_find_file_path_with_subdirectory(self):
        """
        Test that if filename contains directories, we look there and find the correct file.
        """
        self.assertEqual(
            os.path.join(self.TESTS_DIR, 'test_files', 'assets', 'subdir', 'test.json'),
            self.preprocessor.find_file_path('subdir/test.json')
        )

    def test_find_file_path_in_current_dir(self):
        """
        Test that if file exists in current_dir, we find that one
        """
        self.assertEqual(
            os.path.join(self.TESTS_DIR, 'test_files', 'deep_assets', 'assets', 'test.json'),
            self.preprocessor.find_file_path('test.json')
        )

    def test_build_csv_table(self):
        output = self.preprocessor.build_csv_table(os.path.join(self.ROOT_DIR, self.ASSET_DIR, 'test.csv'))
        expected_output = [
            '<table>',
            '<tr>',
            '<th>', 'Test 1', '</th>',
            '<th>', 'Test 2', '</th>',
            '<th>', 'Test 3', '</th>',
            '</tr>',
            '<tr>',
            '<td>', 'a', '</td>',
            '<td>', 'b', '</td>',
            '<td>', 'c', '</td>',
            '</tr>',
            '</table>'
        ]
        self.assertEqual(expected_output, output)

    def test_handle_csv(self):
        output = self.preprocessor.handle_csv(os.path.join(self.ROOT_DIR, self.ASSET_DIR, 'test.csv'))
        # handle_csv takes output from build_csv_table() and turns it into a symbol for markdown
        expected_output = u'\x02wzxhzdk:0\x03'
        self.assertEqual(expected_output, output)

    def test_handle_code_json(self):
        """
        Test a json file
        """
        output = self.preprocessor.handle_code(os.path.join(self.ROOT_DIR, self.ASSET_DIR, 'test.json'), '.json')
        self.assertEqual(output, [u'``` .json', '{"test": "content"}', u'```'])

    def test_handle_code_javascript(self):
        """
        Test a single line source code file
        """
        output = self.preprocessor.handle_code(os.path.join(self.ROOT_DIR, self.ASSET_DIR, 'test.js'), '.js')
        self.assertEqual(output, [u'``` .js', '''alert('test');''', u'```'])

    def test_handle_code_java_multiline(self):
        """
        Test a source file with multiple lines.
        """
        output = self.preprocessor.handle_code(os.path.join(self.ROOT_DIR, self.ASSET_DIR, 'test.java'), '.java')
        expected_output = [
            u'``` .java',
            u'public class TestJava{',
            u'',
            u'    public static void main(String[] args) {',
            u'        System.out.println("Test");',
            u'    }',
            u'',
            u'}',
            u'```']
        self.assertEqual(output, expected_output)
