# -*- coding:utf-8 -*-
# Copyright (c) 2017, Combine Control Systems AB
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#     * Redistributions of source code must retain the above copyright
#       notice, this list of conditions and the following disclaimer.
#     * Redistributions in binary form must reproduce the above copyright
#       notice, this list of conditions and the following disclaimer in the
#       documentation and/or other materials provided with the distribution.
#     * Neither the name of the Combine Control Systems AB nor the
#       names of its contributors may be used to endorse or promote products
#       derived from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED.
# IN NO EVENT SHALL COMBINE CONTROL SYSTEMS AB BE LIABLE FOR ANY
# DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
from contextlib import contextmanager
import xml.etree.ElementTree as ET
import zipfile
import xlrd


@contextmanager
def open_workbook(filename):
    """Open workbook, on demand - if possible."""
    with xlrd.open_workbook(filename, on_demand=True) as wb:
        yield wb


def is_xlsx(filename):
    """Return True file seems to be an xlsx file, False otherwise."""
    return bool(_get_xlsx_sheetnames(filename))


def is_xls(filename):
    """Return True file seems to be an xls file, False otherwise."""
    # This header is shared between .doc, .xls, .ppt and other OLECF formats.
    OLECF_HEADER = b"\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1"  # noqa

    # At 512 bytes there should be a "subheader" defining what the specific
    # OLECF format of this file. See:
    # http://www.filesignatures.net/index.php?page=search&search=XLS&mode=EXT
    # and
    # http://www.garykessler.net/library/file_sigs.html
    SUBHEADER_OFFSET = 512  # noqa
    XLS_SUBHEADERS = [  # noqa
        b"\x09\x08\x10\x00\x00\x06\x05\x00",
        b"\xfd\xff\xff\xff\x20\x00\x00\x00",
        b"\xfd\xff\xff\xff\x10",
        b"\xfd\xff\xff\xff\x1f",
        b"\xfd\xff\xff\xff\x22",
        b"\xfd\xff\xff\xff\x23",
        b"\xfd\xff\xff\xff\x28",
        b"\xfd\xff\xff\xff\x29"]
    MAX_SUBHEADER_LEN = max([len(subheader) for subheader in XLS_SUBHEADERS])  # noqa

    # Read header and "subheader" from file.
    try:
        with open(filename, 'rb') as f:
            header = f.read(len(OLECF_HEADER))
            f.seek(SUBHEADER_OFFSET)
            subheader = f.read(MAX_SUBHEADER_LEN)
    except:
        return False

    if header == OLECF_HEADER:
        # If a subheader from the approved list exists we accept it as an xls
        # file imidiately...
        for xls_subheader in XLS_SUBHEADERS:
            if subheader.startswith(xls_subheader):
                return True
        # ... otherwise let's see if xlrd thinks that it is an xls file.
        try:
            with open_workbook(filename):
                return True
        except:
            return False
    return False


def get_xl_sheetnames(filename):
    return _get_xlsx_sheetnames(filename) or _get_xls_sheetnames(filename)


def _get_xls_sheetnames(filename):
    try:
        with open_workbook(filename) as wb:
            return wb.sheet_names()
    except:
        return []


def _get_xlsx_sheetnames(filename):
    # Type of main content relationship in xlsx files.
    WB_REL_TYPE = ("http://schemas.openxmlformats.org/officeDocument/"  # noqa
                   "2006/relationships/officeDocument")

    # Namespace used in workbook file in xlsx files.
    WB_NS = "{http://schemas.openxmlformats.org/spreadsheetml/2006/main}"  # noqa

    # Get name of main content (workbook) file from main relations file. Main
    # relations file is located at _rels/.rels.
    try:
        zf = zipfile.ZipFile(filename)
        types = ET.fromstring(zf.read('_rels/.rels'))
    except (zipfile.BadZipfile, KeyError, ET.ParseError):
        # Trying to read a file that isn't in the zip archive gives KeyError
        return []

    # The top level tag is <Types>, containing among other things <Override>
    # tags. One of the <Override> tags will have WB_REL_TYPE as its Type
    # attribute and the path to the main content (workbook) file as its Target
    # attribute.
    for child in types.getchildren():
        if child.get('Type') == WB_REL_TYPE:
            wb_path = child.get('Target')
            break
    else:
        return []

    # Get sheetnames from main content (workbook) file
    try:
        wb_dom = ET.fromstring(zf.read(wb_path))
    except (KeyError, ET.ParseError):
        return []

    # The top level tag is <workbook> which contains among other things a
    # <sheets> tag, which in turn contains a number of <sheet> tags. Each
    # <sheet> tag has a name attribute with the name of that worksheet.
    sheetnames = []
    for sheet in wb_dom.find(WB_NS + 'sheets').getchildren():
        sheetname = sheet.get('name')
        if sheetname:
            sheetnames.append(sheetname)
    return sheetnames
