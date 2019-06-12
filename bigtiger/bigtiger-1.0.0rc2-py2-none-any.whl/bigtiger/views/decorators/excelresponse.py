# -*- coding: utf-8 -*-

'''
Created on 2017-6-22
@author: linkeddt.com
'''

from __future__ import unicode_literals, print_function

import functools

import os
import datetime
import StringIO

from django.conf import settings
from django.http import HttpResponse
from django.utils.encoding import DEFAULT_LOCALE_ENCODING
from django.utils.http import urlquote

import xlrd
import xlwt
from xlutils.copy import copy


def _get_content_style():
    """
    style = xlwt.Style.default_style
    font = xlwt.Font()
    font.colour_index = 0
    font.bold = False
    alignment = xlwt.Alignment()
    alignment.horz = xlwt.Alignment.HORZ_LEFT
    alignment.vert = xlwt.Alignment.VERT_CENTER
    bordesr = xlwt.Borders()
    bordesr.left = xlwt.Borders.THIN
    bordesr.top = xlwt.Borders.THIN
    bordesr.right = xlwt.Borders.THIN
    bordesr.bottom = xlwt.Borders.THIN
    bordesr.left_colour = 0x08
    bordesr.top_colour = 0x08
    bordesr.right_colour = 0x08
    bordesr.bottom_colour = 0x08
    style.borders = bordesr
    style.font = font
    style.alignment = alignment
    """

    style = xlwt.easyxf(
        'font: bold 0, colour_index 0; align: wrap on, vert center, horz general; border: left thin, right thin, top thin, bottom thin')
    return style


def _get_title_style():
    """
    style = xlwt.Style.default_style
    alignment = xlwt.Alignment()
    alignment.horz = xlwt.Alignment.HORZ_CENTER
    alignment.vert = xlwt.Alignment.VERT_CENTER

    font = xlwt.Font()
    font.bold = True
    font.height = 400

    style.alignment = alignment
    style.font = font
    return style
    """

    style = xlwt.easyxf(
        'font: bold 1, colour_index 0, height 350; align: wrap on, vert center, horz center')
    return style


def export_temp_xls(output_file_name, data, template_file_name, start_row=1, start_col=0, sheet_index=0):
    
    # encoding = DEFAULT_LOCALE_ENCODING
    path = os.path.join(settings.XLS_TEMPLATE, template_file_name).replace(
        '\\', '/').replace('//', '/')

    rb = xlrd.open_workbook(path, formatting_info=True)
    wb = copy(rb)
    w_sheet = wb.get_sheet(sheet_index)

    w_sheet.write(0, 0, output_file_name, _get_title_style())
    w_sheet.name = output_file_name

    style = _get_content_style()
    if data:
        for rowx, row in enumerate(data):
            for colx, value in enumerate(row):
                if isinstance(value, datetime.datetime):
                    style.num_format_str = 'yyyy-mm-dd hh:mm:ss'
                elif isinstance(value, datetime.date):
                    style.num_format_str = 'yyyy-mm-dd'
                elif isinstance(value, datetime.time):
                    style.num_format_str = 'hh:mm:ss'
                elif isinstance(value, float):
                    style.num_format_str = '#,##0.00'
                elif isinstance(value, int):
                    style.num_format_str = '0'
                else:
                    style.num_format_str = u'General'
                w_sheet.write(start_row + rowx, start_col + colx, value, style)

    output = StringIO.StringIO()
    wb.save(output)
    output.seek(0)

    filename = '%s_%s.xls' % (
        output_file_name, datetime.datetime.now().strftime('%Y%m%d%H%M%S'))

    response = HttpResponse(output.getvalue())
    response['Content-Type'] = 'application/octet-stream'
    response[
        'Content-Disposition'] = 'attachment;filename="{0}"'.format(urlquote(filename))

    return response


def export_xls(output_file_name, headers, data):
    """
    data = [(item.ADCD, item.ADNM, item.LandArea, item.CultiArea, item.Population, item.Household, item.House, item.CutoffDate,) for item in result]
    data.insert(0, (u'行政区划代码', u'行政区划名称', u'土地面积', u'耕地面积', u'总人口', u'家庭户数', u'房屋数', u'资料截止日期', ))
    return self.ExportXls(u'行政区划基本情况', None,data)
    """

    encoding = DEFAULT_LOCALE_ENCODING

    if headers is not None:
        data.insert(0, headers)

    book = xlwt.Workbook(encoding=encoding)
    sheet = book.add_sheet(output_file_name)
    font0 = xlwt.Style.default_style.font

    font1 = xlwt.Font()
    font1.colour_index = 2
    font1.bold = True
    #font1.height = 300

    bordesr = xlwt.Borders()
    bordesr.left = xlwt.Borders.THIN
    bordesr.top = xlwt.Borders.THIN
    bordesr.right = xlwt.Borders.THIN
    bordesr.bottom = xlwt.Borders.THIN
    bordesr.left_colour = 0x08
    bordesr.top_colour = 0x08
    bordesr.right_colour = 0x08
    bordesr.bottom_colour = 0x08

    style1 = xlwt.Style.default_style
    style1.borders = bordesr

    for rowx, row in enumerate(data):
        for colx, value in enumerate(row):
            if isinstance(value, datetime.datetime):
                style1.num_format_str = 'yyyy-mm-dd hh:mm:ss'
            elif isinstance(value, datetime.date):
                style1.num_format_str = 'yyyy-mm-dd'
            elif isinstance(value, datetime.time):
                style1.num_format_str = 'hh:mm:ss'
            if rowx == 0:
                style1.font = font1
            else:
                style1.font = font0
            sheet.write(rowx, colx, value, style=style1)
            sheet.col(colx).width = 5000

    output = StringIO.StringIO()
    book.save(output)
    output.seek(0)

    response = HttpResponse(content_type='application/vnd.ms-excel')
    response[
        'Content-Disposition'] = 'attachment;filename=%s.xls' % datetime.datetime.now().strftime('%Y%m%d%H%M%S')
    response.write(output.getvalue())
    return response


def excelresponse(output_file_name, template_file_name,
                  start_row=1, start_col=0, sheet_index=0):
    """
    return result excelResponse.
    """

    def _excelresponse(fn):
        @functools.wraps(fn)
        def __excelresponse(*args, **kwargs):
            result = fn(*args, **kwargs)
            return export_temp_xls(output_file_name, result, template_file_name,
                                   start_row, start_col, sheet_index)
        return __excelresponse
    return _excelresponse
