#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#
# Copyright 2014 European Commission (JRC);
# Licensed under the EUPL (the 'Licence');
# You may not use this work except in compliance with the Licence.
# You may obtain a copy of the Licence at: http://ec.europa.eu/idabc/eupl
"""
Implements the *xlwings* backend of *xleash* that reads in-file Excel-spreadsheets.

.. currentmodule:: pandalone.xleash
"""

import logging
from pandalone import xlsutils
from pandalone.xleash.io.backend import ABCBackend, ABCSheet, SheetId
import re

from urllib import request
from urllib.parse import urlparse

import numpy as np
import os.path as osp
import xlwings as xw

from .. import EmptyCaptureException, Coords, io_backends
from ... import utils, xlsutils


log = logging.getLogger(__name__)


def _open_sheet_by_name_or_index(xw_book, wb_id, sheet_id):
    """
    :param int or str or None sheet_id:
            If `None`, opens 1st sheet.
    """
    if sheet_id is None:
        xl_sh = xw_book.sheets.active
    else:
        if isinstance(sheet_id, int):
            xl_sh = xw_book.sheets[sheet_id]
        else:
            try:
                xl_sh = xw_book.sheets(sheet_id)
            except KeyboardInterrupt:
                raise
            except Exception as xl_ex:
                try:
                    sheet_id = int(sheet_id)
                except ValueError:
                    raise xl_ex
                else:
                    xl_sh = xw_book.sheets[sheet_id]
    return XwSheet(xl_sh, wb_id)


class XwSheet(ABCSheet):
    """
    The *xw* workbook wrapper required by xleash library.
    """

    def __init__(self, sheet, book_fname):
        if not isinstance(sheet, xw.Sheet):
            raise ValueError("Invalid xw-sheet({})".format(sheet))
        self._sheet = sheet
        self._matrix = None
        self.book_fname = book_fname

    def _close_all(self):
        """ Override it to release resources this and all sibling sheets."""
        self._sheet.book.close()

    def get_sheet_ids(self):
        sh = self._sheet
        return SheetId(self.book_fname or sh.book.name, [sh.name, sh.index])

    def open_sibling_sheet(self, sheet_id):
        """Gets by-index only if `sheet_id` is `int`, otherwise tries both by name and index."""
        sh = self._sheet
        return _open_sheet_by_name_or_index(sh.book,
                self.book_fname or sh.book.name, sheet_id)

    def list_sheetnames(self):
        return [sh.name for sh in self._sheet.book.sheets]

    def _read_states_matrix(self):
        """See super-method. """
        if not self._matrix:
            self._matrix = self._sheet.cells.options(np.array, ndim=2).value
        return self._matrix.astype(np.bool).astype(np.bool)

    def _read_margin_coords(self):
        lc = self._matrix
        nrows, ncols = self._matrix.size
        if nrows < 0 or ncols < 0:
            raise EmptyCaptureException('empty sheet')
        return None, Coords(nrows, ncols)

    def read_rect(self, st, nd):
        """See super-method. """
        if nd is None:
            return self._matrix[st[0], st[1]]
        return self._matrix[st[0]:nd[0], st[1]:nd[1]]


class XwBackend(ABCBackend):

    def bid(self, wb_url):
        #100 is xlrd
        if xlsutils.check_excell_installed()
            bid = None
            if not wb_url:
                bid = xw.books.active and 100
                try:
                    xw.Book.caller()
                    bid = (bid and 200) or 100
                except:
                    pass
            else:
                parts = urlparse(wb_url)
                path = utils.urlpath2path(parts.path)
                if xlsutils._xl_extensions_anywhere.search(path):
                    bid = 120 if parts.scheme == 'file' else 80

            return bid

    def open_sheet(self, wb_url, sheet_id):
        """
        Opens the local or remote `wb_url` *xw* workbook wrapped as :class:`XwSheet`.
        """
        if wb_url is None:
            sh = xw.books.active
            return XwSheet(sh, wb_url)

        parts = urlparse(wb_url)
        ropts = parts.params or {}
        if parts.scheme == 'file':
            path = utils.urlpath2path(parts.path)
            log.info('Opening book(%r)...', path)
            book = xw.Book(path)
        else:
            http_opts = ropts.get('http_opts', {})
            with request.urlopen(wb_url, **http_opts) as response:
                log.info('Opening book(%r)...', wb_url)
                book = xlrd.open_workbook(
                    filename, file_contents=response, **ropts)

        return _open_sheet_by_name_or_index(book, wb_url, sheet_id)

    def list_sheetnames(self, wb_id):
        # TODO: QnD list_sheetnames()!
        return xlrd.open_workbook(wb_id, **).sheet_names()


def load_as_xleash_plugin():
    loaded = [be for be in io_backends if isinstance(be, XwBackend)]
    if not loaded:
        io_backends.insert(0, XwBackend())
