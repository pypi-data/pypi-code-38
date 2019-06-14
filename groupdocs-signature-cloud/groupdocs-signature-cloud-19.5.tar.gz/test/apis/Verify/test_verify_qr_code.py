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

class TestVerifyQRcode(TestContext):

    def test_verify_qr_code_image(self):
        test_file = TestFile.image_signed()
        settings = self.populate_options('Image', test_file)            
        response = self.sign_api.verify_signatures(VerifySignaturesRequest(settings))
        self.check_response(response, test_file)

    def test_verify_qr_code_pdf(self):
        test_file = TestFile.pdf_signed()
        settings = self.populate_options('Pdf', test_file)            
        response = self.sign_api.verify_signatures(VerifySignaturesRequest(settings))
        self.check_response(response, test_file)

    def test_verify_qr_code_presentation(self):
        test_file = TestFile.presentation_signed()
        settings = self.populate_options('Presentation', test_file)            
        response = self.sign_api.verify_signatures(VerifySignaturesRequest(settings))
        self.check_response(response, test_file)

    def test_verify_qr_code_spreadsheet(self):
        test_file = TestFile.spreadsheet_signed()
        settings = self.populate_options('Spreadsheet', test_file)            
        response = self.sign_api.verify_signatures(VerifySignaturesRequest(settings))
        self.check_response(response, test_file)

    def test_verify_qr_code_wordprocessing(self):
        test_file = TestFile.wordprocessing_signed()
        settings = self.populate_options('WordProcessing', test_file)            
        response = self.sign_api.verify_signatures(VerifySignaturesRequest(settings))
        self.check_response(response, test_file)                       

    @staticmethod
    def populate_options(documentType, testFile):
        opts = VerifyQRCodeOptions()
        opts.document_type = documentType
        opts.signature_type = 'QRCode'
        opts.text = 'John Smith'
        opts.qr_code_type = 'Aztec'
        opts.match_type = 'Contains'

        opts.page = 1
        opts.all_pages = True
        ps = PagesSetup()
        ps.even_pages = False
        ps.first_page = True
        ps.last_page = False
        ps.odd_pages = False
        ps.page_numbers = [1]
        opts.pages_setup = ps

        settings = VerifySettings()
        settings.file_info = testFile.ToFileInfo()
        settings.options = [opts]
        return settings
    
    def check_response(self, response, test_file):
        self.assertTrue(response)
        self.assertTrue(response.file_info)
        self.assertEqual(response.file_info.file_path, test_file.FilePath())     


if __name__ == '__main__':
    unittest.main()
