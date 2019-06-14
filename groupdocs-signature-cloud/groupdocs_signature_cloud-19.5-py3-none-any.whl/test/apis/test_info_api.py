# coding: utf-8

# -----------------------------------------------------------------------------------
# <copyright company="Aspose Pty Ltd">
#   Copyright (c) 2003-2019 Aspose Pty Ltd
# </copyright>
# <summary>
#   Permission is hereby granted, free of charge, to any person obtaining a copy
#  of this software and associated documentation files (the "Software"), to deal
#  in the Software without restriction, including without limitation the rights
#  to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#  copies of the Software, and to permit persons to whom the Software is
#  furnished to do so, subject to the following conditions:
#
#  The above copyright notice and this permission notice shall be included in all
#  copies or substantial portions of the Software.
#
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#  FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#  AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#  LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#  OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
#  SOFTWARE.
# </summary>
# -----------------------------------------------------------------------------------

from __future__ import absolute_import

import unittest
import os

from groupdocs_signature_cloud import *
from test.test_context import TestContext
from test.test_file import TestFile

class TestInfoApi(TestContext):

    def test_get_supported_file_formats(self):
        response = self.info_api.get_supported_file_formats()
        self.assertGreater(len(response.formats), 0)
        for format in response.formats:
            self.assertFalse(format.file_format == "")
            self.assertFalse(format.extension == "")        

    def test_get_supported_barcodes(self):
        response = self.info_api.get_supported_barcodes()
        self.assertGreater(len(response.barcode_types), 0)
        for format in response.barcode_types:
            self.assertFalse(format.name == "")

    def test_get_supported_qrcodes(self):
        response = self.info_api.get_supported_qr_codes()
        self.assertGreater(len(response.qr_code_types), 0)
        for format in response.qr_code_types:
            self.assertFalse(format.name == "")

    def test_document_info(self):
        test_file = TestFile.pdf_one_page()
        settings = InfoSettings()
        settings.file_info = test_file.ToFileInfo()
        response = self.info_api.get_info(GetInfoRequest(settings))
        self.assertEqual(response.size, 55321)
        self.assertEqual(response.extension, "pdf")
        self.assertEqual(response.file_format, "Pdf")
        self.assertEqual(response.max_page_height, 792)
        self.assertEqual(response.width_for_max_height, 612)
        self.assertEqual(response.pages_count, 1)
        self.assertEqual(response.file_info.file_path, settings.file_info.file_path)

if __name__ == '__main__':
    unittest.main()
