# coding: utf-8
# -----------------------------------------------------------------------------------
# <copyright company="Aspose Pty Ltd" file="TestFile.py">
#   Copyright (c) 2019 Aspose Pty Ltd
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

from groupdocs_signature_cloud import FileInfo
""" 
    Describes file for tests.
"""
class TestFile(object):

    @classmethod
    def pdf_one_page(cls):
        f = TestFile()
        f.file_name = "01_pages.pdf"
        f.folder = "Pdf\\"
        return f

    @classmethod
    def image_jpg(cls):
        f = TestFile()
        f.file_name = "01_pages.jpg"
        f.folder = "Images\\"
        return f  

    @classmethod
    def presentation_pptx(cls):
        f = TestFile()
        f.file_name = "01_pages.pptx"
        f.folder = "Presentations\\"
        return f           

    @classmethod
    def spreadsheet_xlsx(cls):
        f = TestFile()
        f.file_name = "01_pages.xlsx"
        f.folder = "Spreadsheets\\"
        return f  

    @classmethod
    def word_docx(cls):
        f = TestFile()
        f.file_name = "01_pages.docx"
        f.folder = "WordProcessing\\"
        return f  

    @classmethod
    def image_signed(cls):
        f = TestFile()
        f.file_name = "SignedForVerificationAll.png"
        f.folder = "Signed\\"
        f.size = 27533
        return f

    @classmethod
    def pdf_signed(cls):
        f = TestFile()
        f.file_name = "SignedForVerificationAll.pdf"
        f.folder = "Signed\\"
        f.size = 164060
        return f

    @classmethod
    def presentation_signed(cls):
        f = TestFile()
        f.file_name = "SignedForVerificationAll.pptx"
        f.folder = "Signed\\"
        f.size = 43205
        return f

    @classmethod
    def spreadsheet_signed(cls):
        f = TestFile()
        f.file_name = "SignedForVerificationAll.xlsx"
        f.folder = "Signed\\"
        f.size = 318157
        return f

    @classmethod
    def wordprocessing_signed(cls):
        f = TestFile()
        f.file_name = "SignedForVerificationAll.docx"
        f.folder = "Signed\\"
        f.size = 1358290
        return f

    @classmethod
    def additional_signature01(cls):
        f = TestFile()
        f.file_name = "signature_01.jpg"
        f.folder = "Additional\\"        
        return f

    @classmethod
    def additional_pfx(cls):
        f = TestFile()
        f.file_name = "SherlockHolmes.pfx"
        f.folder = "Additional\\"        
        return f   

    @classmethod
    def image_sign(cls):
        f = TestFile()
        f.file_name = "JohnSmithSign.png"
        f.folder = "Additional\\"        
        return f   

    @classmethod
    def get_test_files(cls):
        return [
            cls.pdf_one_page(),
            cls.image_jpg(),
            cls.presentation_pptx(),
            cls.spreadsheet_xlsx(),
            cls.word_docx(),
            cls.image_signed(),
            cls.pdf_signed(),
            cls.presentation_signed(),
            cls.spreadsheet_signed(),
            cls.wordprocessing_signed(),
            cls.additional_signature01(),
            cls.additional_pfx(),
            cls.image_sign()
        ]

    def FilePath(self):
        return self.folder + self.file_name

    def ToFileInfo(self):
        f = FileInfo()
        f.file_path = self.folder + self.file_name
        if hasattr(self, 'password'):
            f.password = self.password
        return f        